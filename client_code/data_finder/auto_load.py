import anvil.server
from routing.router import _route, Route


_GLOBAL_KEYS = set()
_GLOBAL_CACHE = dict()


def find_global_fields():
    """Find data fields that are reused between routes."""
    all_fields = set()
    reused_fields = set()

    for route in _route.sorted_routes:
        if hasattr(route, "fields"):
            # include duplicate fields in global cache
            fields = route.fields
            repeats = set(fields).intersection(all_fields)
            reused_fields.update(repeats)
            all_fields.update(fields)

        if hasattr(route, "global_fields"):
            # include all fields in global cache
            global_fields = route.global_fields
            reused_fields.update(global_fields)

    global _GLOBAL_KEYS
    _GLOBAL_KEYS = reused_fields


def get_missing_keys(data: dict, missing_value) -> list:
    """Get the sub-dict that contains missing values"""
    return [key for key, value in data.items() if value == missing_value]


def evaluate_field(field: str, loader_args: dict):
    """Add the params to the field
    'account_{account_id}' -> 'account_1234'
    """
    return field.format(**loader_args["params"])


def update_global(data: dict, loader_args: dict, missing_value):
    global _GLOBAL_CACHE

    for field, value in data.items():
        key = evaluate_field(field, loader_args)
        if (
            value is not missing_value
            and field in _GLOBAL_KEYS
            and key not in _GLOBAL_CACHE
        ):
            _GLOBAL_CACHE[key] = value


def key_list_to_dict(keys: list, missing_value):
    """Populate a dictionary with the given keys and fill with the missing value"""
    return dict.fromkeys(keys or list(), missing_value)


def strict_data(fields: list, data: dict, missing_value) -> dict:
    # Strictly enforce that all data must be filled
    missing_keys = get_missing_keys(data, missing_value)
    if missing_keys:
        raise LookupError(f"unable to fetch all requested data: {missing_keys}")

    # Only return keys that were explicitly asked for
    return {key: data[key] for key in fields}


class AutoLoad(Route):
    """Automatically load data from required_fields

    fields:
        list of keys that should can be automatically added to global cache if duplicated across routes

    global_fields:
        list of keys that will be included in global cache

    local_fields:
        list of keys that will only be used locallaly and will be excluded from global cache

    remap_fields:
        dict that remaps the caching key for the output data
        uses for cases with param populated fields.

        example without:
            field = ['account_{account_id}']
            load_data() -> {'account_{account_id}': {'name': 'Arthur'}}

        example without:
            field = ['account_{account_id}']
            remap_fields = {'account_{account_id}': 'account'}

            load_data() -> {'account': {'name': 'Arthur'}}

    strict:
        bool, should we raise an error if there are values that can not be found or just fill them with None
        strict will also limit the return keys to strictly those listed in required_fields.

    missing_value:
        What should be used to indicate a missing value. Searching continues until the value is found.
        When the value could not be found, the missing value will be given unless flagged strict

    """

    cache_data = True

    fields = list()
    global_fields = list()
    local_fields = list()

    remap_fields = dict()

    strict = True
    missing_value = None

    def load_data(self, **loader_args) -> dict:
        return self._auto_load(**loader_args)

    def _auto_load(self, **loader_args):
        """Step through the resources to find the requested data fields
            1. Look for fields in loader_args['nav_context']
            2. Look for fields in global cache
            3. Finally, request the data from the server
        """
        print("Auto Load")
        print("loader_args")
        import json
        print(json.dumps(loader_args, indent=4))
        
        fields = self._get_all_fields()
        data = key_list_to_dict(fields, self.missing_value)

        found_in_nav = self._load_from_nav_context(data, loader_args)
        # print("found_in_nav", found_in_nav)
        data.update(found_in_nav)

        found_in_global = self._load_from_global_cache(data, loader_args)
        # print("found_in_global", found_in_global)
        data.update(found_in_global)

        found_from_server = self._load_from_server(data, loader_args)
        # print("found_from_server", found_from_server)
        data.update(found_from_server)

        # Update the global cache
        update_global(data, loader_args, self.missing_value)

        if self.strict:
            strict_data(fields, data, self.missing_value)

        return self._apply_field_remap(data)

    def _get_all_fields(self):
        return self.fields + self.global_fields + self.local_fields

    def _load_from_nav_context(self, data: dict, loader_args: dict) -> dict:
        """We expect that nav context will use the remapped key"""
        missing_keys = get_missing_keys(data, self.missing_value)
        found = dict()

        if missing_keys and loader_args.get("nav_context", False):
            nav_context = loader_args["nav_context"]
            for field in data.keys():
                # look in nav_context using key: account not the field: account_{id}
                key = self.remap_fields.get(field, field)

                # store the value using the field
                value = nav_context.get(key, self.missing_value)
                if value is not self.missing_value:
                    found[field] = value
        return found

    def _load_from_global_cache(self, data: dict, loader_args: dict) -> dict:
        missing_keys = get_missing_keys(data, self.missing_value)
        found = dict()

        if missing_keys and _GLOBAL_CACHE:
            for field in data.keys():
                # look in global cache using param populated key: account_123 not the field: account_{id}
                key = evaluate_field(field, loader_args)
                print(key)

                # store the value using the field
                value = _GLOBAL_CACHE.get(key, self.missing_value)
                if value is not self.missing_value:
                    found[field] = value
        return found

    def _load_from_server(self, data: dict, loader_args: dict) -> dict:
        missing_keys = get_missing_keys(data, self.missing_value)
        found = dict()

        if missing_keys:
            found.update(anvil.server.call_s("request", missing_keys, **loader_args))
        return found

    def _apply_field_remap(self, data):
        return {
            self.remap_fields.get(field, field): value for field, value in data.items()
        }
