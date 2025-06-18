from routing.router._route import sorted_routes
from routing.router import Route
from routing import router

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
    global _DATA
    global _GROUPS
    
    _DATA.clear()
    _GROUPS.clear()


def get_route_from_path(path: str) -> Route:
    if path is None:
        return None

    for route in sorted_routes:
        if hasattr(route, "path") and route.path == path:
            return route

    return None


def get_route_fields(route) -> set[str]:
    fields = set()
    if route is not None:
        for field_type in ["fields", "local_fields", "global_fields"]:
            fields.update(getattr(route, field_type, set()))
            
    return fields


def get_path_fields(path: str) -> set[str]:
    route = get_route_from_path(path)
    return get_route_fields(route)
    

def _invalidate_specific(fields_or_keys: set[str]):
    global _DATA
    global _GROUPS

    # Look for specific chache keys
    for field_or_key in fields_or_keys:
        # Get resolved keys from groups and pop them or return just the base field
        for key in _GROUPS.pop(field_or_key, {field_or_key, }):
            # Remove cached data
            _DATA.pop(key, None)


def _find_impacted_paths(fields_or_keys: set[str]) -> set[str]:
    impacted_paths = set()
    for route in sorted_routes:
        route_fields = get_route_fields(route)
        if hasattr(route, "path") and not route_fields.isdisjoint(fields_or_keys):
            impacted_paths.add(route.path)
    return impacted_paths


def ensure_set(a: str | list[str] | set[str] | None) -> set[str]:
    if a is None:
        return set()
        
    if isinstance(a, str):
        return {a, }

    else:
        return set(a)


def invalidate(fields: str | list[str] = None, keys: str | list[str]=None, paths: str | list[str]=None, auto_path=False):
    """ Invalidate keychain fields and keys and routing cache for paths
    Args:
        fields: keychain fields to invalidate 'page_{page_number}' will invalidate all cached pages ie. 'page_1', 'page_3'...
        keys: keychain keys to invalidate ie., 'page_2'
        paths: routing path to invalidate, this will invalidate the routing cache as well as keychain fields associated with the path
        auto_path: Automatically collect the paths that are impacted for the given fields and keys and invalidates the routing cache
    
    """
    fields_or_keys = set()
    fields_or_keys.update(ensure_set(fields))
    fields_or_keys.update(ensure_set(keys))
    paths = ensure_set(paths)

    if auto_path:
        # Find the paths that are impacted by field or key invalidation and invalidate the router cache for the paths
        impacted_paths = _find_impacted_paths(fields_or_keys)
        # Invalidate here so we 
        for path in impacted_paths:
            router.invalidate(path=path)
    
    for path in ensure_set(paths):
        fields_or_keys.update(get_path_fields(path))
        router.invalidate(path=path)
    
    _invalidate_specific(fields_or_keys)


def initialize_cache():
    """Find data fields that are reused between routes."""
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
    key = evaluate_field(field, loader_args)
    return _DATA.get(key, missing_value)                


def load(fields, missing_value, loader_args):
    found = dict()

    if fields and _DATA:
        for field in fields:
            value = _get(field, missing_value, loader_args)
            if value is not missing_value:
                found[field] = value
    return found

