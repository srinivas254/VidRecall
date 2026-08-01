from config import client,EMBEDDING_MODEL,LLM_MODEL
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    VideoUnavailable,
    NoTranscriptFound,
    TranscriptsDisabled
)
import re
import numpy as np 
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
        
