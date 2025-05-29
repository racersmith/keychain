import anvil.server
from functools import partial


REQUEST_MAP = dict()


def set_request_auth_fn(fn):
    global REQUEST_AUTH_FN
    REQUEST_AUTH_FN = fn


class Flatten:
    """Flatten the given data into the response"""
    def __init__(self, **data):
        self.data = data


def register_data_request(field: str | list, permission=None, quiet=False, missing_value=None):
    """Register a function for a data field"""
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
                return missing_value
            raise PermissionError("Access denied")

        for key in field:
            REQUEST_MAP[key] = partial(wrapper, func, permission, quiet)

        return wrapper

    return decorator


@anvil.server.callable
def _routing_auto_data_request(fields_requested: list, **loader_args):
    """Single point of access for all client data needs
    Easier to secure a single endpoint and allows for batched server calls
    """
    update = dict()
    for key in fields_requested:
        # Don't repeat a call if the data is already in update
        if key not in update:
            fn = REQUEST_MAP.get(key, None)
            if fn:
                value = fn(**loader_args)
                if isinstance(value, Flatten):
                    update.update(value.data)
                else:
                    update[key] = value

    invalid_keys = set(fields_requested) - update.keys()
    if invalid_keys:
        print(f"No matching function for keys: {list(invalid_keys)}")
    return update
