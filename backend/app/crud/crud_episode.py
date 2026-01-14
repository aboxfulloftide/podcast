from mysql.connector.connection import MySQLConnection
from app.schemas.episode import Episode as EpisodeSchema
from datetime import datetime

def create_episode(db: MySQLConnection, podcast_id: int, episode: EpisodeSchema, download_path: str = None, edited_path: str = None, status: str = 'pending'):
    """
    Create a new episode record in the database.
    """
    cursor = db.cursor()
    query = """
        INSERT INTO episodes 
        (podcast_id, guid, title, original_audio_url, publication_date, download_path, edited_path, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        podcast_id,
        episode.guid,
        episode.title,
        str(episode.original_audio_url),
        episode.publication_date,
        download_path,
        edited_path,
        status
    ))
    db.commit()
    episode_id = cursor.lastrowid
    cursor.close()
    return {"id": episode_id, **episode.dict(), "podcast_id": podcast_id, "download_path": download_path, "edited_path": edited_path, "status": status}

def get_episode_by_guid_and_podcast_id(db: MySQLConnection, guid: str, podcast_id: int):
    """
    Get an episode by its GUID and podcast ID.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM episodes WHERE guid = %s AND podcast_id = %s"
    cursor.execute(query, (guid, podcast_id))
    episode = cursor.fetchone()
    cursor.close()
    return episode

def update_episode_status(db: MySQLConnection, episode_id: int, status: str, download_path: str = None, edited_path: str = None):
    """
    Update the status and optionally paths of an episode.
    """
    cursor = db.cursor()
    updates = ["status = %s"]
    params = [status]
    if download_path:
        updates.append("download_path = %s")
        params.append(download_path)
    if edited_path:
        updates.append("edited_path = %s")
        params.append(edited_path)
    
    query = f"UPDATE episodes SET {', '.join(updates)} WHERE id = %s"
    params.append(episode_id)
    cursor.execute(query, tuple(params))
    db.commit()
    cursor.close()
    return True

def get_episodes_by_podcast_id(db: MySQLConnection, podcast_id: int):
    """
    Get all episodes for a given podcast, ordered by publication date descending.
    """
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM episodes WHERE podcast_id = %s ORDER BY publication_date DESC"
    cursor.execute(query, (podcast_id,))
    episodes = cursor.fetchall()
    cursor.close()
    return episodes

def delete_episode(db: MySQLConnection, episode_id: int):
    """
    Delete an episode record from the database.
    """
    cursor = db.cursor()
    query = "DELETE FROM episodes WHERE id = %s"
    cursor.execute(query, (episode_id,))
    db.commit()
    cursor.close()
    return True
