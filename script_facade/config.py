"""Default configuration

Use environment variable to override
"""
import os

REQUEST_CACHE_URL = os.environ.get('REQUEST_CACHE_URL', 'redis://localhost:6379/0')
REQUEST_CACHE_EXPIRE = 24 * 60 * 60  # 24 hours

SERVER_NAME = os.getenv("SERVER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")


RXNAV_URL = os.getenv("RXNAV_URL", "https://rxnav.nlm.nih.gov")
RXNAV_LOOKUP_ENABLED = os.environ.get('RXNAV_LOOKUP_ENABLED', 'false').lower() == 'true'
