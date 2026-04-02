from pydantic import BaseModel
 
 
class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str
 
 
class ProcessedPost(BaseModel):
    id: int
    userId: int
    title: str
    word_count: int
    title_upper: str