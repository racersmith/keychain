from routing.router._route import sorted_routes
from routing.router import Route
from routing import router
from routing.router._matcher import get_match
from routing.router._navigate import get_nav_location
from routing.router._segments import Segment
from routing.router._utils import url_encode


# Global cache stores
_DATA = dict()  # Actual key: value cache store  {"account_123": "987"}
_FIELDS = set()  # What data fields are we looking for?  These are not the same as the store keys in _DATA ie. "account_{account_id}"
_GROUPS = dict()  # field: {key, ...} group of key sets associated with a particular field {"account_{account_id}": {"account_123", "account_456"}}


def evaluate_field(field: str, loader_args: dict):
    """Add the params to the field
    'account_{account_id}' -> 'account_123'
    """
    return field.format(**loader_args.get("params", dict()))


def clear_cache():
    """ Clear all cached data in keychain as well as routing """
    global _DATA
    global _GROUPS
    
    _DATA.clear()
    _GROUPS.clear()
    router.clear_cache()


def wildcard_path_params(path):
    """ Fill any parameters in the path with a wildcard """
    WILDCARD = "*"
    # remove leading dots
    segments = Segment.from_path(path)
    leading_dots = path.startswith(".")

    path = ""

    for segment in segments:
        if segment.is_static():
            path += "/" + url_encode(segment.value)
        elif segment.is_param():
            path += "/" + url_encode(WILDCARD)

    if leading_dots:
        # remove the leasing slash
        path = path[1:]

    return path


def get_match_from_path(path: str) -> Route:
    if path is None:
        # boring... 
        return None

    # Here we are filling any path params with a wildcard to expand our search when necessary and not require passing params
    generic_path = wildcard_path_params(path)

    # use as much of routing as possible to resolve a path
    location = get_nav_location(generic_path, path=None, query=None, params=None, hash=None)
    match = get_match(location)
    return match


def get_route_fields(route) -> set[str]:
    """ Get all fields assocated with a route """
    fields = set()
    if route is not None:
        for field_type in ["fields", "local_fields", "global_fields"]:
            fields.update(getattr(route, field_type, set()))
            
    return fields


def get_path_fields(path: str) -> set[str]:
    """ Get all fields assocated with a path """
    match = get_match_from_path(path)
    return get_route_fields(match.route)
    

def invalidate_specific(fields_or_keys: set[str]):
    """ remove cache data for specific fields and keys 
    when a field is given that includes params, we utilize the _GROUPS dict to find assocated keys to invalidate
    In this case this will also remove the _GROUP entry for the field.
    """
    global _DATA
    global _GROUPS

    # Look for specific chache keys
    for field_or_key in fields_or_keys:
        # Get resolved keys from groups and pop them or return just the base field
        for key in _GROUPS.pop(field_or_key, {field_or_key, }):
            # Remove cached data
            _DATA.pop(key, None)


def find_impacted_paths(fields_or_keys: set[str]) -> set[str]:
    """ Find the paths that contain the field or key """
    impacted_paths = set()
    for route in sorted_routes:
        if getattr(route, "path", None) is None:
            continue
            
        route_fields = get_route_fields(route)
        if route_fields.isdisjoint(fields_or_keys):
            impacted_paths.add(route.path)
    return impacted_paths


def ensure_set(a) -> set[str]:
    """ ensure that the argument is convereted into a set but does not split a string 
    Args:
        a: str | list[str] | set[str] | None

    Returns:
        set of strings
        'abc' -> {'abc', }
    """
    
    if a is None:
        return set()
        
    if isinstance(a, str):
        return {a, }

    else:
        return set(a)


def invalidate(
    field_or_key: str=None,
    *,
    path: str=None, 
    auto_invalidate_paths=True):
    """ Invalidate keychain fields and keys and routing cache for paths
    
    Args:
        field_or_key: str | list[str], keychain fields or keys to invalidate 'page_{page_number}' will invalidate all cached pages ie. 'page_1', 'page_3'...
        path: str | list[str], routing path to invalidate, this will invalidate the routing cache as well as keychain fields associated with the path
        auto_invalidate_paths: Automatically collect the paths that are impacted for the given fields and keys and invalidates the routing cache
    """
    fields_or_keys = ensure_set(field_or_key)

    for path in ensure_set(path):
        # add the path's fields to our invalidation list
        fields_or_keys.update(get_path_fields(path))
        router.invalidate(path=path, exact=False)

    invalidate_specific(fields_or_keys)
    
    if auto_invalidate_paths:
        # Find the paths that are impacted by field or key invalidation and invalidate the router cache for the paths
        impacted_paths = find_impacted_paths(fields_or_keys)

        # Invalidate here rather than adding these to the paths so we keep any cached data that could be preserved
        for path in impacted_paths:
            router.invalidate(path=path, exact=False)
            
    
    


def initialize_cache():
    """Find data fields that are reused between routes.
    Fields that are reused are automatically added to the global keychain cache
    """
    all_fields = set()
    reused_fields = set()

    for route in sorted_routes:
        if hasattr(route, "fields"):
            # include duplicate fields in global cache
            fields = route.fields
            repeats = set(fields).intersection(all_fields)
            reused_fields.update(repeats)
            all_fields.update(fields)

        if hasattr(route, "global_fields"):
            # include all fields in global cache
            reused_fields.update(route.global_fields)

    global _FIELDS
    _FIELDS = reused_fields


def _set(field: str, value, missing_value, loader_args):
    """ set global cache value """
    global _DATA
    global _GROUPS

    key = evaluate_field(field, loader_args)

    if (
        value is not missing_value
        and field in _FIELDS
        and key not in _DATA
    ):
        _DATA[key] = value
        if key != field:
            key_group = _GROUPS.get(field, set())
            key_group.add(key)
            _GROUPS[field] = key_group


def update(data: dict, missing_value, loader_args):
    """ Update our local global cache """
    for field, value in data.items():
       _set(field, value, missing_value, loader_args)


def _get(field: str, missing_value, loader_args) -> dict:
    """ Get cache value """
    key = evaluate_field(field, loader_args)
    return _DATA.get(key, missing_value)                


def load(fields, missing_value, loader_args):
    """ Get all requested cached data """
    found = dict()

    if fields and _DATA:
        for field in fields:
            value = _get(field, missing_value, loader_args)
            if value is not missing_value:
                found[field] = value
    return found
