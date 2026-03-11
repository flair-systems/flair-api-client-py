import requests
import time
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

class EmptyBodyException(Exception):
    def __init__(self, resp):
        self.status_code = resp.status_code

    def __str__(self):
        return self.__class__.__name__ + "<HTTP Response: " + \
            str(self.status_code) + ">"

class ApiError(Exception):
    def __init__(self, resp):
        self.status_code = resp.status_code
        self.body = resp.text
        try:
            self.json_body = resp.json()
            self.error_details = self.json_body.get('errors') or self.json_body.get('error_description') or self.json_body.get('error')
        except ValueError:
            self.json_body = None
            self.error_details = None

    def __str__(self):
        details = f", Details: {self.error_details}" if self.error_details else ""
        body_preview = f", Body: {self.body[:100]}..." if self.body else ""
        return (f"{self.__class__.__name__}<HTTP Response: {self.status_code}"
                f"{details}{body_preview}>")

class AuthenticationError(ApiError):
    """Specific error for authentication failures."""
    pass

class Relationship(object):
    def __init__(self, rel, client, rel_data):
        self.client = client
        self.rel = rel
        self.self_href = rel_data.get('links', {}).get('self', '')
        self.related_href = rel_data.get('links', {}).get('related', '')
        self.data = rel_data.get('data', {})

    def get(self, **params):
        return self.client.get_url(self.related_href, **params)

    def add(self, data):
        data = data if isinstance(data, list) else [data]
        rel_form = relationship_data(data)
        if not isinstance(self.data, list) and isinstance(rel_form, list):
             if self.data is None: self.data = []
             elif not isinstance(self.data, list): self.data = [self.data]
        elif isinstance(self.data, list) and not isinstance(rel_form, list):
             rel_form = [rel_form] 
        self.client.post_url(self.self_href, dict(data=rel_form))

    def update(self, data):
        rel_form = relationship_data(data)
        self.client.patch_url(self.self_href, dict(data=rel_form))
        self.data = rel_form
        return self.data

    def delete(self, data):
        data = data if isinstance(data, list) else [data]
        rel_form = relationship_data(data)
        self.client.delete_url(self.self_href, dict(data=rel_form))

class ResourceCollection(object):
    def __init__(self, client, meta, type_, resources):
        self.client = client
        self.type_ = type_
        self.resources = resources
        self.meta = meta

    def load_next_page(self):
        if self.meta.get('next'):
            col = self.client.get_url(self.meta['next'])
            if isinstance(col, ResourceCollection):
                self.resources.extend(col.resources)
                self.meta = col.meta
            else:
                print(f"Warning: Expected ResourceCollection from next page, got {type(col)}")
                self.meta['next'] = None

    def __getitem__(self, idx):
        return self.resources[idx]

    def __len__(self):
        return len(self.resources)

    def __iter__(self):
        current_index = 0
        while True:
            if current_index < len(self.resources):
                yield self.resources[current_index]
                current_index += 1
            elif self.meta.get('next'):
                self.load_next_page()
                if current_index >= len(self.resources):
                     break
            else:
                break

    def all(self):
        """Yields all resources, loading next pages as needed."""
        for resource in self:
            yield resource

    def up_to(self, limit):
        while len(self.resources) < limit and self.meta.get('next'):
            self.load_next_page()
        return self

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
        if not isinstance(other, Resource):
            return NotImplemented
        return self.type_ == other.type_ and self.id_ == other.id_

    def to_relationship(self):
        return {"id": self.id_, "type": self.type_}

    def get_self(self):
        resp = self.client.get(self.type_, id=self.id_)
        self.attributes = resp.attributes
        self.relationships = resp.relationships
        return self

    def get_rel(self, rel, **params):
        if rel not in self.relationships:
             raise KeyError(f"Relationship '{rel}' not found for this resource.")
        return self.relationships[rel].get(**params)

    def update(self, attributes={}, relationships={}):
        resp = self.client.update(
            self.type_, self.id_, attributes=attributes, relationships=relationships
        )
        self.attributes = resp.attributes
        self.relationships = resp.relationships
        return self

    def delete(self):
        self.client.delete(self.type_, self.id_)
        self.deleted = True

    def add_rel(self, **kwargs):
        for rel, val in kwargs.items():
            if rel not in self.relationships:
                 raise KeyError(f"Relationship '{rel}' not found. Cannot add.")
            self.relationships[rel].add(val)

    def update_rel(self, **kwargs):
        for rel, val in kwargs.items():
            if rel not in self.relationships:
                 raise KeyError(f"Relationship '{rel}' not found. Cannot update.")
            self.relationships[rel].update(val)

    def delete_rel(self, **kwargs):
        for rel, val in kwargs.items():
            if rel not in self.relationships:
                 raise KeyError(f"Relationship '{rel}' not found. Cannot delete.")
            self.relationships[rel].delete(val)


class Client(object):
    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 api_root='https://api.flair.co/',
                 mapper={},
                 admin=False,
                 default_model=Resource,
                 oauth_version=2,  # Default to OAuth 2.0 (credentials from the Flair App)
                 grant_type='client_credentials',  # Default OAuth 2.0 grant type
                 scope=None,  # Optional scope string
                 username=None,  # For OAuth 2.0 'password' grant
                 password=None,  # For OAuth 2.0 'password' grant
                 redirect_uri=None,  # For OAuth 2.0 'authorization_code' grant
                 auth_code=None,  # For OAuth 2.0 'authorization_code' grant (initial code)
                 refresh_token_initial=None,  # If starting with a known refresh token
                 fallback_to_legacy_auth=True  # Allow fallback to OAuth 1.0 on initial auth failure
                 ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_root = api_root.rstrip('/') + '/'
        self.mapper = mapper
        self.admin = admin
        self.default_model = default_model

        # Authentication details
        self.oauth_version = oauth_version
        self.grant_type = grant_type
        self.scope = scope
        self.username = username
        self.password = password
        self.redirect_uri = redirect_uri
        self.auth_code = auth_code

        # Token storage
        self.access_token = None
        self.refresh_token = refresh_token_initial
        self.token_type = 'Bearer'
        self.expires_at = None
        self.granted_scope = None

        self.api_root_resp = None
        self.fallback_to_legacy_auth = fallback_to_legacy_auth

    @property
    def token(self):
        """Backward compatibility property for accessing the token."""
        return self.access_token

    def create_url(self, path):
        path = path.lstrip('/')
        return urljoin(self.api_root, path)

    def _process_token_response(self, resp):
        """Processes the JSON response from a token request."""
        try:
            resp.raise_for_status()
            data = resp.json()

            if 'access_token' not in data:
                raise AuthenticationError(resp) 

            self.access_token = data['access_token']
            self.token_type = data.get('token_type', 'Bearer')
            self.granted_scope = data.get('scope')

            if 'refresh_token' in data:
                self.refresh_token = data['refresh_token']

            expires_in = data.get('expires_in')
            if expires_in:
                buffer = 30
                self.expires_at = time.time() + int(expires_in) - buffer
            else:
                self.expires_at = None

            return resp.status_code

        except requests.exceptions.RequestException as e:
            new_exc = AuthenticationError(e.response if e.response is not None else resp)
            new_exc.__cause__ = e
            raise new_exc
        except ValueError as e:
             new_exc = AuthenticationError(resp)
             new_exc.__cause__ = e
             raise new_exc

    def _auth_legacy(self):
        """Authenticate using the original /oauth/token endpoint."""
        token_url = self.create_url("/oauth/token")
        payload = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type="client_credentials"
        )
        print("Attempting Legacy Authentication...")
        resp = requests.post(token_url, data=payload)
        try:
            resp.raise_for_status()
            data = resp.json()
            self.access_token = data.get('access_token')
            self.token_type = 'Bearer'
            expires_in = data.get('expires_in')
            if expires_in:
                buffer = 30
                self.expires_at = time.time() + int(expires_in) - buffer
            else:
                 self.expires_at = None
            if not self.access_token:
                raise AuthenticationError(resp)
            print("Legacy Authentication Successful.")
            return resp.status_code
        except requests.exceptions.RequestException as e:
            new_exc = AuthenticationError(e.response if e.response is not None else resp)
            new_exc.__cause__ = e
            raise new_exc
        except ValueError as e:
            new_exc = AuthenticationError(resp)
            new_exc.__cause__ = e
            raise new_exc

    def _auth_oauth2(self, grant_type_override=None):
        """Authenticate using OAuth 2.0 /oauth2/token endpoint."""
        token_url = self.create_url("/oauth2/token")
        current_grant_type = grant_type_override or self.grant_type
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': current_grant_type,
        }
        if self.scope:
            payload['scope'] = self.scope

        print(f"Attempting OAuth 2.0 Authentication (grant_type: {current_grant_type})...")

        if current_grant_type == 'client_credentials':
            pass
        elif current_grant_type == 'password':
            if not self.username or not self.password:
                raise ValueError("Username and password required for 'password' grant type.")
            payload['username'] = self.username
            payload['password'] = self.password
        elif current_grant_type == 'authorization_code':
            if not self.auth_code or not self.redirect_uri:
                raise ValueError("Authorization code and redirect_uri required for 'authorization_code' grant type.")
            payload['code'] = self.auth_code
            payload['redirect_uri'] = self.redirect_uri
        elif current_grant_type == 'refresh_token':
            if not self.refresh_token:
                raise ValueError("Refresh token required for 'refresh_token' grant type.")
            payload['refresh_token'] = self.refresh_token
        else:
            raise ValueError(f"Unsupported grant_type: {current_grant_type}")

        resp = requests.post(token_url, data=payload)
        status_code = self._process_token_response(resp)
        print(f"OAuth 2.0 Authentication ({current_grant_type}) Successful.")
        if current_grant_type == 'authorization_code':
            self.auth_code = None
        return status_code

    def authenticate(self):
        """Get the initial access token based on configuration."""
        try:
            if self.oauth_version == 2:
                return self._auth_oauth2()
            elif self.oauth_version == 1:
                return self._auth_legacy()
            else:
                raise ValueError(f"Unsupported oauth_version: {self.oauth_version}")
        except AuthenticationError as e:
            print(f"Initial authentication failed: {e}")
            if self.oauth_version == 2 and self.fallback_to_legacy_auth:
                print("Attempting fallback to legacy authentication...")
                try:
                    return self._auth_legacy()
                except AuthenticationError as fallback_e:
                    print(f"Legacy fallback authentication also failed: {fallback_e}")
                    raise fallback_e
            else:
                raise e

    def refresh_oauth2_token(self):
        """Refresh the OAuth 2.0 token using the refresh token."""
        if not self.refresh_token:
            print("No refresh token available. Cannot refresh.")
            raise AuthenticationError("Refresh token missing, cannot refresh.")

        print("Access token expired or nearing expiry. Refreshing...")
        try:
            return self._auth_oauth2(grant_type_override='refresh_token')
        except AuthenticationError as e:
            print(f"Failed to refresh token: {e}")
            self.access_token = None
            self.refresh_token = None
            self.expires_at = None
            raise e

    def _ensure_valid_token(self):
        """Checks if token exists and is valid, refreshes if needed."""
        if self.access_token is None:
            print("No access token found. Authenticating...")
            self.authenticate()
        elif self.expires_at is not None and time.time() >= self.expires_at:
            print("Access token expired.")
            if self.oauth_version == 2 and self.refresh_token:
                try:
                    self.refresh_oauth2_token()
                except AuthenticationError:
                    print("Token refresh failed. Attempting full re-authentication...")
                    self.authenticate()
            else:
                 print("No refresh mechanism or not OAuth 2.0. Re-authenticating fully...")
                 self.authenticate()

    def token_header(self):
        """Returns the Authorization header."""
        if not self.access_token:
             raise AuthenticationError("Cannot create token header: Access token missing.")
        headers = {'Authorization': f'{self.token_type} {self.access_token}'}
        if self.admin:
            headers['x-admin-mode'] = 'admin'
        return headers

    def api_root_response(self):
        """Fetches and caches the API root links."""
        url = self.create_url("/api/")
        try:
            resp = requests.get(url, headers=DEFAULT_CLIENT_HEADERS)
            resp.raise_for_status()
            self.api_root_resp = resp.json().get('links')
            if not self.api_root_resp:
                 print(f"Warning: No 'links' found in API root response from {url}")
            return resp.status_code
        except requests.exceptions.RequestException as e:
             print(f"Error fetching API root {url}: {e}")
             raise ApiError(e.response if e.response is not None else None) from e
        except ValueError:
             raise ApiError(resp)

    def _fetch_api_root_if_not(self):
        """Ensures API root links are fetched."""
        if self.api_root_resp is None:
            return self.api_root_response()

    def resource_url(self, resource_type, id=None):
        """Constructs URL for a resource type, using cached root links."""
        self._fetch_api_root_if_not()
        if self.api_root_resp is None:
             raise RuntimeError("API root links could not be fetched. Cannot construct resource URL.")
        if resource_type not in self.api_root_resp:
             raise KeyError(f"Resource type '{resource_type}' not found in API root links.")

        resource_path = self.api_root_resp[resource_type].get('self')
        if not resource_path:
             raise ValueError(f"No 'self' link found for resource type '{resource_type}' in API root.")

        base_url = self.create_url(resource_path)

        full_url = base_url
        if id is not None:
             full_url = full_url.rstrip('/')+'/'+str(id)
        return full_url

    def _make_request(self, method, url, headers=None, params=None, json_data=None):
        """Internal helper to make authenticated requests."""
        self._ensure_valid_token()
        self._fetch_api_root_if_not()

        request_headers = self.token_header()
        request_headers.update(DEFAULT_CLIENT_HEADERS)
        if headers:
            request_headers.update(headers)

        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=json_data
            )
            return self.handle_resp(resp)
        except requests.exceptions.RequestException as e:
            raise ApiError(e.response if e.response is not None else None) from e

    def get(self, resource_type, id=None, params=None):
        full_url = self.resource_url(resource_type, id)
        return self._make_request('GET', full_url, params=params)

    def get_url(self, url, **params):
        if not url.startswith(self.api_root):
            full_url = self.create_url(url)
        else:
            full_url = url
        return self._make_request('GET', full_url, params=params)

    def to_relationship_dict(self, relationships):
        """Formats relationships for API requests."""
        return {k: {'data': relationship_data(r)}
                for k, r in relationships.items()}

    def update(self, resource_type, id, attributes={}, relationships={}):
        full_url = self.resource_url(resource_type, id)
        rels = self.to_relationship_dict(relationships)
        req_body = {'data': {
            'id': str(id),
            'type': resource_type,
            'attributes': attributes,
            **({'relationships': rels} if rels else {})
        }}

        return self._make_request('PATCH', full_url, json_data=req_body)

    def patch_url(self, url, data):
        if not url.startswith(self.api_root):
            full_url = self.create_url(url)
        else:
           full_url = url
        return self._make_request('PATCH', full_url, json_data=data)

    def delete(self, resource_type, id):
        full_url = self.resource_url(resource_type, id)
        return self._make_request('DELETE', full_url)

    def delete_url(self, url, data=None):
        if not url.startswith(self.api_root):
            full_url = self.create_url(url)
        else:
           full_url = url
        return self._make_request('DELETE', full_url, json_data=data)

    def create(self, resource_type, attributes={}, relationships={}, params={}):
        collection_url = self.resource_url(resource_type, id=None)
        rels = self.to_relationship_dict(relationships)
        req_body = {'data': {
            'type': resource_type,
            'attributes': attributes,
             **({'relationships': rels} if rels else {})
        }}

        return self._make_request('POST', collection_url, params=params, json_data=req_body)

    def post_url(self, url, data, params=None):
        if not url.startswith(self.api_root):
            full_url = self.create_url(url)
        else:
           full_url = url
        return self._make_request('POST', full_url, params=params, json_data=data)

    def create_model(self,
                     id=None,
                     type=None,
                     attributes={},
                     relationships={},
                     **kwargs):
        """Creates a Resource or specific mapped model instance."""
        if not type:
            raise ValueError("Resource 'type' is required to create a model.")
        klass = self.mapper.get(type, self.default_model)
        return klass(client=self, id_=id, type_=type, attributes=attributes, relationships=relationships)

    def handle_resp(self, resp):
        """Processes the HTTP response, checks status, and creates models."""
        status_code = resp.status_code

        if 200 <= status_code < 300:
            if status_code == 204:
                return None
            try:
                if not resp.content:
                     print(f"Warning: Received status {status_code} with empty body.")
                     return None

                body = resp.json()

                if 'data' not in body:
                     print(f"Warning: Response body does not contain 'data' key. Body: {body}")
                     return body

                if body['data'] is None:
                    return None

                response_data = body['data']

                if isinstance(response_data, list):
                    if not response_data:
                         return ResourceCollection(self, body.get('meta', {}), None, [])
                    collection_type = response_data[0].get('type')
                    resources = [self.create_model(**r) for r in response_data]
                    return ResourceCollection(self, body.get('meta', {}), collection_type, resources)
                elif isinstance(response_data, dict):
                    return self.create_model(**response_data)
                else:
                     print(f"Warning: Unexpected type for 'data' in response: {type(response_data)}")
                     return response_data

            except ValueError as e:
                raise ApiError(resp) from e
            except EmptyBodyException as e:
                 raise e

        elif status_code >= 400:
            if status_code in [401, 403]:
                raise AuthenticationError(resp)
            else:
                raise ApiError(resp)

        else:
            print(f"Warning: Received unexpected status code {status_code}. Response Body: {resp.text[:200]}")
            try:
                 resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                 raise ApiError(resp) from e
            return resp.text

def make_client(client_id, client_secret, root,
                mapper={}, admin=False, default_model=Resource,
                oauth_version=2, grant_type='client_credentials', scope=None,
                username=None, password=None, redirect_uri=None, auth_code=None,
                refresh_token_initial=None, fallback_to_legacy_auth=True):
    """
    Factory function to create and initialize an API client.

    Handles initial authentication and API root fetching.
    """
    c = Client(
       client_id=client_id,
       client_secret=client_secret,
       api_root=root,
       mapper=mapper,
       admin=admin,
       default_model=default_model,
       oauth_version=oauth_version,
       grant_type=grant_type,
       scope=scope,
       username=username,
       password=password,
       redirect_uri=redirect_uri,
       auth_code=auth_code,
       refresh_token_initial=refresh_token_initial,
       fallback_to_legacy_auth=fallback_to_legacy_auth
    )
    try:
        c.authenticate()
    except AuthenticationError as e:
        print(f"FATAL: Client initialization failed - Could not authenticate.")
        raise e

    try:
        c.api_root_response()
    except ApiError as e:
         print(f"Warning: Failed to fetch API root during client initialization: {e}")

    return c