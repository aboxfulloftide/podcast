import uuid
from mysql.connector.connection import MySQLConnection
from app.schemas.subscription import SubscriptionCreate

def create_subscription(db: MySQLConnection, subscription: SubscriptionCreate, user_id: int, podcast_id: int):
    """
    Create a new subscription in the database.
    """
    cursor = db.cursor()
    custom_feed_slug = str(uuid.uuid4())
    query = "INSERT INTO subscriptions (user_id, podcast_id, custom_feed_slug) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, podcast_id, custom_feed_slug))
    db.commit()
    subscription_id = cursor.lastrowid
    cursor.close()
    return {"id": subscription_id, "user_id": user_id, "podcast_id": podcast_id, "custom_feed_slug": custom_feed_slug}

def get_subscription_by_user_and_podcast(db: MySQLConnection, user_id: int, podcast_id: int):
    """
    Get a subscription from the database by user_id and podcast_id.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, user_id, podcast_id, custom_feed_slug FROM subscriptions WHERE user_id = %s AND podcast_id = %s"
    cursor.execute(query, (user_id, podcast_id))
    subscription = cursor.fetchone()
    cursor.close()
    return subscription

def get_subscription_by_id(db: MySQLConnection, subscription_id: int):
    """
    Get a single subscription from the database by its ID.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, user_id, podcast_id, custom_feed_slug, episode_retention_count FROM subscriptions WHERE id = %s"
    cursor.execute(query, (subscription_id,))
    subscription = cursor.fetchone()
    cursor.close()
    return subscription

def get_subscriptions_by_user_id(db: MySQLConnection, user_id: int):
    """
    Get all subscriptions for a user, along with podcast details.
    """
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT 
            s.id AS subscription_id, 
            s.custom_feed_slug, 
            p.id AS podcast_id, 
            p.title AS podcast_title, 
            p.feed_url AS podcast_feed_url,
            p.image_url AS podcast_image_url
        FROM subscriptions s
        JOIN podcasts p ON s.podcast_id = p.id
        WHERE s.user_id = %s
    """
    cursor.execute(query, (user_id,))
    subscriptions = cursor.fetchall()
    cursor.close()
    return subscriptions

def get_all_subscriptions_with_podcast_details(db: MySQLConnection):
    """
    Get all subscriptions from the database, along with podcast details.
    """
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT 
            s.id AS subscription_id, 
            s.user_id,
            s.podcast_id,
            s.custom_feed_slug,
            s.episode_retention_count,
            p.title AS podcast_title, 
            p.feed_url AS podcast_feed_url,
            p.image_url AS podcast_image_url
        FROM subscriptions s
        JOIN podcasts p ON s.podcast_id = p.id
    """
    cursor.execute(query)
    subscriptions = cursor.fetchall()
    cursor.close()
    return subscriptions
