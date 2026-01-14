import os
import logging
from feedgen.feed import FeedGenerator
from app.core.config import settings # Import settings
from datetime import datetime
# Removed: from app.main import BASE_DIR # Temporary import to access BASE_DIR from main.py

logger = logging.getLogger(__name__)


def generate_custom_rss_feed(
    subscription_id: int,
    custom_feed_slug: str,
    podcast_title: str,
    podcast_image_url: str,
    podcast_feed_url: str, # Original feed URL
    episodes: list # List of processed episode dictionaries
):
    """
    Generates a custom RSS feed for a subscribed podcast.
    """
    fg = FeedGenerator()
    fg.id(f"urn:uuid:{custom_feed_slug}")
    fg.title(f"{podcast_title} (Ad-Free)")
    fg.author({'name': 'Podcast Ad-Remover', 'email': 'noreply@example.com'})
    fg.link(href=podcast_feed_url, rel='alternate') # Link to original feed
    fg.logo(podcast_image_url)
    fg.subtitle(f'Ad-free version of {podcast_title}')
    fg.link(href=f"{settings.CUSTOM_FEEDS_BASE_URL}/{custom_feed_slug}.xml", rel='self')
    fg.language('en') # Assuming English for now, could be dynamic
    fg.image(podcast_image_url)

    for ep in episodes:
        fe = fg.add_entry()
        fe.id(f"urn:uuid:{ep['guid']}") # Use original GUID
        fe.title(ep['title'])
        fe.link(href=ep['original_audio_url']) # Link to original audio for compatibility
        
        # Ensure publication_date is a datetime object, convert if necessary
        if isinstance(ep['publication_date'], str):
            try:
                pub_date = datetime.fromisoformat(ep['publication_date'])
            except ValueError:
                pub_date = datetime.min # Fallback
        else:
            pub_date = ep['publication_date']
        
        fe.published(pub_date.replace(tzinfo=None)) # Ensure datetime is naive for feedgen
        fe.description(f"Ad-free version of: {ep['title']}")
        
        # Determine which audio URL to use (edited or original if no edit)
        audio_file_path = ep['edited_path'] if ep['edited_path'] else ep['download_path']
        
        # Ensure audio_file_path is a local path and convert to a public URL
        # Assuming the server serves /custom-media/ for edited podcasts
        if audio_file_path and os.path.exists(audio_file_path):
            # The path needs to be relative to the BASE_DIR
            relative_path_from_base = os.path.relpath(audio_file_path, start=settings.BASE_DIR)
            
            # Construct the public URL using the base URL for media files
            # This requires a dedicated endpoint to serve these files
            public_audio_url = f"{settings.CUSTOM_FEEDS_BASE_URL}/media/{relative_path_from_base}"
            fe.enclosure(public_audio_url, 0, 'audio/mpeg') # Length needs to be determined
        else:
            logger.warning(f"Audio file not found for episode {ep['guid']} at {audio_file_path}. Using original audio URL.")
            fe.enclosure(ep['original_audio_url'], 0, 'audio/mpeg') # Fallback to original
            


    # Ensure the directory for custom feeds exists
    output_dir = os.path.join(settings.BASE_DIR, settings.CUSTOM_FEEDS_PATH)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the RSS feed to a file
    feed_path = os.path.join(output_dir, f"{custom_feed_slug}.xml")
    fg.rss_file(feed_path, pretty=True)
    
    return feed_path