import time
import hashlib
import requests
from app.core.config import settings

def get_podcast_index_headers():
    """
    Generate the required headers for authenticating with the Podcast Index API.
    """
    api_key = settings.PODCAST_INDEX_API_KEY
    api_secret = settings.PODCAST_INDEX_API_SECRET
    
    # The API documentation requires a hash of the API key, secret, and current time
    api_time = str(int(time.time()))
    data_to_hash = api_key + api_secret + api_time
    sha1_hash = hashlib.sha1(data_to_hash.encode()).hexdigest()
    
    headers = {
        "X-Auth-Date": api_time,
        "X-Auth-Key": api_key,
        "Authorization": sha1_hash,
        "User-Agent": "PodcastAdRemover/1.0"
    }
    return headers

def search_podcasts(query: str):
    """
    Search for podcasts by a query string.
    """
    headers = get_podcast_index_headers()
    url = f"https://api.podcastindex.org/api/1.0/search/byterm?q={query}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
