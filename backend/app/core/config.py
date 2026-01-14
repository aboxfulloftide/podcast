import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DB_USER: str = os.getenv("USER_NAME")
    DB_PASSWORD: str = os.getenv("PASSWORD")
    DB_HOST: str = os.getenv("HOST")
    DB_NAME: str = os.getenv("DATABASE_NAME")
    DB_PORT: int = os.getenv("PORT")

    # Podcast Index API settings
    PODCAST_INDEX_API_KEY: str = os.getenv("PODCAST_INDEX_API_KEY")
    PODCAST_INDEX_API_SECRET: str = os.getenv("PODCAST_INDEX_API_SECRET")

    # JWT settings
    SECRET_KEY: str = "a_very_secret_key"  # Replace with a real secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage Paths
    RAW_AUDIO_PATH: str = "storage/podcasts/raw"
    EDITED_AUDIO_PATH: str = "storage/podcasts/edited"
    CUSTOM_FEEDS_PATH: str = "storage/feeds" # Path where generated RSS feed XML files are stored
    
    # Base URL for custom feeds (e.g., http://your-domain.com/custom-feeds)
    # This should match how your web server (e.g., Nginx or FastAPI static files) exposes these.
    CUSTOM_FEEDS_BASE_URL: str = "http://localhost:8000/custom-feeds" # Default for local dev

    # Project Base Directory
    # This assumes config.py is in backend/app/core/
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

settings = Settings()
