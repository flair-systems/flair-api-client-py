Flair API Client (Python) [![Build Status](https://travis-ci.org/flair-systems/flair-api-client-py.svg?branch=master)](https://travis-ci.org/flair-systems/flair-api-client-py)
=========

This package provides a very simple API client for the [Flair API](https://api.flair.co/). Since the Flair API uses the [JSON-API](https://jsonapi.org) standard, this client is just a very thin wrapper around a JSON API client, but provides hooks for a extending it with custom models.

## Installation

Eventually this will be released on PyPi, for now you'll need to install via github

```
pip install git+git://github.com/flair-systems/flair-api-client-py.git
```

This package depdends on [requests](http://docs.python-requests.org/en/master/), and requires Python 3.5 or greater.

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
room.update(attributes={'name': 'Master Bedroom'}, relationships={structure=structures[0], vents=vents})

# create a vent
vent = c.create('vents', attributes={'name': 'North Vent'}, relationships={room=room})

# Add a vent to a room
room.add_rel(vents=vent)

# Update vent relationship for a room
room.update_rel(vents=[vent])

# Delete a vent relationship for a room
room.delete_rel(vents=vent)
```

### Authorization

At the moment, this package only supports authenticating to the Flair API using a client credentials request. This will give access to resources owned by the user to whom the credentials were issued. Support for other OAuth flow will be coming in future releases.

### Extension

If, instead of having requests initialize or update the default Resource object, you'd like to use your own classes you can initialize the client with a mapper:

```python
from flair_api import make_client, Resource

class User(Resource):
    def __init__(*args, **kwargs):
        self.__super__.init(*args, **kwargs)
        
    def __str__(self):
        return "User: " + self.attributes['name']
        
client = make_client(client_id, client_secret, 'https://api.flair.co/', mapper={'users': User})

users = client.get('users')

for user in users:
    print(user)  # "User: Edward", "User: Kenny", "User: Danimal"
```

## Contributing

Contributions are welcome by anyone. You'll just need to sign our [Contributor License Agreement]().

## License

Copyright 2016 by Standard Euler, Inc

Licensed under the [GNU Public License 3.0](http://www.gnu.org/licenses/gpl-3.0.en.html). See LICENSE.
