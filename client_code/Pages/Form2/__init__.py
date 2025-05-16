from ._anvil_designer import Form2Template
from routing import router

import time

class Form2(Form2Template):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        properties["item"] = routing_context.data
        self.init_components(**properties)

        now = time.time()
        print(f"Form2: {self.item}")
        cached_time = self.item['form_2']
        self.text_1.text = f"{now} - {cached_time} = {now - cached_time}"