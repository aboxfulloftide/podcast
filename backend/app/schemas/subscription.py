from pydantic import BaseModel, HttpUrl

class SubscriptionBase(BaseModel):
    podcast_id: int
    user_id: int

class SubscriptionCreate(SubscriptionBase):
    feed_url: HttpUrl # Change to HttpUrl for validation
    title: str
    image_url: HttpUrl # Change to HttpUrl for validation

class Subscription(SubscriptionBase):
    id: int
    custom_feed_slug: str

    class Config:
        orm_mode = True

class SubscriptionWithPodcastDetails(BaseModel):
    subscription_id: int
    custom_feed_slug: str
    podcast_id: int
    podcast_title: str
    podcast_feed_url: HttpUrl
    podcast_image_url: HttpUrl

    class Config:
        orm_mode = True
