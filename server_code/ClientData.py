import anvil.server

import time

def get_form_1_data():
    return time.time()

def get_form_2_data():
    return time.time()

def get_form_3_data():
    return time.time()


FUNCTION_MAP = {
    "form_1": get_form_1_data,
    "form_2": get_form_2_data,
    "form_3": get_form_3_data,
}


@anvil.server.callable
def request(*args, **kwargs):
    print(f"Requesting data for {kwargs.keys()}")
    update = {key: FUNCTION_MAP[key]() for key in kwargs.keys() if key in FUNCTION_MAP}
    print(f"")
    return update
    