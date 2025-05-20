from routing.router import Route
from .data_finder import fetch


class AutoLoad(Route):
    """ Automatically load data from required_fields 

        required_fields:
            list of keys that will be in the dict from load_data()
            
        strict:
            bool, should we raise an error if there are values that can not be found or just fill them with None
            strict will also limit the return keys to strictly those listed in required_fields.
            

    example:
        class Account(AutoRoute):
            required_fields = ['name', 'email']
            strict = False
    
        
        load_data() -> {'name': 'Arther', 'email': None, 'phone': '987-654-3210'}
        The registered functions for the keys were unable to find 'email' and added an extra key 'phone'
        
    
        class Account(AutoRoute):
            required_fields = ['name', 'email']
            strict = True
    
        load_data() -> raises LookupError()    
        The registered functions for the keys were unable to find 'email' so an error is raised
    """
    cache_data = True

    required_fields = list()
    strict = True

    def load_data(self, **loader_args) -> dict:
        return fetch(loader_args, self.required_fields, strict=self.strict)
