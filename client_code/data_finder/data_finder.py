import anvil.server

from routing.router import _route


MISSING_VALUE = None

def find_global_fields(missing_value=None):
    all_fields = set()
    reused_fields = set()
    
    for route in _route.sorted_routes:
        if hasattr(route, "required_fields"):
            reused_fields.update(route.required_fields.union(all_fields))
            all_fields.update(route.required_fields)

    return dict.fromkeys(reused_fields, missing_value)

global _GLOBAL_CACHE 
_GLOBAL_CACHE = find_global_fields(MISSING_VALUE)


def extract_missing(data: dict, missing_value=None):
    """Get the sub-dict that contains missing values"""
    return {key: missing_value for key, value in data.items() if value == missing_value}


def update_missing_from_dict(data: dict, update_from: dict, missing_value):
    """Update the data dict without changing its keys"""
    missing = extract_missing(data)
    if missing:
        missing = {
            key: update_from[key] for key in missing.keys() if key in update_from
        }
        data.update(missing)
    return data


def update_missing_from_global(data: dict, missing_value):
    """Fill any missing data from global cache"""
    return update_missing_from_dict(data, _GLOBAL_CACHE, missing_value)


def update_missing_from_request(data: dict, missing_value):
    """Request missing data from the server"""
    missing = extract_missing(data)
    if missing:
        data.update(anvil.server.call_s("request", **missing))
    return data


def key_list_to_dict(keys: list, missing_value):
    """Populate a dictionary with the given keys and fill with the missing value"""
    return dict.fromkeys(keys or list(), missing_value)


def fetch(
    loader_args: dict,
    local_data: list = None,
    global_data: list = None,
    strict: bool = True,
    missing_value=None,
):
    local_data = key_list_to_dict(local_data, missing_value)
    global_data = key_list_to_dict(global_data, missing_value)
    data = dict(**local_data, **global_data)

    data = update_missing_from_dict(data, loader_args["nav_context"], missing_value)
    data = update_missing_from_global(data, missing_value)
    data = update_missing_from_request(data, missing_value)

    # Store the requested global data
    _GLOBAL_CACHE = update_missing_from_dict(_GLOBAL_CACHE, data, missing_value)
    _GLOBAL_CACHE.update(update_missing_from_dict(global_data, data, missing_value))

    if strict:
        # Strictly enforce that all data must be filled
        missing = extract_missing(data, missing_value)
        if missing:
            raise ValueError(
                f"unable to fetch all requested data: {list(missing.keys())}"
            )

    return data
