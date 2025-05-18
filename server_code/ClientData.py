import anvil.server

import time


def get_form_1_data():
    return time.time()

def get_form_2_data():
    return time.time()

def get_form_3_data():
    return time.time()


REQUEST_MAP = {
    'form_1': get_form_1_data,
    "form_2": get_form_2_data,
    "form_3": get_form_3_data,
}


@anvil.server.callable
def request(*args, **kwargs):
    """ Single point of access for all client data needs
    Easier to secure a single endpoint and allows for batched server calls
    """
    
    print(f"Requesting data for {list(kwargs.keys())}")
    update = {key: REQUEST_MAP[key]() for key in kwargs.keys() if key in REQUEST_MAP}

    invalid_keys = kwargs.keys() - update.keys()
    if invalid_keys:
        print(f"No matching function for keys: {list(invalid_keys)}")
    return update
    