from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection
from app.api import deps
from app.crud import crud_podcast, crud_subscription
from app.schemas import subscription as subscription_schema
from app.schemas import user as user_schema
from typing import List

router = APIRouter()

@router.post("/", response_model=subscription_schema.Subscription)
def subscribe_to_podcast(
    *,
    db: MySQLConnection = Depends(deps.get_db),
    current_user: user_schema.User = Depends(deps.get_current_user),
    podcast_feed_url: str,
    podcast_title: str,
    podcast_image_url: str,
):
    """
    Subscribe to a podcast.
    """
    db_gen = next(db) # Get the actual connection object from the generator
    
    # Check if podcast already exists in our database
    podcast = crud_podcast.get_podcast_by_feed_url(db_gen, feed_url=podcast_feed_url)
    if not podcast:
        podcast = crud_podcast.create_podcast(db_gen, title=podcast_title, feed_url=podcast_feed_url, image_url=podcast_image_url)

    # Check if user is already subscribed to this podcast
    existing_subscription = crud_subscription.get_subscription_by_user_and_podcast(
        db_gen, user_id=current_user['id'], podcast_id=podcast['id']
    )
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already subscribed to this podcast",
        )

    # Create the subscription
    subscription_in = subscription_schema.SubscriptionCreate(
        podcast_id=podcast['id'],
        user_id=current_user['id'],
        feed_url=podcast_feed_url, # Not directly used for creation, but for schema validation
        title=podcast_title,
        image_url=podcast_image_url
    )
    subscription = crud_subscription.create_subscription(
        db_gen, subscription=subscription_in, user_id=current_user['id'], podcast_id=podcast['id']
    )
    return subscription

@router.get("/my", response_model=List[subscription_schema.SubscriptionWithPodcastDetails])
def read_my_subscriptions(
    db: MySQLConnection = Depends(deps.get_db),
    current_user: user_schema.User = Depends(deps.get_current_user),
):
    """
    Retrieve all subscriptions for the current user.
    """
    db_gen = next(db)
    subscriptions = crud_subscription.get_subscriptions_by_user_id(db_gen, user_id=current_user['id'])
    return subscriptions
