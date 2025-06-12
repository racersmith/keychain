<p align="center">
<img src="theme/assets/keychain.png" width="256">
</p>

# Keychain
The idea of keychain is to simplify the access to data in an Anvil App that is using
[routing](https://github.com/anvil-works/routing) by using data keys that are consistent between
page, client and server.  Keychain automatically fetches any cached data on the client side then requests any missing
data from the server in a single round-trip server call.

## What does Keychain do?
Keychain takes the common usage of data binding from a form's item attribute ie. `self.item['name']` and extends this
to defining what data a form requires, caching, and retriving missing data from the server. The data key `name` in this 
example, is data definition throughout these places.

Keychain automatically finds the data from `loader_args['nav_context']`, keyring's client cache, and finally, requesting
from the server.

When requesting data from the server, the page retrieves all missing data in a single server call reducing load time.
However, on the server side, data is not defined in a single server function, and the user is free to reduce each 
function to the smallest realistic return scope.  Keychain, automatically compiles the necessary server functions to 
return the requested data keys to the client.

Keychain allows data permission to be defined at the key level and allows for redirections if a client tries to access
data without the necessary permissions.

## Example

### client/routes.py
``` python
from routing.router import Route, Redirect
from keychain.client import AutoLoad, initialize_cache


class HomeRoute(AutoLoad):
    path = "/home"
    form = "Pages.Home"
    fields = ["first_load", "the answer to everything"]
    strict = False


class AccountRoute(AutoLoad):
    path = "/account"
    form = "Pages.Account"
    strict = False
    fields = ["first_load", "the answer to life", "name", "email"]
```

Here we define what data `fields` are required for each page.  Notice that `"first_load"` is reused between pages.
Keychain will automatically cache the reused field for reuse between the pages.

### server/client_data.py
``` python
import anvil.server
import anvil.user
from keychain.server import register_data_request, Flatten

import time


def admin_check():
    user = anvil.users.get_user()
    return user['role'] == 'admin'


@register_data_request(
    field=[f"the answer to {x}" for x in ["everything", "life", "the universe"]],
    permission=admin_check
)
def get_the_answer(*args, **loader_args):
    print("get_the_answer", loader_args["params"])
    return 42


@register_data_request(field=["name", "email", "phone"])
def get_account_data(*args, **loader_args):
    """Allow multiple fields to resolve to the same function for use cases like this.
    Here I'm using the Flatten marker that will then be flattened in the data reponse.
    This might be a complication that without much benefit.
    This could be interesting if we namespaced keys...
    ie.
        'account' -> {'name': name, 'email': email, 'phone': phone}
        'account.email' -> email
    """
    print("get_account_data", loader_args.get("params", None))
    return Flatten(name="Arther", email="arther@galaxyguides.com", phone="987-654-3210")


@register_data_request(field=["first_load", "server_time"])
def get_time(*args, **loader_args):
    print("get_time", loader_args.get("params", None))
    return time.time()
```

Each of the fields pages are requesting should have a matching function on the server.  These functions are registered
by adding `@register_data_request` decorator.  Adding a `permission` to the registration forces a function call before
the data is accessed.

The server functions will have the data applied to the key that is requested. So, in this case, `"first_load"` was
the request field and the resulting dict key not `"server_time"`.

`Flatten` allows you to update the request dict rather than adding a sub dict.  This behavior can be seen in the 
`get_account` function. Requesting `"account"` without Flatten would result in:
``` python
{
    "account": {
        "name": "Arther",
        "email": "arther@galaxyguides.com", 
        "phone": "987-654-3210"
    }
}
```

with Flatten the result is not nested under `"account"`
``` python
{
    "name": "Arther",
    "email": "arther@galaxyguides.com", 
    "phone": "987-654-3210"
}
```


### /client/Pages.Home
``` python 
from ._anvil_designer import HomeTemplate
from routing import router


class Home(HomeTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        properties["item"] = routing_context.data
        self.init_components(**properties)
```

Using the standard `routing` form boilerplate means that you will have a `self.item` that has a dict with keys that
align with the defined routes `fields`.

Now, with the fields the page requires and the function on the server registered, all required data will be available 
to the form in the routing_context.data as a dict.

``` python
self.item = {
    "first_load": 123456789, 
    "the answer to everything": 42,
}
```

## Demo App
Checkout the demo app for Keychain:

[Clone in Anvil without keychain clone](https://anvil.works/build#clone:UKCRS4JSFMPBJBAX=GJHMGQFWRORN55FSMRCJRMV6)

[Clone in Anvil with keychain clone](https://anvil.works/build#clone:UKCRS4JSFMPBJBAX=GJHMGQFWRORN55FSMRCJRMV6|UESVUJKDGQULTT5M=EZQCPFBV2DT3TRODVQX3CG7Z)

## Using
[Clone Keychain](https://anvil.works/build#clone:UESVUJKDGQULTT5M=EZQCPFBV2DT3TRODVQX3CG7Z)

App ID: `UESVUJKDGQULTT5M` 

## Fields vs. Keys
I make a distinction between the two because of an additional feature within Keychain. Conceptually, `keys` are used 
for storage and retrieval and `fields` are key templates. In most cases, these are the same.  The examples presented so 
far do not have any difference between the `field` and the `key`

However, if we wanted the ability to retrieve and cache data that is associated with some `id` this is where the 
distinction becomes useful.

Let's say we have some `"private"` field that is associated with a `private_id=1234`.  We need to be able to request
`("private", 1234)` and we also need to store a unique instance of `"private"` for this `private_id`.  
Using `fields` you would define the `field` as `"private_{private_id}"`.  The field is now generic to the route, 
but the data can be retrieved and cached using your defined `key` which in this case `"private_1234"`. 
The attributes are automatically filled from 
`loader_args["params"]`.  To get the `key` from the `field`, Keychain does a simple string formatting: 
`key = field.format(**loader_args["params"])`
So, any number of `params` can be used to create a unique `key` for storage and retrieval. 

``` python
# client/routes.py
class PrivateIdRoute(AutoLoad):
    path = "/private/:private_id"
    form = "Pages.Private"
 
    fields = ["private_{private_id}"]
```

Here we use the `path`'s `private_id` within the `field`.  Now, there is a slight annoyance with this.  The `self.item`
would have the key `"private_{private_id}"`.  When using `nav_context` to send data during navigation you would also 
need to use this key.  However, you can remap keys to simplify this case:

``` python
# client/routes.py
class PrivateIdRoute(AutoLoad):
    path = "/private/:private_id"
    form = "Pages.Private"
   
    global_fields = ["private_{private_id}"]
    remap_fields = {
        "private_{private_id}": "private",
    }
```

Server functions are registered using the `field="private_{private_id}"` and you have access to `loader_args`.
``` python
# server/client_data.py
@register_data_request(field="private_{private_id}")
def get_private_value(*args, **loader_args):
    return f"Private Value:{3 * str(loader_args['params'].get('private_id'))}"
```
