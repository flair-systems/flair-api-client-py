Flair API Client (Python) [![Build Status](https://travis-ci.org/flair-systems/flair-api-client-py.svg?branch=master)](https://travis-ci.org/flair-systems/flair-api-client-py)
=========

This package provides a very simple API client for the [Flair API](https://api.flair.co/). Since the Flair API uses the [JSON-API](https://jsonapi.org) standard, this client is just a very thin wrapper around a JSON API client, but provides hooks for a extending it with custom models.

## Installation

Eventually this will be released on PyPi, for now you'll need to install via github

```
pip install git+https://github.com/flair-systems/flair-api-client-py.git
```

This package depends on [requests](http://docs.python-requests.org/en/master/), and requires Python 3.5 or greater.

## Usage

```python
from flair_api import make_client

client = make_client(client_id, client_secret, 'https://api.flair.co/')

# retrieve a list of structures available to this account
structures = client.get('structures')

# get a single room by id
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

To authenticate with the Flair API, you'll need to open the Flair App and create or find your OAuth 2.0 credentials in Account Settings (near the bottom under Developer Settings). This package supports authenticating using these client credentials, as well as the original OAuth 1.0 (legacy) credentials, which will provide access to resources granted to that user.

### Extension

If you want to use custom classes instead of the default `Resource` object, you can initialize the client with a `mapper` dictionary that maps resource types to your custom classes. Custom classes must inherit from `Resource` and call `super().__init__()` with the required parameters.

```python
from flair_api import make_client, Resource

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
