from ._anvil_designer import Form1Template
from routing import router

import time

class Form1(Form1Template):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        properties["item"] = routing_context.data
        self.init_components(**properties)

        now = time.time()
        print(f"Form1: {self.item}")
        cached_time = self.item['form_1']
        self.text_1.text = f"{now} - {cached_time} = {now - cached_time}"
