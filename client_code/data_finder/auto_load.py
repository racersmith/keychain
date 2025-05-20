from routing.router import Route
from .data_finder import fetch


class AutoLoad(Route):
    """ Automatically load data from required_fields 

        fields:
            list of keys that should can be automatically added to global cache if duplicated across routes
        global_fields:
            list of keys that will be included in global cache
        local_fields:
            list of keys that will only be used locallaly and will be excluded from global cache
            
        strict:
            bool, should we raise an error if there are values that can not be found or just fill them with None
            strict will also limit the return keys to strictly those listed in required_fields.
            
    """
    cache_data = True

    fields = list()
    global_fields = list()
    local_fields = list()
    strict = True

    def load_data(self, **loader_args) -> dict:
        return fetch(loader_args, self._get_all_fields(), strict=self.strict)

    def _get_all_fields(self):
        return self.fields + self.global_fields + self.local_fields