import os
import requests
import logging
from app.core.config import settings
# Removed: from app.main import BASE_DIR # Temporary import to access BASE_DIR from main.py

logger = logging.getLogger(__name__)

def download_audio_file(url: str, destination_folder: str, filename: str) -> str:
    """
    Downloads an audio file from a URL to a specified destination.
    Returns the full path to the downloaded file.
    """
    full_destination_folder = os.path.join(settings.BASE_DIR, destination_folder)
    os.makedirs(full_destination_folder, exist_ok=True)
    full_path = os.path.join(full_destination_folder, filename)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Successfully downloaded {url} to {full_path}")
        return full_path
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        raise
    except IOError as e:
        logger.error(f"Error writing file to {full_path}: {e}")
        raise

def process_audio_for_ad_removal(
    input_path: str, 
    output_folder: str, # Changed from output_path to output_folder
    markers_ms: list[int], 
    strategy: str,
    output_filename: str # New parameter for output filename
) -> str:
    """
    Applies ad removal rules to an audio file using pydub.
    Returns the path to the processed audio file.
    """
    full_output_folder = os.path.join(settings.BASE_DIR, output_folder)
    os.makedirs(full_output_folder, exist_ok=True)
    output_path = os.path.join(full_output_folder, output_filename)

    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
        
        processed_audio = AudioSegment.empty()

        if strategy == "remove_before" and markers_ms:
            # Keep audio from the first marker onwards
            processed_audio = audio[markers_ms[0]:]
        elif strategy == "remove_after" and markers_ms:
            # Keep audio up to the last marker
            processed_audio = audio[:markers_ms[-1]]
        elif strategy == "remove_between" and markers_ms and len(markers_ms) >= 2:
            # Keep segments outside the marked intervals
            # Ensure markers are sorted
            sorted_markers = sorted(markers_ms)
            
            # Start with the segment before the first marker
            current_segment_start = 0
            for i in range(0, len(sorted_markers), 2):
                start_ad = sorted_markers[i]
                end_ad = sorted_markers[i+1] if i+1 < len(sorted_markers) else audio.duration_seconds * 1000 # If odd number, remove till end

                processed_audio += audio[current_segment_start:start_ad]
                current_segment_start = end_ad
            
            # Add any remaining audio after the last marker
            if current_segment_start < audio.duration_seconds * 1000:
                processed_audio += audio[current_segment_start:]

        else:
            # If no specific strategy or markers, return original (or a copy)
            logger.info(f"No specific ad removal strategy or markers for {input_path}. Copying original.")
            processed_audio = audio
            
        processed_audio.export(output_path, format="mp3")
        logger.info(f"Successfully processed {input_path} to {output_path} with strategy {strategy}")
        return output_path
    except ImportError:
        logger.error("pydub not installed. Please install it with 'pip install pydub'")
        raise
    except Exception as e:
        logger.error(f"Error processing audio file {input_path}: {e}")
        raise
