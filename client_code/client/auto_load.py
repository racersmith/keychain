import anvil.server
from routing.router import Route, navigate

from . import errors
from . import cache
from . import utils


def strict_data(fields: list, data: dict, missing_value):
    """Raise an error if any field is missing data"""
    missing_data_fields = list()
    for field in fields:
        if data.get(field, missing_value) == missing_value:
            missing_data_fields.append(field)

    if missing_data_fields:
        raise LookupError(f"unable to fetch all requested data: {missing_data_fields}")


def restrict_to_requested(fields: list, data: dict) -> dict:
    return {field: data[field] for field in fields}


def load_from_nav_context(
    data: dict, missing_value, remap_fields: dict, **loader_args
) -> dict:
    """We expect that nav context will use the remapped key"""
    missing_keys = utils.get_missing_fields(data, missing_value)
    found = dict()

    if missing_keys and loader_args.get("nav_context", False):
        nav_context = loader_args["nav_context"]
        for field in data.keys():
            # look in nav_context using key ie. "account" not the field ie. "account_{id}"
            key = remap_fields.get(field, field)

            # return the value using the field
            value = nav_context.get(key, missing_value)
            if value is not missing_value:
                found[field] = value
    return found


def load_from_global_cache(data: dict, missing_value, **loader_args) -> dict:
    missing_keys = utils.get_missing_fields(data, missing_value)
    return cache.load(missing_keys, missing_value, **loader_args)


def load_from_server(
    data: dict, missing_value, permission_error_path: str, **loader_args: dict
) -> dict:
    missing_keys = utils.get_missing_fields(data, missing_value)
    found = dict()

    if missing_keys:
        try:
            if anvil.is_server_side():
                print('direct server side request')
                from .DataFinder import _keychain_data_request
                server_data = _keychain_data_request(missing_keys, **loader_args)
            else:
                print('client side request')
                server_data = anvil.server.call_s(
                    "_keychain_data_request", missing_keys, **loader_args
                )
            found.update(server_data)
        except errors.AccessDenied as e:
            if permission_error_path:
                navigate(
                    path=permission_error_path,
                    nav_context=dict(**data, **loader_args.get("nav_context", dict())),
                )
            else:
                raise e

    return found


def apply_field_remap(data: dict, remap_fields: dict):
    return {remap_fields.get(field, field): value for field, value in data.items()}


def fetch(
    fields: list[str],
    missing_value=None,
    remap_fields: dict[str, str] = None,
    permission_error_path: str = None,
    strict: bool = False,
    restrict_fields: bool = False,
    force_update=False,
    **loader_args,
):
    remap_fields = remap_fields or dict()
    data = utils.key_list_to_dict(fields, missing_value)

    if not force_update:
        # if we are not forcing an update, search through our potential cache locations.
        found_in_nav = load_from_nav_context(
            data, missing_value, remap_fields, **loader_args
        )
        print("found_in_nav", found_in_nav)
        data.update(found_in_nav)

        found_in_global = load_from_global_cache(data, missing_value, **loader_args)
        print("found_in_global", found_in_global)
        data.update(found_in_global)

    found_from_server = load_from_server(
        data, missing_value, permission_error_path, **loader_args
    )
    print("found_from_server", found_from_server)
    data.update(found_from_server)

    # Update the global cache
    cache.update(data, missing_value, **loader_args)

    if restrict_fields:
        data = restrict_to_requested(fields, data)

    if strict:
        strict_data(fields, data, missing_value)

    return apply_field_remap(data, remap_fields)


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
        return fetch(
            fields,
            self.missing_value,
            self.remap_fields,
            self.permission_error_path,
            self.strict,
            self.restrict_fields,
            **loader_args,
        )

    def _get_output_keys(self) -> list:
        fields = self._get_all_fields()
        return [self.remap_fields.get(field, field) for field in fields]

    def _get_all_fields(self) -> list:
        return self.fields + self.global_fields + self.local_fields
