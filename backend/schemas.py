from pydantic import BaseModel

class VideoRequest(BaseModel):
    url: str

class VideoResponse(BaseModel):
    message: str

class SessionRequest(BaseModel):
    url: str

class SessionResponse(BaseModel):
    video_id: str
    source: str

class QuestionRequest(BaseModel):
    question: str
    source: str

class QuestionResponse(BaseModel):
    answer: str