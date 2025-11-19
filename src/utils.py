import re
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def validate_linkedin_url(url: str) -> bool:
   
    if not url:
        return False

   
    patterns = [
        r'https?://(www\.)?linkedin\.com/in/[\w-]+/?',
        r'https?://(www\.)?linkedin\.com/pub/[\w-]+/?',
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True

    return False


def retry_on_failure(max_retries: int = 3, delay: int = 2, backoff: int = 2):
   
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")

            raise last_exception

        return wrapper
    return decorator


def sanitize_text(text: str) -> str:
  
    if not text:
        return ""

   
    text = ' '.join(text.split())

  
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')

    return text.strip()


def format_json_output(data: dict, indent: int = 2) -> str:
    
    import json
    return json.dumps(data, indent=indent, ensure_ascii=False)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def log_profile_info(profile_data: dict):
    
    logger.info("=" * 50)
    logger.info("Profile Information:")
    logger.info(f"  Name: {profile_data.get('name', 'N/A')}")
    logger.info(f"  Title: {profile_data.get('title', 'N/A')}")
    logger.info(f"  Company: {profile_data.get('company', 'N/A')}")

    about = profile_data.get('about')
    if about:
        logger.info(f"  About: {truncate_text(about, 100)}")
    else:
        logger.info("  About: N/A")

    logger.info("=" * 50)


def create_error_response(error_message: str, url: str = None) -> dict:
   
    response = {
        'name': None,
        'title': None,
        'company': None,
        'about': None,
        'email': None,
        'error': error_message,
        'status': 'failed'
    }

    if url:
        response['url'] = url

    return response
