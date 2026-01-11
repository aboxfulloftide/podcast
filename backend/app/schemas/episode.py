from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class Episode(BaseModel):
    guid: str
    title: str
    original_audio_url: HttpUrl
    publication_date: datetime
    
    class Config:
        orm_mode = True
