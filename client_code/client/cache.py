from routing.router._route import sorted_routes

# Global cache stores
_DATA = dict()  # Actual key: value cache store  {"account_123": "987"}
_FIELDS = set()  # What data fields are we looking for?  These are not the same as the store keys in _DATA ie. "account_{account_id}"
_GROUPS = dict()  # field: {key, ...} group of key sets associated with a particular field {"account_{account_id}": {"account_123", "account_456"}}


def evaluate_field(field: str, loader_args: dict):
    """Add the params to the field
    'account_{account_id}' -> 'account_123'
    """
    return field.format(**loader_args["params"])


def clear_cache():
    global _DATA
    global _GROUPS
    
    _DATA.clear()
    _GROUPS.clear()


def invalidate(*fields_or_keys):
    global _DATA
    global _GROUPS
    
    for field_or_key in fields_or_keys:
        for key in _GROUPS.pop(field_or_key, {field_or_key, }):
            _DATA.pop(key, None)


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

