from routing.router import Route, Redirect
import anvil.server



def request_missing(data: dict, missing_value = None):
    """ Make a request that tries to fill missing values.  This should be a flat request. """
    missing = {key: missing_value for key, value in data.items() if value == missing_value}
    if missing:
        data.update(anvil.server.call_s('request', **missing))
    return data


class HomeRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        data = {'form_1': None, 'form_2': None, 'form_3': None}
        data.update(loader_args['nav_context'])
        print(f"loading data for {self.path}\n\texisting data: {data}\n\tnav_context: {loader_args['nav_context']}")
        raise Redirect(path='/1', nav_context=request_missing(data))

class Form1Route(Route):
    path = "/1"
    form = "Pages.Form1"
    cache_data = True

    def load_data(self, **loader_args):
        data = {'form_1': None, 'form_2': None}
        data.update(loader_args['nav_context'])
        print(f"loading data for {self.path}\n\texisting data: {data}\n\tloader_args: {loader_args}")
        return request_missing(data)

class Form2Route(Route):
    path = "/2"
    form = "Pages.Form2"
    cache_data = True

    def load_data(self, **loader_args):
        data = {'form_2': None}
        data.update(loader_args['nav_context'])
        print(f"loading data for {self.path}\n\texisting data: {data}\n\tloader_args: {loader_args}")
        return request_missing(data)

class Form3Route(Route):
    path = "/3"
    form = "Pages.Form3"
    cache_data = True

    def load_data(self, **loader_args):
        data = {'form_3': None}
        data.update(loader_args['nav_context'])
        print(f"loading data for {self.path}\n\texisting data: {data}\n\tloader_args: {loader_args}")
        return request_missing(data)