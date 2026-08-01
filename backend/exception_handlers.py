from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions import (
    InvalidURLException,
    InvalidVideoIDException,
    VideoUnavailableException,
    TranscriptDisabledException
)

async def invalid_url_exception_handler(
    request: Request,
    exc: InvalidURLException
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc)
        }
    )

async def invalid_video_id_exception_handler(
    request: Request,
    exc: InvalidVideoIDException
):
    return JSONResponse(
        status_code=400,
        content={
            "detail":str(exc)
        }
    )

async def video_unavailable_exception_handler(
    request: Request,
    exc: VideoUnavailableException
):
    return JSONResponse(
        status_code=404,
        content={
            "detail":str(exc)
        }
    )

async def transcript_disabled_exception_handler(
    request: Request,
    exc: TranscriptDisabledException
):
    return JSONResponse(
        status_code=422,
        content={
            "detail":str(exc)
        }
    )

async def internal_server_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error"
        }
    )
