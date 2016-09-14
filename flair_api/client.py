import requests
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

DEFAULT_CLIENT_HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/json'
}


def relationship_data(data):
    return [m.to_relationship() for m in data] \
        if isinstance(data, list) else data.to_relationship()


class ApiError(Exception):
    def __init__(self, resp):
        self.status_code = resp.status_code
        self.body = resp.body
        try:
            self.json = resp.json()
        except:
            self.json = None


class Relationship(object):
    def __init__(self, rel, client, rel_data):
        self.client = client
        self.rel = rel
        self.self_href = rel_data.get('links', {}).get('self', '')
        self.related_href = rel_data.get('links', {}).get('related', '')
        self.data = rel_data.get('data', {})

    def get(self):
        return self.client.get_url(self.related_href)

    def add(self, data):
        data = data if isinstance(data, list) else [data]
        rel_form = relationship_data(data)
        self.data.append(rel_form)
        self.client.post_url(self.self_href, dict(data=rel_form))

    def update(self, data):
        rel_form = relationship_data(data)
        self.data = rel_form
        self.client.patch_url(self.self_href, dict(data=rel_form))
        return self.data

    def delete(self, data):
        data = data if isinstance(data, list) else [data]
        rel_form = relationship_data(data)
        self.data.remove(rel_form)
        self.client.delete_url(self.self_href, dict(data=rel_form))


class Resource(object):
    def __init__(self, client, id_, type_, attributes, relationships):
        self.client = client
        self.id_ = id_
        self.type_ = type_
        self.attributes = attributes
        self.relationships = {rel: Relationship(rel, self.client, data)
                              for rel, data in relationships.items()}
        self.deleted = False

    def __eq__(self, other):
        return self.type_ == other.type_ and self.id_ == other.id_

    def to_relationship(self):
        return {"id": self.id_, "type": self.type_}

    def get_self(self):
        resp = self.client.get(self.type_, id=self.id_)
        self.attributes = resp.attributes
        self.relationships = resp.relationships
        return self

    def get_rel(self, rel):
        return self.relationships[rel].get()

    def update(self, attributes={}, relationships={}):
        resp = self.client.update(
            self.type_, self.id_, attributes, relationships
        )
        self.attributes = resp.attributes
        self.relationships = resp.relationships
        return self

    def delete(self):
        self.client.delete(self.type_, self.id_)
        self.deleted = True

    def add_rel(self, **kwargs):
        for rel, val in kwargs.items():
            self.relationships[rel].add(val)

    def update_rel(self, **kwargs):
        for rel, val in kwargs.items():
            self.relationships[rel].update(val)

    def delete_rel(self, **kwargs):
        for rel, val in kwargs.items():
            self.relationships[rel].delete(val)


class Client(object):
    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 api_root='https://api-qa.flair.co/',
                 mapper={},
                 default_model=Resource):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_root = api_root
        self.mapper = mapper
        self.default_model = default_model

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
        resp = requests.get(
            self.create_url("/api/"), headers=DEFAULT_CLIENT_HEADERS
        )
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

    def resource_url(self, resource_type, id):
        resource_path = self.api_root_resp[resource_type]['self']
        if id:
            resource_path = resource_path + "/" + str(id)

        return resource_path

    def get(self, resource_type, id=None):
        self._fetch_token_if_not()
        self._fetch_api_root_if_not()
        return self.handle_resp(
            requests.get(
                self.create_url(self.resource_url(resource_type, id)),
                headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS)
            )
        )

    def to_relationship_dict(self, relationships):
        return {k: {'data': relationship_data(r)}
                for k, r in relationships.items()}

    def update(self, resource_type, id, attributes, relationships):
        self._fetch_token_if_not()
        self._fetch_api_root_if_not()
        rels = self.to_relationship_dict(relationships)
        req_body = {'data': {
            'id': id,
            'type': resource_type,
            'attributes': attributes,
            'relationships': rels
        }}

        return self.handle_resp(
            requests.patch(
                self.create_url(self.resource_url(resource_type, id)),
                headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS),
                json=req_body
            )
        )

    def delete(self, resource_type, id):
        self._fetch_token_if_not()
        self._fetch_api_root_if_not()
        requests.delete(
            self.create_url(self.resource_url(resource_type, id)),
            headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS)
        )

    def create(self, resource_type, attributes={}, relationships={}):
        self._fetch_token_if_not()
        self._fetch_api_root_if_not()
        rels = self.to_relationship_dict(relationships)
        req_body = {'data': {
            'type': resource_type,
            'attributes': attributes,
            'relationships': rels
        }}

        return self.handle_resp(
            requests.post(
                self.create_url(self.resource_url(resource_type, None)),
                headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS),
                json=req_body
            )
        )

    def delete_url(self, url, data):
        return self.handle_resp(requests.delete(
            self.create_url(url),
            headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS),
            json=data
        ))

    def patch_url(self, url, data):
        return self.handle_resp(requests.patch(
            self.create_url(url),
            headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS),
            json=data
        ))

    def post_url(self, url, data):
        return self.handle_resp(requests.post(
            self.create_url(url),
            headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS),
            json=data
        ))

    def get_url(self, url):
        return self.handle_resp(requests.get(
            self.create_url(url),
            headers=dict(self.token_header(), **DEFAULT_CLIENT_HEADERS)
        ))

    def create_model(self,
                     id=None,
                     type=None,
                     attributes={},
                     relationships={}):
        klass = self.mapper.get(type, self.default_model)
        return klass(self, id, type, attributes, relationships)

    def handle_resp(self, resp):
        if not resp.status_code == 204:
            body = resp.json()
        else:
            body = ''

        if resp.status_code == 200 and isinstance(body['data'], list):
            return [self.create_model(**r) for r in body['data']]
        elif resp.status_code == 200 or resp.status_code == 201:
            return self.create_model(**body['data'])
        elif resp.status_code >= 400:
            raise ApiError(resp)
        else:
            return body


def make_client(client_id, client_secret, root, mapper={}):
    c = Client(client_id=client_id, client_secret=client_secret, api_root=root, mapper=mapper)
    c.oauth_token()
    c.api_root_response()
    return c
