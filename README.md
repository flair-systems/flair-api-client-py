Flair API Client (Python) [![Build Status](https://travis-ci.org/flair-systems/flair-api-client-py.svg?branch=master)](https://travis-ci.org/flair-systems/flair-api-client-py)
=========

This package provides a very simple API client for the [Flair API](https://api.flair.co/). Since the Flair API uses the [JSON-API](https://jsonapi.org) standard, this client is just a very thin wrapper around a JSON API client, but provides hooks for a extending it with custom models.

## Installation

Eventually this will be released on PyPi, for now you'll need to install via github

```
pip install git+https://github.com/flair-systems/flair-api-client-py.git
```

This package depends on [requests](http://docs.python-requests.org/en/master/), and requires Python 3.8 or greater.

## Usage

```python
from flair_client import make_client
client = make_client(
    client_id=client_id,
    client_secret=client_secret,
    root='https://api.flair.co/',
    user_agent='MyProject/1.0.0'
)

# retrieve a list of structures available to this account
structures = client.get('structures')

# get a single room by room's id
room = client.get('rooms', id="1")

# fetch vents in a room
vents = room.get_rel('vents')

# delete a room
room.delete()

# update a room
room.update(attributes={'name': 'Master Bedroom'}, relationships=dict(structure=structures[0], vents=vents))

# create a vent
vent = c.create('vents', attributes={'name': 'North Vent'}, relationships=dict(room=room))

# Add a vent to a room
room.add_rel(vents=vent)

# Update vent relationship for a room
room.update_rel(vents=[vent])

# Delete a vent relationship for a room
room.delete_rel(vents=vent)
```

### Authorization

To authenticate with the Flair API, you'll need to open the Flair App and create or find your OAuth 2.0 credentials in Account Settings (near the bottom under Developer Settings). This project supports two authentication modes:

- **OAuth 2.0 (v2)**: The modern authentication method using the `/oauth2/token` endpoint. Supports refresh tokens for persistent access.
- **OAuth 2.0 (V1 / legacy)**: The original authentication method using the `/oauth/token` endpoint. Does not support refresh tokens.

The client automatically handles token expiration and will re-authenticate as needed. For OAuth 2.0 (v2) with refresh tokens, the client will use the refresh token to obtain new access tokens when they expire. For persistent access across script restarts, store the refresh token and reuse it by passing it to the `refresh_token_initial` parameter when creating a new client instance.

**Obtaining a refresh token**: Refresh tokens are obtained during the initial OAuth 2.0 authentication flow. Once you have a refresh token from your first successful authentication, store it and reuse it in subsequent runs.

**Rate limiting**: Access token creation is rate-limited (approximately 50 requests/day). Reusing refresh tokens avoids hitting this limit since refresh operations don't count toward it. Limits are subject to change.

For secure storage of refresh tokens, use a JSON file with restricted permissions:

```python
import json
# Use the preferred backward-compatible import
from flair_client import make_client

# Load refresh token from file
try:
    with open('refresh_token.json', 'r') as f:
        refresh_token = json.load(f)['refresh_token']
except (FileNotFoundError, KeyError):
    refresh_token = None

client = make_client(
    client_id='your_client_id',
    client_secret='your_client_secret',
    root='https://api.flair.co/',
    refresh_token_initial=refresh_token,  # Reuse existing refresh token
    user_agent='MyProject/1.0.0'  # Specify your project name and version
)

# When the client gets a new refresh token, store it for future use
if refresh_token != client.refresh_token:
    with open('refresh_token.json', 'w') as f:
        json.dump({'refresh_token': client.refresh_token}, f)
    refresh_token = client.refresh_token
```

**Security Note**: Never share your refresh tokens. Store them securely and restrict file permissions (e.g., `chmod 600 refresh_token.json`) when using file-based storage.

### User-Agent (optional)

Specifying a custom User-Agent header helps relate requests from your application in API logs and provide better support. The recommended format is:

```
ProjectName/Version (Language)
```

Examples:
- `'MyProject/1.0.0 (Python)'` - for a Python application
- `'MyMobileApp/2.5.0 (Python/asyncio)'` - for an async Python app
- `'DataPipeline/0.1.0'` - minimal format without language info

The `(Language)` portion is optional but recommended, as it helps the API team understand the context of your requests.

### Extension

If you want to use custom classes instead of the default `Resource` object, you can initialize the client with a `mapper` dictionary that maps resource types to your custom classes. Custom classes must inherit from `Resource` and call `super().__init__()` with the required parameters.

```python
# Use the preferred backward-compatible import
from flair_client import make_client, Resource

# Alternative direct import
# from flair_api import make_client, Resource

class User(Resource):
    def __init__(self, client, id_, type_, attributes, relationships):
        super().__init__(client, id_, type_, attributes, relationships)

    def __str__(self):
        return f"User: {self.attributes.get('name', 'Unknown')}"

client = make_client(client_id, client_secret, 'https://api.flair.co/', mapper={'users': User})

users = client.get('users')

for user in users:
    print(user)  # "User: Edward", "User: Kenny", "User: Danimal"
```

## Contributing

Contributions are welcome by anyone. To get started, [sign the Contributor License Agreement](https://www.clahub.com/agreements/flair-systems/flair-api-client-py).

## License

Copyright 2016-2025 by Standard Euler, Inc

Licensed under the [Apache Public License 2.0](http://www.apache.org/licenses/LICENSE-2.0). See LICENSE.
