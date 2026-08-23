from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from exceptions import (
    InvalidURLException,
    InvalidVideoIDException,
    VideoUnavailableException,
    TranscriptDisabledException,
    QdrantCollectionNotFoundException,
    NoChunksFoundException,
    VideoNotProcessedException
)
from exception_handlers import (
    invalid_url_exception_handler,
    invalid_video_id_exception_handler,
    video_unavailable_exception_handler,
    transcript_disabled_exception_handler,
    internal_server_exception_handler,
    qdrant_collection_not_found_exception_handler,
    no_chunks_found_exception_handler,
    video_not_processed_exception_handler
)

from database import Base, engine
from pgsql_models import SmallVideo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

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
    QdrantCollectionNotFoundException,
    qdrant_collection_not_found_exception_handler
)

app.add_exception_handler(
    NoChunksFoundException,
    no_chunks_found_exception_handler
)

app.add_exception_handler(
    VideoNotProcessedException,
    video_not_processed_exception_handler
)

app.add_exception_handler(
    Exception,
    internal_server_exception_handler
)

app.include_router(router)