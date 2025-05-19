from routing.router import Route, Redirect

from . import data_finder


class RootRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path="/home")


class AutoLoad(Route):
    required_fields = list()
    cache_data = True
    strict = True
    
    def load_data(self, **loader_args):
        return data_finder.fetch(loader_args, self.required_fields, strict=self.strict)


class HomeRoute(AutoLoad):
    path = "/home"
    form = "Pages.Home"
    required_fields = ["first_load", "the answer to everything"]


class AccountRoute(AutoLoad):
    path = "/account"
    form = "Pages.Account"
    strict = False
    required_fields = ["first_load", "the answer to the life", "name"]


class PrivateIdRoute(AutoLoad):
    path = "/private/:private_id"
    form = "Pages.Private"
    strict = False
    required_fields = ["first_load", "the answer to the universe", "the answer to the life", "something_private", "private_value"]
    

class PrivateRoute(AutoLoad):
    path = "/private"
    form = "Pages.Private"
    strict = False
    required_fields = ["first_load", "the answer to the universe", "the answer to the life", "something_private"]


class ProtectedRoute(AutoLoad):
    path = "/protected"
    form = "Pages.Protected"
    required_fields = ["first_load", "the answer to the universe", "the answer to the life", "what is the question"]


# This could be more tightly integrated so this is not needed here...
data_finder._GLOBAL_CACHE = data_finder.find_global_fields()