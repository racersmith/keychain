import anvil.server
from routing.router import Route, navigate, Redirect

from . import errors
from . import cache


def get_missing_fields(data: dict, missing_value) -> list:
    """Get the sub-dict that contains missing values"""
    return [field for field, value in data.items() if value == missing_value]


def key_list_to_dict(keys: list, missing_value):
    """Populate a dictionary with the given keys and fill with the missing value"""
    return dict.fromkeys(keys or list(), missing_value)


def strict_data(fields: list, data: dict, missing_value) -> dict:
    """Raise an error if any field is missing data"""
    missing_data_fields = list()
    for field in fields:
        if data.get(field, missing_value) == missing_value:
            missing_data_fields.append(field)

    if missing_data_fields:
        raise LookupError(f"unable to fetch all requested data: {missing_data_fields}")


def restrict_to_requested(fields: list, data: dict) -> dict:
    return {field: data[field] for field in fields}


def fetch_from_server(*fields, **loader_args) -> dict:
    return anvil.server.call_s("_keychain_data_request", fields, **loader_args)


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

    restrict_fields:
        bool, when true, only the fields that were requested will be returned.
        Otherwise, allow additional fields to be added

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
    restrict_fields = False
    missing_value = None
    permission_error_path = None

    def load_data(self, **loader_args) -> dict:
        return self._auto_load(**loader_args)

    def _auto_load(self, **loader_args):
        """Step through the resources to find the requested data fields
        1. Look for fields in loader_args['nav_context']
        2. Look for fields in global cache
        3. Finally, request the data from the server
        """

        fields = self._get_all_fields()
        data = key_list_to_dict(fields, self.missing_value)

        found_in_nav = self._load_from_nav_context(data, loader_args)
        print("found_in_nav", found_in_nav)
        data.update(found_in_nav)

        found_in_global = self._load_from_global_cache(data, loader_args)
        print("found_in_global", found_in_global)
        data.update(found_in_global)

        found_from_server = self._load_from_server(data, loader_args)
        print("found_from_server", found_from_server)
        data.update(found_from_server)

        # Update the global cache
        cache.update(data, self.missing_value, loader_args)

        if self.strict:
            strict_data(fields, data, self.missing_value)

        if self.restrict_fields:
            data = restrict_to_requested(fields, data)

        return self._apply_field_remap(data)

    def _get_output_keys(self) -> list:
        fields = self._get_all_fields()
        return [self.remap_fields.get(field, field) for field in fields]

    def _get_all_fields(self) -> list:
        return self.fields + self.global_fields + self.local_fields

    def _load_from_nav_context(self, data: dict, loader_args: dict) -> dict:
        """We expect that nav context will use the remapped key"""
        missing_keys = get_missing_fields(data, self.missing_value)
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
        missing_keys = get_missing_fields(data, self.missing_value)
        return cache.load(missing_keys, self.missing_value, loader_args)

    def _load_from_server(self, data: dict, loader_args: dict) -> dict:
        missing_keys = get_missing_fields(data, self.missing_value)
        found = dict()

        if missing_keys:
            try:
                found.update(fetch_from_server(*missing_keys, **loader_args))
            except errors.AccessDenied:
                navigate(
                    path=self.permission_error_path,
                    nav_context=loader_args["nav_context"],
                )
            except Redirect as r:
                return navigate(**r.__dict__, replace=True)

        return found

    def _apply_field_remap(self, data: dict):
        return {
            self.remap_fields.get(field, field): value for field, value in data.items()
        }
