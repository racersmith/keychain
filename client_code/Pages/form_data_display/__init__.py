from ._anvil_designer import form_data_displayTemplate

import json
import time

class form_data_display(form_data_displayTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)


    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.item['now'] = time.time()
        self.text_1.text = json.dumps(self.item, indent=4)
