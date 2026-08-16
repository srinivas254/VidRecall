from fastapi import APIRouter, Depends
from schemas import (
    VideoRequest,
    VideoResponse,
    QuestionRequest,
    QuestionResponse
)
from services import (
    validate_youtube_url,
    extract_video_id,
    get_transcript,
    should_use_rag,
    get_chunks,
    generate_embeddings,
    store_embeddings,
    check_video_processed,
    generate_query_embeddings,
    retrieve_chunks
)

from llm_service import (
    llm_call
)

from no_rag_service import (
    store_small_video
)
from database import (
    get_db
)
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/video-process", response_model=VideoResponse)
async def process_the_video(request: VideoRequest, db: Session = Depends(get_db)):

    validate_youtube_url(request.url)

    video_id = extract_video_id(request.url)
 
    text_data = get_transcript(video_id)

    ragRequirement = should_use_rag(text_data)

    if ragRequirement:
        chunks = get_chunks(text_data)

        embeddings = generate_embeddings(chunks)

        total_points = store_embeddings(video_id, chunks, embeddings)

        message = f"Video processed with {total_points} points"
        
        return VideoResponse(
            message = message, 
            video_id = video_id)
    else:

        video = store_small_video(db, video_id, text_data)

        return VideoResponse(
            message = f"Video context persisted in the disk storage",
            video_id = video.video_id)


@router.post("/chat/{video_id}", response_model=QuestionResponse)
async def retrieve_answer(request: QuestionRequest, video_info = Depends(check_video_processed)):

    video_id, content, source = video_info

    if source == "postgres":
        context = content
    
    else:
        
        query_embedding = generate_query_embeddings(request.question)

        relevant_chunks = retrieve_chunks(video_id, query_embedding)

        context = "\n\n".join(relevant_chunks)

    answer = llm_call(context, request.question)

    return QuestionResponse(
        answer = answer
    )

