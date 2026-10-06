import pytest
from requests import HTTPError

from script_facade.client import oauth
from script_facade.client.client import _post_pdmp, session_data
from script_facade.client.config import DefaultConfig as client_config


TOKEN_URL = 'https://token.example/ohp/oauth/jwt/token'
ASSERTION = 'header.payload.signature'
PMP_URL = 'https://pmp.example/ncpdp_requests'


def _token_response(mocker, access_token='access-token', expires_in='3600'):
    response = mocker.Mock(status_code=201)
    response.json.return_value = {
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': expires_in,
    }
    return response


def _configure_oauth(mocker, assertion=ASSERTION):
    mocker.patch.object(client_config, 'SCRIPT_JWT_ASSERTION', assertion)
    mocker.patch.object(client_config, 'SCRIPT_TOKEN_URL', TOKEN_URL)
    mocker.patch.object(client_config, 'SCRIPT_ORG_FACILITY_ID', '7uycso22')
    mocker.patch.object(client_config, 'SCRIPT_ENDPOINT_URL', PMP_URL)
    mocker.patch.object(client_config, 'SCRIPT_MOCK_URL', None)


def test_token_request_posts_assertion(app, mocker):
    _configure_oauth(mocker)
    mocker.patch.object(oauth, '_redis_client', return_value=None)
    send = mocker.patch(
        'script_facade.client.oauth.send_unpatched',
        return_value=_token_response(mocker),
    )

    with app.app_context():
        assert oauth.get_access_token() == 'access-token'

    method, url = send.call_args[0]
    data = send.call_args[1]['data']
    assert method == 'POST'
    assert url == TOKEN_URL
    assert data['grant_type'] == 'urn:ietf:params:oauth:grant-type:jwt-bearer'
    assert data['assertion'] == ASSERTION
    assert send.call_args[1]['headers']['Content-Type'] == 'application/x-www-form-urlencoded'


def test_access_token_redis_ttl_uses_expires_in(app, mocker):
    _configure_oauth(mocker)
    cache = mocker.Mock()
    cache.get.return_value = None
    mocker.patch.object(oauth, '_redis_client', return_value=cache)
    mocker.patch(
        'script_facade.client.oauth.send_unpatched',
        return_value=_token_response(mocker, expires_in='3600'),
    )

    with app.app_context():
        assert oauth.get_access_token() == 'access-token'

    key, value = cache.set.call_args[0]
    assert key == oauth.access_token_key(TOKEN_URL, ASSERTION)
    assert value == 'access-token'
    assert cache.set.call_args[1]['ex'] == 3600


def test_cached_access_token_skips_token_endpoint(app, mocker):
    _configure_oauth(mocker)
    cache = mocker.Mock()
    cache.get.return_value = b'cached-token'
    mocker.patch.object(oauth, '_redis_client', return_value=cache)
    send = mocker.patch('script_facade.client.oauth.send_unpatched')

    with app.app_context():
        assert oauth.get_access_token() == 'cached-token'

    send.assert_not_called()
    cache.set.assert_not_called()


def test_oauth_submission_headers_and_no_client_cert(app, mocker):
    _configure_oauth(mocker)
    cache = mocker.Mock()
    cache.get.return_value = b'access-1'
    mocker.patch.object(oauth, '_redis_client', return_value=cache)
    response = mocker.Mock(status_code=200, text='<Message/>')
    send = mocker.patch('script_facade.client.client.send_unpatched', return_value=response)

    with app.app_context():
        body = _post_pdmp('Luke', 'Skywalker', '1977-01-12', 'AB1234567', '20170701')

    assert body == '<Message/>'
    method, url = send.call_args[0]
    headers = send.call_args[1]['headers']
    assert method == 'POST'
    assert url == PMP_URL
    assert headers['Authorization'] == 'Bearer access-1'
    assert headers['x-doc-type'] == 'PMP'
    assert headers['x-org-facility-id'] == '7uycso22'
    assert headers['Content-Type'] == 'application/xml'
    assert headers['x-ref-id']
    assert 'cert' not in send.call_args[1]


def test_certificate_auth_when_assertion_absent(app, mocker):
    _configure_oauth(mocker, assertion=None)
    response = mocker.Mock(status_code=200, text='<Message/>')
    send = mocker.patch('script_facade.client.client.send_unpatched', return_value=response)

    with app.app_context():
        body = _post_pdmp('Luke', 'Skywalker', '1977-01-12', 'AB1234567', '20170701')

    assert body == '<Message/>'
    assert send.call_args[1]['cert'] == session_data['cert']
    assert 'Authorization' not in send.call_args[1]['headers']


def test_rejected_access_token_is_not_retried(app, mocker):
    _configure_oauth(mocker)
    cache = mocker.Mock()
    cache.get.return_value = b'stale-token'
    mocker.patch.object(oauth, '_redis_client', return_value=cache)
    rejected = mocker.Mock(status_code=401, text='unauthorized')
    rejected.raise_for_status.side_effect = HTTPError('401')
    send = mocker.patch('script_facade.client.client.send_unpatched', return_value=rejected)

    with app.app_context():
        with pytest.raises(HTTPError):
            _post_pdmp('Luke', 'Skywalker', '1977-01-12', 'AB1234567', '20170701')

    assert send.call_count == 1
    cache.delete.assert_not_called()


def test_rejected_assertion(app, mocker):
    _configure_oauth(mocker)
    mocker.patch.object(oauth, '_redis_client', return_value=None)
    mocker.patch(
        'script_facade.client.oauth.send_unpatched',
        return_value=mocker.Mock(status_code=401),
    )

    with app.app_context():
        with pytest.raises(RuntimeError, match='assertion was rejected'):
            oauth.get_access_token()


def test_no_redis_when_cache_url_unset(app, mocker):
    _configure_oauth(mocker)
    send = mocker.patch(
        'script_facade.client.oauth.send_unpatched',
        return_value=_token_response(mocker),
    )

    with app.app_context():
        app.config['REQUEST_CACHE_URL'] = None
        assert oauth.get_access_token() == 'access-token'
        assert oauth.get_access_token() == 'access-token'

    assert send.call_count == 2


def test_http_error_from_submission_is_raised(app, mocker):
    _configure_oauth(mocker, assertion=None)
    response = mocker.Mock(status_code=500, text='error')
    response.raise_for_status.side_effect = HTTPError('500')
    mocker.patch('script_facade.client.client.send_unpatched', return_value=response)

    with app.app_context():
        with pytest.raises(HTTPError):
            _post_pdmp('Luke', 'Skywalker', '1977-01-12', 'AB1234567', '20170701')
