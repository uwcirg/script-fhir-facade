"""HTTP calls that do not go through the process-wide requests-cache patch.

``requests_cache.install_cache`` replaces ``requests.Session``. This module is
imported by the PDMP client before that patch runs, and keeps the original
session class for the token exchange and the NCPDP submission.
"""
from requests.sessions import Session as UnpatchedSession

# Bound at import, while ``requests.sessions.Session`` is still the original class.
_unpatched_request = UnpatchedSession.request


def send_unpatched(method, url, **kwargs):
    """Send one HTTP request with the session class captured before requests-cache."""
    return _unpatched_request(UnpatchedSession(), method, url, **kwargs)
