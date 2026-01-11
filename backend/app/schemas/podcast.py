from pydantic import BaseModel, HttpUrl
from typing import List

class PodcastFeed(BaseModel):
    id: int
    title: str
    url: HttpUrl
    image: HttpUrl

class PodcastSearchResult(BaseModel):
    feeds: List[PodcastFeed]
    count: int
    description: str
