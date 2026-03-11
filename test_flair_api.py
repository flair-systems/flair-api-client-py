import pytest
from flair_api import make_client
from flair_api.client import DEFAULT_CLIENT_HEADERS
import requests_mock

@pytest.fixture
def api_root():
    return {
        'links': {
            'structures': {
                'self': '/api/structures',
                'type': 'structures'
            },
            'rooms': {
                'self': '/api/rooms',
                'type': 'rooms'
            }
        }
    }

@pytest.fixture
def api_token():
    return 'token'

@pytest.fixture
def structure_body():
    return {
        'id': '1',
        'type': 'structures',
        'attributes': {
            'name': 'Home Sweet Home'
        },
        'relationships': {
            'rooms': {
                'data': [{'id': '1', 'type': 'rooms'}],
                'links': {
                    'self': '/api/structures/1/relationships/rooms',
                    'related': '/api/structures/1/rooms'
                }
            }
        }
    }

@pytest.fixture
def mock_api(api_root, api_token, structure_body):
    with requests_mock.mock() as m:
        m.post('http://example.com/oauth2/token', json={
            'access_token': api_token,
            'expires_in': 3600
        })
        m.get('http://example.com/api/', json=api_root)
        m.get('http://example.com/api/structures',
              headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(meta={}, data=[structure_body]))
        m.post('http://example.com/api/structures',
               headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
               json=dict(meta={}, data=structure_body))
        m.get('http://example.com/api/structures/1',
              headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(meta={}, data=structure_body))
        m.patch('http://example.com/api/structures/1',
                headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                json=dict(meta={}, data=dict(structure_body, **{'attributes': {'name': 'Better Name'}})))
        m.delete('http://example.com/api/structures/1',
                 headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                 text='', status_code=204)
        yield m

@pytest.fixture
def mock_api_oauth1(api_root, api_token, structure_body):
    """Mock API for OAuth 1.0 authentication."""
    with requests_mock.mock() as m:
        m.post('http://example.com/oauth/token', json={
            'access_token': api_token,
            'expires_in': 3600
        })
        m.get('http://example.com/api/', json=api_root)
        m.get('http://example.com/api/structures',
              headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(meta={}, data=[structure_body]))
        m.post('http://example.com/api/structures',
               headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
               json=dict(meta={}, data=structure_body))
        m.get('http://example.com/api/structures/1',
              headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(meta={}, data=structure_body))
        m.patch('http://example.com/api/structures/1',
                headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                json=dict(meta={}, data=dict(structure_body, **{'attributes': {'name': 'Better Name'}})))
        m.delete('http://example.com/api/structures/1',
                 headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                 text='', status_code=204)
        yield m

@pytest.fixture
def mock_api_fallback(api_root, api_token, structure_body):
    """Mock API for testing OAuth 2.0 fallback to OAuth 1.0."""
    with requests_mock.mock() as m:
        # OAuth 2.0 endpoint fails
        m.post('http://example.com/oauth2/token', status_code=401)
        # OAuth 1.0 endpoint succeeds
        m.post('http://example.com/oauth/token', json={
            'access_token': api_token,
            'expires_in': 3600
        })
        m.get('http://example.com/api/', json=api_root)
        m.get('http://example.com/api/structures',
              headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(meta={}, data=[structure_body]))
        m.post('http://example.com/api/structures',
               headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
               json=dict(meta={}, data=structure_body))
        m.get('http://example.com/api/structures/1',
              headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(meta={}, data=structure_body))
        m.patch('http://example.com/api/structures/1',
                headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                json=dict(meta={}, data=dict(structure_body, **{'attributes': {'name': 'Better Name'}})))
        m.delete('http://example.com/api/structures/1',
                 headers=dict({'Authorization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                 text='', status_code=204)
        yield m

@pytest.fixture
def api_client(mock_api):
    return make_client('client_id', 'client_secret', 'http://example.com')

@pytest.fixture
def api_client_oauth1(mock_api_oauth1):
    """API client configured for OAuth 1.0."""
    return make_client('client_id', 'client_secret', 'http://example.com', oauth_version=1)

@pytest.fixture
def api_client_fallback(mock_api_fallback):
    """API client that will fallback from OAuth 2.0 to OAuth 1.0."""
    return make_client('client_id', 'client_secret', 'http://example.com', fallback_to_legacy_auth=True)

def test_client_setup(api_client, api_root, api_token):
    assert api_client
    assert api_client.token == api_token
    assert api_client.api_root_resp == api_root['links']
    # Verify OAuth version is set to default (2)
    assert api_client.oauth_version == 2

def test_client_get(api_client):
    s = api_client.get('structures')
    assert len(s) == 1
    assert s[0].id_ == '1'

def test_client_get_with_id(api_client):
    s = api_client.get('structures', id=1)
    assert s.id_ == '1'

def test_client_update_model(api_client):
    s = api_client.get('structures', id=1)
    s.update(attributes=dict(name='Better Name'))
    assert s.attributes['name'] == 'Better Name'

def test_client_deleted_model(api_client):
    s = api_client.get('structures', id=1)
    s.delete()
    assert s.deleted is True

def test_client_create_model(api_client):
    s = api_client.create('structures', attributes={'name': 'Home Sweet Home'})
    assert s.attributes['name'] == 'Home Sweet Home'

# OAuth 1.0 specific tests
def test_client_setup_oauth1(api_client_oauth1, api_root, api_token):
    """Test client setup with OAuth 1.0."""
    assert api_client_oauth1
    assert api_client_oauth1.token == api_token
    assert api_client_oauth1.api_root_resp == api_root['links']
    # Verify OAuth version is set to 1
    assert api_client_oauth1.oauth_version == 1

def test_client_get_oauth1(api_client_oauth1):
    """Test GET request with OAuth 1.0."""
    s = api_client_oauth1.get('structures')
    assert len(s) == 1
    assert s[0].id_ == '1'

def test_client_get_with_id_oauth1(api_client_oauth1):
    """Test GET request with ID using OAuth 1.0."""
    s = api_client_oauth1.get('structures', id=1)
    assert s.id_ == '1'

# Fallback behavior tests
def test_client_fallback_to_oauth1(api_client_fallback, api_root, api_token):
    """Test client fallback from OAuth 2.0 to OAuth 1.0."""
    assert api_client_fallback
    assert api_client_fallback.token == api_token
    assert api_client_fallback.api_root_resp == api_root['links']
    # Client should still be configured for OAuth 2.0, but authentication would have fallen back
    assert api_client_fallback.oauth_version == 2
