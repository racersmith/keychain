import anvil.server

import time


REQUEST_MAP = {
    # 'form_1': get_form_1_data,
    # "form_2": get_form_2_data,
    # "form_3": get_form_3_data,
    # "context": get_context_data,
}


def register_data_request(field: str, permission_fn=None):
    global REQUEST_MAP
    def wrapper(func):
        if field in REQUEST_MAP:
            raise ValueError(f"'{field}' already has a registred function")
        REQUEST_MAP[field] = func
        return func
    return wrapper

def register_data_request(field: str, permission_fn=None):
    def decorator(func):
        if field in REQUEST_MAP:
            raise ValueError(f"'{field}' already has a registred function")
        REQUEST_MAP[field] = func
        
        def wrapper(*args, **kwargs):
            if permission_fn():
                return func(*args, **kwargs)
            else:
                raise PermissionError()
        return wrapper
    return decorator

@register_data_request(field='form_1')
def get_form_1_data(*args, **loader_args):
    return time.time()

@register_data_request(field='form_2')
def get_form_2_data(*args, **loader_args):
    return time.time()

@register_data_request(field='form_3')
def get_form_3_data(*args, **loader_args):
    return time.time()

@register_data_request(field='context')
def get_context_data(*args, **loader_args):
    return loader_args


@anvil.server.callable
def request(data_request: dict, **loader_args):
    """ Single point of access for all client data needs
    Easier to secure a single endpoint and allows for batched server calls
    """
        
    print(f"Requesting data for {list(data_request.keys())}")
    update = {key: REQUEST_MAP[key](**loader_args) for key in data_request.keys() if key in REQUEST_MAP}

    invalid_keys = data_request.keys() - update.keys()
    if invalid_keys:
        print(f"No matching function for keys: {list(invalid_keys)}")
    return update
    