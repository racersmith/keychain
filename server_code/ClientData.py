import anvil.server
from functools import partial
import time


""" This would be part of routing """
REQUEST_MAP = dict()
MISSING_VALUE = None


class Flatten:
    """ Flatten the given data into the response """
    def __init__(self, **data):
        self.data = data


def register_data_request(field: str|list, permission=None, quiet=False):
    """ Register a function for a data field """
    # Register new fields or raise an error if we are trying to write over an existing
    if isinstance(field, str):
        field = [field]
        
    for key in field:
        if key in REQUEST_MAP:
            raise ValueError(f"'{key}' already has a registred function")
                
    def decorator(func):
        def wrapper(func, permission, quiet, *args, **kwargs):
            # Check our permission status
            if permission is None or permission():
                return func(*args, **kwargs)

            # We don't have permission
            if quiet:
                # Quietly return just None
                return MISSING_VALUE
            raise PermissionError("Access denied")


        for key in field:
            REQUEST_MAP[key] = partial(wrapper, func, permission, quiet)
        
        return wrapper
        
    return decorator


@anvil.server.callable
def request(data_request: dict, **loader_args):
    """ Single point of access for all client data needs
    Easier to secure a single endpoint and allows for batched server calls
    """
    update = dict()
    for key in data_request.keys():
        value = REQUEST_MAP[key](**loader_args)
        if isinstance(value, Flatten):
            update.update(value.data)
        else:
            update[key] = value
    

    invalid_keys = data_request.keys() - update.keys()
    if invalid_keys:
        print(f"No matching function for keys: {list(invalid_keys)}")
    return update


""" This would be user implemented """

def admin_check():
    # just for demo's sake something to validate the user request
    return False

@register_data_request(field=["the answer to everything", "the answer to the life", "the answer to the universe"])
def get_the_answer(*args, **loader_args):
    return 42

@register_data_request(field='what is the question', permission=admin_check, quiet=False)
def get_the_question(*args, **loader_args):
    # raise LookupError('The question remains unknown')
    raise LookupError("The question remains unknown.")

@register_data_request(field=['account', 'name', 'email', 'phone'])
def get_account_data(*args, **loader_args):
    """ Allow multiple fields to resolve to the same function for use cases like this.
    Here I'm using the Flatten marker that will then be flattened in the data reponse.
    This might be a complication that without much benefit.
    This could be interesting if we namespaced keys...
    ie.
        'account' -> {'name': name, 'email': email, 'phone': phone}
        'account.email' -> email
    """
    return Flatten(name='Arther', email='arther@galaxyguides.com', phone='987-654-3210')

@register_data_request(field='first_load')
def get_time(*args, **loader_args):
    return time.time()

@register_data_request(field='something_private', permission=admin_check, quiet=True)
def get_private_data(*args, **loader_args):
    return "Private Data from server"

@register_data_request(field='something_secret', permission=admin_check, quiet=False)
def get_secret_data(*args, **loader_args):
    return "Secret Data from server"

@register_data_request(field='private_value')
def get_private_value(*args, **loader_args):
    return f"Private Value:{3*str(loader_args['params'].get('private_id'))}"
