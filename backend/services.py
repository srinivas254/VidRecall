from config import (
    client,
    qdrantClient,
    EMBEDDING_MODEL,
    LLM_MODEL,
    DIRECT_LLM_THRESHOLD,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
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
    create_collection_if_not_exists
)

import re
import uuid
import numpy as np 
import torch
import torch.nn.functional as F
from qdrant_client.models import (
    PointStruct
) 
from exceptions import (
    InvalidURLException,
    InvalidVideoIDException,
    VideoUnavailableException,
    TranscriptDisabledException
)

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
            id = str(uuid.uuid4()),
            vector = embedding,
            payload = {
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
