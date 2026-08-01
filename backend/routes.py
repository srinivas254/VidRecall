from fastapi import APIRouter
from schemas import (
    VideoRequest
)
from services import (
    validate_youtube_url,
    extract_video_id,
    get_transcript
)

router = APIRouter()

@router.post("/video-process")
async def process_the_video(request: VideoRequest) -> str:

    validate_youtube_url(request.url)

    video_id = extract_video_id(request.url)

    text_data = get_transcript(video_id)

    return text_data
