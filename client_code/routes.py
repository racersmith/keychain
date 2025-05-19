from routing.router import Route, Redirect

from . import data_finder


class HomeRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path="/1")


class Form1Route(Route):
    path = "/1"
    form = "Pages.Form1"
    cache_data = True
    required_fields = ["form_1", "form_3"]

    def load_data(self, **loader_args):
        return data_finder.fetch(loader_args, local_data=["form_1"], global_data=["form_3"])


class Form2Route(Route):
    path = "/2"
    form = "Pages.Form2"
    cache_data = True
    required_fields = ["form_2", "invalid_data_key"]

    def load_data(self, **loader_args):
        return data_finder.fetch(loader_args, local_data=["form_2", "invalid_data_key"], strict=False)


class Form3Route(Route):
    path = "/3"
    form = "Pages.Form3"
    cache_data = True
    required_fields = ["form_3"]

    def load_data(self, **loader_args):
        return data_finder.fetch(loader_args, local_data=["form_3"])
