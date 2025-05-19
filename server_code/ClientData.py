import anvil.server

import time


def get_form_1_data(*args, **loader_args):
    return time.time()

def get_form_2_data(*args, **loader_args):
    return time.time()

def get_form_3_data(*args, **loader_args):
    return time.time()


def get_context_data(*args, **loader_args):
    return loader_args


REQUEST_MAP = {
    'form_1': get_form_1_data,
    "form_2": get_form_2_data,
    "form_3": get_form_3_data,
    "context": get_context_data,
}


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
    