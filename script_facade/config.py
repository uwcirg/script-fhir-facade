"""Default configuration

Use environment variable to override
"""
import os

REDIS_URL = os.environ.get(
    'REDIS_URL',
    'redis://localhost:6379/5' if os.environ.get('TESTING', 'false').lower() == 'true'
    else 'redis://localhost:6379/0',
)

REQUEST_CACHE_URL = os.environ.get('REQUEST_CACHE_URL', REDIS_URL)
REQUEST_CACHE_EXPIRE = 24 * 60 * 60  # 24 hours

SERVER_NAME = os.getenv("SERVER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")


RXNAV_URL = os.getenv("RXNAV_URL", "https://rxnav.nlm.nih.gov")
RXNAV_LOOKUP_ENABLED = os.environ.get('RXNAV_LOOKUP_ENABLED', 'false').lower() == 'true'
