from pydantic import BaseModel

class VideoRequest(BaseModel):
    url: str

class VideoResponse(BaseModel):
    message: str
    video_id: str

class LLMRequest(BaseModel):
    prompt: str

class LLMResponse(BaseModel):
    answer: str