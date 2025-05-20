from routing.router import Route, Redirect

from .data_finder import AutoLoad, find_global_fields


class RootRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path="/home")


class HomeRoute(AutoLoad):
    path = "/home"
    form = "Pages.Home"
    required_fields = ["first_load", "the answer to everything"]


class AccountRoute(AutoLoad):
    path = "/account"
    form = "Pages.Account"
    strict = False
    required_fields = ["first_load", "the answer to life", "name"]


class PrivateIdRoute(AutoLoad):
    path = "/private/:private_id"
    form = "Pages.Private"
    strict = False
    required_fields = ["first_load", "the answer to the universe", "the answer to life", "something_private", "private_value"]
    

class PrivateRoute(AutoLoad):
    path = "/private"
    form = "Pages.Private"
    strict = False
    required_fields = ["first_load", "the answer to the universe", "the answer to life", "something_private"]


class ProtectedRoute(AutoLoad):
    path = "/protected"
    form = "Pages.Protected"
    required_fields = ["first_load", "the answer to the universe", "the answer to life", "what is the question"]


# This could be more tightly integrated so this is not needed here...
find_global_fields()
