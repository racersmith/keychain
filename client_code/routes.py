from routing.router import Route, Redirect
import anvil.server

_GLOBAL_CACHE = dict()


def extract_missing(data: dict, missing_value=None):
    """Get the sub-dict that contains missing values"""
    return {key: missing_value for key, value in data.items() if value == missing_value}


def update_missing_from_dict(data: dict, update_from: dict, missing_value):
    """ Update the data dict without changing its keys """
    missing = extract_missing(data)
    if missing:
        missing = {
            key: update_from[key] for key in missing.keys() if key in update_from
        }
        data.update(missing)
    return data


def update_missing_from_global(data: dict, missing_value):
    """ Fill any missing data from global cache """
    return update_missing_from_dict(data, _GLOBAL_CACHE, missing_value)


def update_missing_from_request(data: dict, missing_value):
    """Request missing data from the server"""
    missing = extract_missing(data)
    if missing:
        data.update(anvil.server.call_s("request", **missing))
    return data


def fetch_data(
    loader_args: dict,
    local_data: list = None,
    global_data: list = None,
    strict: bool = True,
    missing_value=None,
):
    local_data = dict.fromkeys(local_data or list(), missing_value)
    global_data = dict.fromkeys(global_data or list(), missing_value)
    data = dict(**local_data, **global_data)

    data = update_missing_from_dict(data, loader_args["nav_context"], missing_value)
    data = update_missing_from_global(data, missing_value)
    data = update_missing_from_request(data, missing_value)

    # Store the requested global data
    _GLOBAL_CACHE.update(update_missing_from_dict(global_data, data, missing_value))

    if strict:
        # Strictly enforce that all data must be filled
        missing = extract_missing(data, missing_value)
        if missing:
            raise ValueError(
                f"unable to fetch all requested data: {list(missing.keys())}"
            )

    return data


class HomeRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path="/1")


class Form1Route(Route):
    path = "/1"
    form = "Pages.Form1"
    cache_data = True

    def load_data(self, **loader_args):
        return fetch_data(loader_args, local_data=["form_1"], global_data=["form_3"])


class Form2Route(Route):
    path = "/2"
    form = "Pages.Form2"
    cache_data = True

    def load_data(self, **loader_args):
        return fetch_data(loader_args, local_data=["form_2"])


class Form3Route(Route):
    path = "/3"
    form = "Pages.Form3"
    cache_data = True

    def load_data(self, **loader_args):
        return fetch_data(loader_args, local_data=["form_3"])
