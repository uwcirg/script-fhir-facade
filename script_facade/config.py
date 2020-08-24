"""Default configuration

Use environment variable to override
"""
import os

RX_SRC_ID = os.getenv("RX_SRC_ID", "https://github.com/uwcirg/script-fhir-facade/")
SERVER_NAME = os.getenv("SERVER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")


RXNAV_URL = os.getenv("RXNAV_URL", "https://rxnav.nlm.nih.gov")
RXNAV_LOOKUP_ENABLED = os.environ.get('RXNAV_LOOKUP_ENABLED', 'false').lower() == 'true'
