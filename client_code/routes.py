from routing.router import Route, Redirect

import time

class HomeRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path='/1')

class Form1Route(Route):
    path = "/1"
    form = "Pages.Form1"
    cache_data = True

    def load_data(self, **loader_args):
        time.sleep(3)
        return {'form1': time.time}

class Form2Route(Route):
    path = "/2"
    form = "Pages.Form2"
    cache_data = True

    def load_data(self, **loader_args):
        time.sleep(3)
        return {'form2': time.time()}

class Form3Route(Route):
    path = "/3"
    form = "Pages.Form3"
    cache_data = True

    def load_data(self, **loader_args):
        time.sleep(3)
        return {'form3': time.time()}