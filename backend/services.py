from config import (
    qdrantClient,
    EMBEDDING_MODEL,
    DIRECT_LLM_THRESHOLD,
    SIMILARITY_THRESHOLD,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SPARSE_RETRIEVAL_MODEL,
    SPARSE_VECTOR_NAME,
    TOP_K)

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    VideoUnavailable,
    NoTranscriptFound,
    TranscriptsDisabled
)

from token_embedding_config import (
    tokenizer,
    model
)

from qdrant_services import (
    create_collection_if_not_exists,
    get_existing_collection
)

from rrf_service import (
    reciprocal_rank_fusion
)

import re
import uuid
import numpy as np 
import torch
import torch.nn.functional as F
from fastapi import Depends
from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
) 
from qdrant_client import models

from exceptions import (
    InvalidURLException,
    InvalidVideoIDException,
    VideoUnavailableException,
    TranscriptDisabledException,
    NoChunksFoundException,
    VideoNotProcessedException
)

from sqlalchemy.orm import Session 
from pgsql_models import SmallVideo
from database import get_db

#regex pattern to validate the url
url_pattern = (
    r"^https:\/\/(?:www\.)?"
    r"(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)"
)

#validate the url
def validate_youtube_url(url: str) -> None:
    if re.match(url_pattern, url) is None:
        raise InvalidURLException("Invalid Youtube URL")

#regex pattern to extract the ID
patterns = [
        r"(?:v=|shorts/|youtu\.be/)([0-9A-Za-z_-]{11})"
    ]

#Extract youtube video ID
def extract_video_id(url: str) -> str:
    for pattern in patterns:
        match = re.search(pattern,url)

        if match:
            return match.group(1)
        
    raise InvalidVideoIDException("Invalid Video ID")

#extract the transcript of the video from the transcript api
def get_transcript(video_id: str) -> str:
    ytt_api = YouTubeTranscriptApi()

    try:
        #1st preference English transcript
        transcript = ytt_api.fetch(video_id, languages=["en"])
    
    except NoTranscriptFound:
         # English transcript not found, look for another transcript
        transcript_list = ytt_api.list(video_id)

        #found the original language transcript
        transcript_language = next(iter(transcript_list),None)

        if transcript_language is None:
            raise TranscriptDisabledException("Transcripts are disabled for this video.")

        transcript = transcript_language.fetch()

        #return the translated transcript
        return " ".join(segment.text for segment in transcript)

    except TranscriptsDisabled:
        raise TranscriptDisabledException("Transcripts are disabled for this video.")

    except VideoUnavailable:
        raise VideoUnavailableException("Video is unavailable.")
    
    #return the original english transcript
    return " ".join(segment.text for segment in transcript)

#check if RAG is neccessary
def should_use_rag(transcript: str) -> bool:
    tokens = tokenizer.encode(transcript)
    print(f"tokens: {len(tokens)}")
    return len(tokens) > DIRECT_LLM_THRESHOLD



#chunking stage
def get_chunks(transcript: str) -> list[str]:

    #convert the transcript to tokens IDs
    tokens = tokenizer.encode(
        transcript,
        add_special_tokens = False
    )

    stride = CHUNK_SIZE - CHUNK_OVERLAP

    chunks = []

    #chunk them on the basis of token IDs
    for i in range(0,len(tokens),stride):

        chunked_tokens = tokens[i:i+CHUNK_SIZE]

        if not chunked_tokens:
            break

        #convert them back to text
        chunk_text = tokenizer.decode(chunked_tokens,
        skip_special_tokens = True)

        chunks.append(chunk_text)

        if i + CHUNK_SIZE >= len(tokens):
            break
    
    return chunks


#generate embeddings
def generate_embeddings(chunks: list[str]) -> list[list[float]]:

    embeddings = []

    for chunk in chunks:

        #for each chunk this will return input token IDs and attention masks as tensors
        inputs = tokenizer(
            chunk,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        #since this is inference no need of gradient descent
        #the token IDs and attention masks are passed as inputs after checking the 
        # padding 0s attention masks are discarded and then we lookup the tensors file and
        # create a learned embedding for all the tokens in the chunk now each token have semantic meaning
        # but no context of other tokens now we pass this to a transformer blocks in that
        # we have multi head self attention which contextualizes each token w.r.t other input tokens
        # then we add the old + new tokens to make a residual connection and then normalize the layer
        # then we pass this into a feed forward neural network with n hidden layers
        # then we pass this through an activation function later again pass this through a FFNN with n hidden layers
        # we then add the old + new vectors and normalize them
        # we get the outputs with it's last hidden state(hidden reps) for all the tokens
        with torch.no_grad():
            outputs = model(**inputs)

        hidden_state = outputs.last_hidden_state

        #pool that 350 * 384 dim vector into a single 384 dim vector
        mean_embedding = hidden_state.mean(dim=1)

        #normalize that 384 dim vector until it's length is 1 unit
        final_embedding = F.normalize(
            mean_embedding,
            p=2,
            dim=1
        )

        #from [1,384] to [384] tensor to 384 elements list
        embeddings.append(
            final_embedding.squeeze().tolist()
        )

    return embeddings


#store all the embeddings into qdrant
def store_embeddings(
    video_id: str,
    chunks: list[str],
    embeddings: list[list[float]]) -> int:

    points = []

    #convert embeddings into points
    for index, embedding in enumerate(embeddings):

        point = PointStruct(
            id=str(uuid.uuid4()),

            vector={
                # Existing dense embedding
                "": embedding,

                # BM25 sparse embedding
                SPARSE_VECTOR_NAME: models.Document(
                    text=chunks[index],
                    model=SPARSE_RETRIEVAL_MODEL
                )
            },

            payload={
                "video_id": video_id,
                "chunk_index": index,
                "chunk_text": chunks[index]
            }
        )

        points.append(point)

    #check if collection exists
    my_collection = create_collection_if_not_exists()

    #insert it
    qdrantClient.upsert(
        collection_name = my_collection,
        points = points
    )

    return len(points)


#check if the video is processed first and return the video id
def check_video_processed(video_id: str, db: Session) -> tuple[str,str]:
    
    #first check the postgres
    video = db.get(SmallVideo, video_id)

    if video:
        return video.video_id, "postgres"

    #if not in postgresql check in qdrant
    my_collection = get_existing_collection()

    points, _ = qdrantClient.scroll(
        collection_name = my_collection,
        scroll_filter = Filter(
            must = [
                FieldCondition(
                    key="video_id",
                    match=MatchValue(
                        value=video_id
                    )
                )
            ]
        ),
        limit = 1
    )

    if points:
        video_id = points[0].payload["video_id"]
        return video_id, "qdrant"

    raise VideoNotProcessedException(
        f"Video {video_id} has not been processed yet"
        )


#we pass the question query and return it's embedding
def generate_query_embeddings(question: str) -> list[float]:

    #return tokens with their IDs
    inputs = tokenizer(
        question,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    #the transformer inference flow begins till the last hidden state
    with torch.no_grad():
        outputs = model(**inputs)

    #return the vector with size [n tokens,384]
    hidden_state = outputs.last_hidden_state

    #converts to [1,384]
    mean_embedding = hidden_state.mean(dim=1)

    #normalize that 384 dim vector until it's length is 1 unit
    final_embedding = F.normalize(
        mean_embedding,
        p=2,
        dim=1
    )

    #from [1,384] tensor to [384] list
    return final_embedding.squeeze().tolist()

#retrieve the relevant video's chunks
def retrieve_chunks(video_id: str, query: str, query_embedding: list[float]) -> list[str]:

    my_collection = get_existing_collection()

    #add a filter to search based on video id
    video_filter = Filter(
        must=[
            FieldCondition(
                key="video_id",
                match=MatchValue(value=video_id)
            )
        ]
    )

    #do a similarity vector search with metadata filtering and retrieve top k chunks
    vector_results = qdrantClient.query_points(
        collection_name=my_collection,
        query=query_embedding,
        limit=TOP_K,
        query_filter=video_filter
    )

    if not vector_results.points:
        raise NoChunksFoundException("No chunks found for this video")

    #from that queryResponse we filter out only the chunks with the point object 
    #  and return it if it's similarity
    #score is greater than cosine 45
    dense_chunks = [point
                    for point in vector_results.points
                    if point.score >= SIMILARITY_THRESHOLD]
    
    # Qdrant's BM25 model converts the question into its
    # sparse representation internally and searches against
    # the sparse vectors stored during ingestion.
    keyword_results = qdrantClient.query_points(
        collection_name=my_collection,

        query=models.Document(
            text=query,
            model=SPARSE_RETRIEVAL_MODEL
        ),

        # Tell Qdrant which sparse vector to search.
        using=SPARSE_VECTOR_NAME,

        # Search only this video's chunks.
        query_filter=video_filter,

        # Get the best TOP_K keyword matches.
        limit=TOP_K
    )

    keyword_chunks = keyword_results.points
        

    if not dense_chunks and not keyword_chunks:
        raise NoChunksFoundException(
            "No relevant chunks found for this video"
        )

    #combine dense + sparse chunk results
    combined_results = dense_chunks + keyword_chunks

    #deduplicate chunks (collect only the unique chunk point objects)
    unique_chunks = {}

    for point in combined_results:

        chunk_index = point.payload["chunk_index"]

        # Only add the chunk the first time we encounter it.
        if chunk_index not in unique_chunks:
            unique_chunks[chunk_index] = point

    # Store the rank of each unique chunk
    # in both retrieval methods.
    chunk_ranks = {}

    # Dense ranking
    for rank, point in enumerate(dense_chunks, start=1):

        chunk_index = point.payload["chunk_index"]

        if chunk_index not in chunk_ranks:
            chunk_ranks[chunk_index] = {
                "dense_rank": None,
                "sparse_rank": None
            }

        chunk_ranks[chunk_index]["dense_rank"] = rank


    # Sparse / BM25 ranking
    for rank, point in enumerate(keyword_chunks, start=1):

        chunk_index = point.payload["chunk_index"]

        if chunk_index not in chunk_ranks:
            chunk_ranks[chunk_index] = {
                "dense_rank": None,
                "sparse_rank": None
            }

        chunk_ranks[chunk_index]["sparse_rank"] = rank

    #we will rank the chunks based on RRF score
    ranked_chunks = reciprocal_rank_fusion(chunk_ranks)

    #convert the ranked chunks into ranked points
    ranked_points = [
    unique_chunks[chunk_index]
    for chunk_index in ranked_chunks
    ]

    #get the final top k chunk text 
    final_chunks = [
    point.payload["chunk_text"]
    for point in ranked_points[:TOP_K]
    ]
    
    return final_chunks


#retrieve the context from pgsql for generation
def get_video_content(video_id: str, db: Session) -> str:
    video = db.get(SmallVideo, video_id)

    return video.content
