from pydantic import BaseModel

class VideoRequest(BaseModel):
    url: str

class VideoResponse(BaseModel):
    message: str
    video_id: str

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str