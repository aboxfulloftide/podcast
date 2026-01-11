from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
import logging
import feedparser
from datetime import datetime
import os

from app.crud import crud_subscription, crud_episode, crud_ad_removal
from app.db.session import db_pool
from app.core import audio_utils, feed_utils
from app.core.config import settings
from app.schemas.episode import Episode as EpisodeSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def process_podcast_feed_job():
    """
    This function will be executed by the scheduler periodically.
    It will orchestrate the podcast processing pipeline.
    """
    logger.info("Starting podcast feed processing job...")
    db_connection = None
    try:
        db_connection = db_pool.get_connection()
        subscriptions = crud_subscription.get_all_subscriptions_with_podcast_details(db_connection)

        for sub in subscriptions:
            logger.info(f"Processing subscription: {sub['podcast_title']} for user {sub['user_id']}")
            
            feed = feedparser.parse(sub['podcast_feed_url'])
            if feed.bozo:
                logger.error(f"Error parsing RSS feed for {sub['podcast_title']}: {feed.bozo_exception}")
                continue

            # Get ad removal rules for this subscription
            ad_removal_rule = crud_ad_removal.get_ad_removal_rule_by_subscription_id(db_connection, sub['subscription_id'])
            
            for entry in feed.entries:
                audio_url = None
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if enclosure.get('type', '').startswith('audio'):
                            audio_url = enclosure.get('href')
                            break
                if not audio_url and hasattr(entry, 'link') and entry.link.endswith(('.mp3', '.ogg', '.wav', '.aac')):
                    audio_url = entry.link
                
                if not audio_url:
                    logger.warning(f"No audio URL found for entry in {sub['podcast_title']}: {getattr(entry, 'title', 'Untitled')}")
                    continue

                guid = getattr(entry, 'guid', audio_url)
                
                # Check if episode already exists in DB
                existing_episode = crud_episode.get_episode_by_guid_and_podcast_id(db_connection, guid, sub['podcast_id'])
                if existing_episode:
                    # For now, we only process new episodes.
                    # Future: could check for updates to existing episodes.
                    continue 

                # Process new episode
                logger.info(f"New episode found: {getattr(entry, 'title', 'Untitled')} from {sub['podcast_title']}")
                
                # Safely get publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                episode_schema = EpisodeSchema(
                    guid=guid,
                    title=getattr(entry, 'title', 'Untitled Episode'),
                    original_audio_url=audio_url,
                    publication_date=pub_date if pub_date else datetime.min
                )

                episode_record = None
                try:
                    # Create a pending record for the episode
                    episode_record = crud_episode.create_episode(db_connection, sub['podcast_id'], episode_schema, status='pending')

                    # Download original audio
                    raw_audio_dir = os.path.join(settings.RAW_AUDIO_PATH, str(sub['podcast_id']))
                    os.makedirs(raw_audio_dir, exist_ok=True)
                    raw_audio_filename = f"{episode_record['id']}_{guid.replace('/', '_').replace(':', '_')}.mp3" 
                    download_path = audio_utils.download_audio_file(
                        audio_url, 
                        raw_audio_dir,
                        raw_audio_filename
                    )
                    crud_episode.update_episode_status(db_connection, episode_record['id'], 'downloaded', download_path=download_path)
                    logger.info(f"Downloaded raw audio to {download_path}")

                    edited_path = None
                    if ad_removal_rule and ad_removal_rule['strategy'] != 'none' and ad_removal_rule['markers']:
                        # Apply ad removal
                        edited_audio_dir = os.path.join(settings.EDITED_AUDIO_PATH, str(sub['podcast_id']))
                        os.makedirs(edited_audio_dir, exist_ok=True)
                        edited_audio_filename = f"edited_{episode_record['id']}_{guid.replace('/', '_').replace(':', '_')}.mp3"
                        edited_path = audio_utils.process_audio_for_ad_removal(
                            download_path,
                            edited_audio_dir, # Pass output_folder
                            [m['marker_time_ms'] for m in ad_removal_rule['markers']],
                            ad_removal_rule['strategy'],
                            edited_audio_filename # Pass output_filename
                        )
                        crud_episode.update_episode_status(db_connection, episode_record['id'], 'processed', edited_path=edited_path)
                        logger.info(f"Processed audio to {edited_path} with strategy {ad_removal_rule['strategy']}")
                    else:
                        logger.info(f"No ad removal rules or strategy 'none' for {sub['podcast_title']}. Skipping ad removal.")
                        # If no ad removal, treat original as processed for custom feed purposes
                        crud_episode.update_episode_status(db_connection, episode_record['id'], 'processed', edited_path=download_path)


                except Exception as ep_e:
                    logger.error(f"Error processing episode {guid} for podcast {sub['podcast_title']}: {ep_e}")
                    if episode_record:
                        crud_episode.update_episode_status(db_connection, episode_record['id'], 'failed')
            
            # Generate custom RSS feed for the user
            try:
                processed_episodes = crud_episode.get_episodes_by_podcast_id(db_connection, sub['podcast_id'])
                # Filter for successfully processed episodes and sort by publication date
                processed_episodes = [
                    ep for ep in processed_episodes 
                    if ep['status'] == 'processed' and ep['publication_date'] is not None
                ]
                processed_episodes.sort(key=lambda x: x['publication_date'], reverse=True)

                feed_utils.generate_custom_rss_feed(
                    sub['subscription_id'],
                    sub['custom_feed_slug'],
                    sub['podcast_title'],
                    sub['podcast_image_url'],
                    sub['podcast_feed_url'],
                    processed_episodes
                )
                logger.info(f"Generated custom RSS feed for subscription {sub['subscription_id']}")
            except Exception as e:
                logger.error(f"Error generating custom RSS feed for {sub['podcast_title']}: {e}")
            
            # Enforce episode retention policy
            try:
                if sub['episode_retention_count'] > 0:
                    processed_episodes = crud_episode.get_episodes_by_podcast_id(db_connection, sub['podcast_id'])
                    # Filter for successfully processed episodes and sort by publication date
                    processed_episodes = [
                        ep for ep in processed_episodes 
                        if ep['status'] == 'processed' and ep['publication_date'] is not None
                    ]
                    processed_episodes.sort(key=lambda x: x['publication_date'], reverse=True)

                    if len(processed_episodes) > sub['episode_retention_count']:
                        episodes_to_delete = processed_episodes[sub['episode_retention_count']:]
                        for ep_to_delete in episodes_to_delete:
                            # Delete audio files
                            if ep_to_delete['download_path'] and os.path.exists(ep_to_delete['download_path']):
                                os.remove(ep_to_delete['download_path'])
                                logger.info(f"Deleted raw audio file: {ep_to_delete['download_path']}")
                            if ep_to_delete['edited_path'] and os.path.exists(ep_to_delete['edited_path']) and ep_to_delete['edited_path'] != ep_to_delete['download_path']:
                                os.remove(ep_to_delete['edited_path'])
                                logger.info(f"Deleted edited audio file: {ep_to_delete['edited_path']}")
                            
                            # Delete from database
                            crud_episode.delete_episode(db_connection, ep_to_delete['id'])
                            logger.info(f"Deleted old episode {ep_to_delete['title']} (ID: {ep_to_delete['id']}) due to retention policy.")
            except Exception as e:
                logger.error(f"Error enforcing retention policy for {sub['podcast_title']}: {e}")


    except Exception as e:
        logger.error(f"Error in podcast feed processing job: {e}")
    finally:
        if db_connection:
            db_connection.close()
            
    logger.info("Podcast feed processing job finished.")

def start_scheduler():
    """
    Starts the APScheduler.
    """
    scheduler.add_job(
        process_podcast_feed_job,
        trigger=IntervalTrigger(minutes=30),  # Run every 30 minutes
        id="podcast_feed_processor",
        name="Podcast Feed Processor",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started.")

def shutdown_scheduler():
    """
    Shuts down the APScheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")
