import requests
import copy
from urllib.parse import urljoin

DEFAULT_CLIENT_HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json'
}

class Relationship(object):
    def __init__(self, rel, client, rel_data):
        self.client = client
        self.rel = rel
        self.self_href = rel_data.get('links', {}).get('self', '')
        self.related_href = rel_data.get('links', {}).get('related', '')
        self.data = rel_data.get('data', {})

    def get(self):
        return self.client.get_url(self.related_href)

class Resource(object):
    def __init__(self, client, id_, type_, attributes, relationships):
        self.client = client
        self.id_ = id_
        self.type_ = type_
        self.attributes = attributes
        self.relationships = {rel: Relationship(rel, self.client, data) for rel, data in relationships.items()}

    def to_relationship(self):
        return {"id": self.id_, "type": self.type_}

    def get_self(self):
        return self.client.get(self.type_, id=self.id_)

    def get_rel(self, rel):
        return self.relationships[rel].get()

class Client(object):
    def __init__(self, client_id=None, client_secret=None, api_root='https://api-qa.flair.co/'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_root = api_root

    def create_url(self, path):
        return urljoin(self.api_root, path)

    def oauth_token(self):
        resp = requests.post(self.create_url("/oauth/token"), data=dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type="client_credentials"
        ))

        self.token = resp.json().get('access_token')
        self.expires_in = resp.json().get('expires_in')

        return resp.status_code

    def api_root_response(self):
        resp = requests.get(self.create_url("/api/"), headers=DEFAULT_CLIENT_HEADERS)
        self.api_root_resp = resp.json().get('links')

        return resp.status_code

    def _fetch_token_if_not(self):
        if self.token is None:
            return self.oauth_token()

    def _fetch_api_root_if_not(self):
        if self.api_root_resp is None:
            return self.api_root_response()

    def token_header(self):
        return {'Authorization': 'Bearer ' + self.token}

    def get(self, resource_type, id=None):
        resource_path = self.api_root_resp[resource_type]['self']
        if id:
            resource_path = resource_path + "/" + str(id)

        return self.handle_resp(requests.get(self.create_url(resource_path), headers={**self.token_header() , **DEFAULT_CLIENT_HEADERS}))

    def get_url(self, url):
        return self.handle_resp(requests.get(self.create_url(url), headers={**self.token_header() , **DEFAULT_CLIENT_HEADERS}))

    def handle_resp(self, resp):
        print(resp.status_code)
        body = resp.json()

        if resp.status_code == 200 and isinstance(body['data'], list):
            return [Resource(self, r['id'], r['type'], r['attributes'], r['relationships']) for r in body['data']]
        elif resp.status_code == 200:
            return Resource(self, body['data']['id'], body['data']['type'], body['data']['attributes'], body['data']['relationships'] )
        else:
            return body

def make_client(client_id, client_secret, root):
    c = Client(client_id=client_id, client_secret=client_secret, api_root=root)
    c.oauth_token()
    c.api_root_response()
    return c
