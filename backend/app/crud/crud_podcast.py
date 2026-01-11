from mysql.connector.connection import MySQLConnection

def get_podcast_by_feed_url(db: MySQLConnection, feed_url: str):
    """
    Get a podcast from the database by feed_url.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, title, feed_url, image_url FROM podcasts WHERE feed_url = %s"
    cursor.execute(query, (feed_url,))
    podcast = cursor.fetchone()
    cursor.close()
    return podcast

def get_podcast_by_id(db: MySQLConnection, podcast_id: int):
    """
    Get a podcast from the database by ID.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, title, feed_url, image_url FROM podcasts WHERE id = %s"
    cursor.execute(query, (podcast_id,))
    podcast = cursor.fetchone()
    cursor.close()
    return podcast


def create_podcast(db: MySQLConnection, title: str, feed_url: str, image_url: str):
    """
    Create a new podcast in the database.
    """
    cursor = db.cursor()
    query = "INSERT INTO podcasts (title, feed_url, image_url) VALUES (%s, %s, %s)"
    cursor.execute(query, (title, feed_url, image_url))
    db.commit()
    podcast_id = cursor.lastrowid
    cursor.close()
    return {"id": podcast_id, "title": title, "feed_url": feed_url, "image_url": image_url}
