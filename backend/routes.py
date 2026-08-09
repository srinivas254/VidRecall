from fastapi import APIRouter
from schemas import (
    VideoRequest,
    LLMRequest,
    LLMResponse
)
from services import (
    validate_youtube_url,
    extract_video_id,
    get_transcript,
    should_use_rag,
    get_chunks,
    generate_embeddings
)

router = APIRouter()

@router.post("/video-process")
async def process_the_video(request: VideoRequest) -> int:

    validate_youtube_url(request.url)

    video_id = extract_video_id(request.url)

    text_data = get_transcript(video_id)

    ragRequirement = should_use_rag(text_data)

    if ragRequirement:
        chunks = get_chunks(text_data)

        embeddings = generate_embeddings(chunks)
        
        return 1
    else:
        return 0

