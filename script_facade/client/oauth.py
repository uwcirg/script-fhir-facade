"""OAuth 2.0 JWT bearer grant for the OneHealthPort HIE PMP gateway."""
import hashlib
import os
import uuid

import redis
from flask import current_app

from script_facade.client.config import DefaultConfig as client_config
from script_facade.client.http import send_unpatched

JWT_BEARER_GRANT = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
_TOKEN_KEY_PREFIX = 'script_facade:oauth:access_token:'


def access_token_key(token_url, assertion):
    """Redis key scoped to the token URL and assertion, without storing either in the key."""
    material = '{}\n{}'.format(token_url, assertion).encode('utf-8')
    return _TOKEN_KEY_PREFIX + hashlib.sha256(material).hexdigest()


def _redis_url():
    """Return REQUEST_CACHE_URL when it is configured, otherwise None."""
    try:
        url = current_app.config.get('REQUEST_CACHE_URL')
    except RuntimeError:
        url = os.environ.get('REQUEST_CACHE_URL')
    return url or None


def _redis_client():
    url = _redis_url()
    if not url:
        return None
    return redis.StrictRedis.from_url(url)


def exchange_assertion(token_url, assertion):
    """Exchange the pre-issued JWT assertion for an access token.

    Returns (access_token, expires_in_seconds). Does not log the assertion or token.
    """
    response = send_unpatched(
        'POST',
        token_url,
        data={
            'grant_type': JWT_BEARER_GRANT,
            'assertion': assertion,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    if response.status_code == 401:
        current_app.logger.error("PDMP token endpoint rejected the JWT assertion")
        raise RuntimeError("OAuth JWT assertion was rejected")
    response.raise_for_status()

    payload = response.json()
    try:
        token = payload['access_token']
        expires_in = int(payload['expires_in'])
    except (KeyError, TypeError, ValueError):
        raise RuntimeError("OAuth token response was missing access_token or expires_in")
    if not token or expires_in <= 0:
        raise RuntimeError("OAuth token response was missing access_token or expires_in")
    return token, expires_in


def get_access_token():
    """Return a bearer access token, using Redis when REQUEST_CACHE_URL is set."""
    assertion = client_config.SCRIPT_JWT_ASSERTION
    if not assertion:
        raise RuntimeError("SCRIPT_JWT_ASSERTION is not configured")
    token_url = client_config.SCRIPT_TOKEN_URL
    key = access_token_key(token_url, assertion)

    cache = _redis_client()
    if cache is not None:
        cached = cache.get(key)
        if cached:
            return cached.decode('utf-8')

    token, expires_in = exchange_assertion(token_url, assertion)
    cache = _redis_client()
    if cache is not None:
        # TTL matches the token lifetime so Redis drops the key when it expires.
        cache.set(key, token, ex=expires_in)
    return token


def pmp_headers():
    """Headers required on an OAuth PMP submission, including a bearer token."""
    facility_id = client_config.SCRIPT_ORG_FACILITY_ID or client_config.SCRIPT_FROM_QUALIFIER
    return {
        'Content-Type': 'application/xml',
        'Authorization': 'Bearer {}'.format(get_access_token()),
        'x-doc-type': 'PMP',
        'x-org-facility-id': facility_id,
        'x-ref-id': uuid.uuid4().hex,
    }
