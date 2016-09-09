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

@pytest.yield_fixture
def mock_api(api_root, api_token, structure_body):
    with requests_mock.mock() as m:
        m.post('http://example.com/oauth/token', json={
            'access_token': api_token,
            'expires_in': 3600
        })
        m.get('http://example.com/api/', json=api_root)
        m.get('http://example.com/api/structures',
              headers=dict({'Authroization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(data=[structure_body]))
        m.post('http://example.com/api/structures',
               headers=dict({'Authroization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
               json=dict(data=structure_body))
        m.get('http://example.com/api/structures/1',
              headers=dict({'Authroization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
              json=dict(data=structure_body))
        m.patch('http://example.com/api/structures/1',
                headers=dict({'Authroization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                json=dict(data=dict(structure_body, **{'attributes': {'name': 'Better Name'}})))
        m.delete('http://example.com/api/structures/1',
                 headers=dict({'Authroization': 'Bearer ' + api_token}, **DEFAULT_CLIENT_HEADERS),
                 text='', status_code=204)
        yield m

@pytest.fixture
def api_client(mock_api):
    return make_client('client_id', 'client_secret', 'http://example.com')

def test_client_setup(api_client, api_root, api_token):
    assert api_client
    assert api_client.token == api_token
    assert api_client.api_root_resp == api_root['links']

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
    assert s.deleted == True

def test_client_create_model(api_client):
    s = api_client.create('structures', attributes={'name': 'Home Sweet Home'})
    assert s.attributes['name'] == 'Home Sweet Home'
