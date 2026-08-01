from fastapi import FastAPI 
from routes import router
from exceptions import (
    InvalidURLException,
    InvalidVideoIDException,
    VideoUnavailableException,
    TranscriptDisabledException
)
from exception_handlers import (
    invalid_url_exception_handler,
    invalid_video_id_exception_handler,
    video_unavailable_exception_handler,
    transcript_disabled_exception_handler,
    internal_server_exception_handler
)

app = FastAPI()

app.add_exception_handler(
    InvalidURLException,
    invalid_url_exception_handler
)

app.add_exception_handler(
    InvalidVideoIDException,
    invalid_video_id_exception_handler
)

app.add_exception_handler(
    VideoUnavailableException,
    video_unavailable_exception_handler
)

app.add_exception_handler(
    TranscriptDisabledException,
    transcript_disabled_exception_handler
)

app.add_exception_handler(
    Exception,
    internal_server_exception_handler
)

app.include_router(router)