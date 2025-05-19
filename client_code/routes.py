from routing.router import Route, Redirect

from . import data_finder


class HomeRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path="/1")


class AutoLoad(Route):
    required_fields = list()
    cache_data = True
    strict=True
    
    def load_data(self, **loader_args):
        return data_finder.fetch(loader_args, self.required_fields, strict=self.strict)


class Form1Route(AutoLoad):
    path = "/1"
    form = "Pages.Form1"
    required_fields = ["form_1", "form_3"]


class Form2Route(AutoLoad):
    path = "/2"
    form = "Pages.Form2"
    strict = False
    required_fields = ["form_2", "invalid_data_key", "context"]

class Form3Route(AutoLoad):
    path = "/3"
    form = "Pages.Form3"
    required_fields = ["form_3"]


data_finder.find_global_fields()