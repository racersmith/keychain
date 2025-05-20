from .DataFinder import register_data_request, Flatten

import time


def admin_check():
    # just for demo's sake something to validate the user request
    return False


@register_data_request(field=[f"the answer to {x}" for x in ["everything", "life", "the universe"]])
def get_the_answer(*args, **loader_args):
    print('get_the_answer', loader_args['params'])
    return 42


@register_data_request(field="what is the question", permission=admin_check, quiet=False)
def get_the_question(*args, **loader_args):
    # raise LookupError('The question remains unknown')
    print('get_the_question', loader_args['params'])
    raise LookupError("The question remains unknown.")


@register_data_request(field=["account", "name", "email", "phone"])
def get_account_data(*args, **loader_args):
    """Allow multiple fields to resolve to the same function for use cases like this.
    Here I'm using the Flatten marker that will then be flattened in the data reponse.
    This might be a complication that without much benefit.
    This could be interesting if we namespaced keys...
    ie.
        'account' -> {'name': name, 'email': email, 'phone': phone}
        'account.email' -> email
    """
    print('get_account_data', loader_args['params'])
    return Flatten(name="Arther", email="arther@galaxyguides.com", phone="987-654-3210")


@register_data_request(field="first_load")
def get_time(*args, **loader_args):
    print('get_time', loader_args['params'])
    return time.time()


@register_data_request(field="something_private", permission=admin_check, quiet=True)
def get_private_data(*args, **loader_args):
    print('get_private_data', loader_args['params'])
    return "Private Data from server"


@register_data_request(field="something_secret", permission=admin_check, quiet=False)
def get_secret_data(*args, **loader_args):
    print('get_secret_data', loader_args['params'])
    return "Secret Data from server"


@register_data_request(field=["private_value", "private_{private_id}"])
def get_private_value(*args, **loader_args):
    print('get_private_value', loader_args['params'])
    return f"Private Value:{3 * str(loader_args['params'].get('private_id'))}"
