from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.crud import crud_podcast
from app.core import podcast_index
from app.schemas import podcast, episode
from mysql.connector.connection import MySQLConnection
from typing import List
import feedparser
from datetime import datetime

router = APIRouter()

@router.get("/search", response_model=podcast.PodcastSearchResult)
def search_podcasts_api(
    query: str,
    current_user: dict = Depends(deps.get_current_user) # Protect this endpoint
):
    """
    Search for podcasts.
    """
    try:
        results = podcast_index.search_podcasts(query)
        
        # Data cleaning: Ensure feeds have a valid, non-empty image URL
        cleaned_feeds = [
            feed for feed in results.get("feeds", []) 
            if isinstance(feed.get("image"), str) and feed.get("image").strip()
        ]
        results["feeds"] = cleaned_feeds
        results["count"] = len(cleaned_feeds)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{podcast_id}/episodes", response_model=List[episode.Episode])
def get_podcast_episodes(
    podcast_id: int,
    db: MySQLConnection = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user) # Protect this endpoint
):
    """
    Retrieve episodes for a given podcast from its RSS feed.
    """
    db_gen = next(db)
    podcast_db = crud_podcast.get_podcast_by_id(db_gen, podcast_id)
    if not podcast_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")

    feed = feedparser.parse(podcast_db['feed_url'])
    if feed.bozo:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not parse RSS feed: {feed.bozo_exception}")

    episodes = []
    for entry in feed.entries:
        audio_url = None
        # Try to find the audio enclosure
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('audio'):
                    audio_url = enclosure.get('href')
                    break
        
        # If no audio enclosure found, try directly from link if it's an audio file
        if not audio_url and hasattr(entry, 'link') and entry.link.endswith(('.mp3', '.ogg', '.wav', '.aac')):
             audio_url = entry.link

        if audio_url:
            # Safely get publication date
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6])
            
            episodes.append(episode.Episode(
                guid=getattr(entry, 'guid', audio_url), # Use audio_url as fallback for guid
                title=getattr(entry, 'title', 'Untitled Episode'),
                original_audio_url=audio_url,
                publication_date=pub_date if pub_date else datetime.min # Use datetime.min as fallback
            ))
    return episodes
