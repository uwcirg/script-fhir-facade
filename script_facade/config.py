"""Default configuration

Use environment variable to override
"""
import os

SERVER_NAME = os.getenv("SERVER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")


RXNAV_URL = os.getenv("RXNAV_URL")
RXNAV_LOOKUP_ENABLED = os.environ.get('RXNAV_LOOKUP_ENABLED', 'false').lower() == 'true'
