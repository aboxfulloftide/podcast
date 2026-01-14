from fastapi import APIRouter
from app.api.endpoints import users, podcasts, subscriptions, ad_removal

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(podcasts.router, prefix="/podcasts", tags=["podcasts"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(ad_removal.router, prefix="/ad-removal", tags=["ad-removal"])
