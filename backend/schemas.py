from pydantic import BaseModel

class VideoRequest(BaseModel):
    url: str

class LLMRequest(BaseModel):
    prompt: str

class LLMResponse(BaseModel):
    answer: str