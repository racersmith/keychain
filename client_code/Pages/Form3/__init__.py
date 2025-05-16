from ._anvil_designer import Form3Template
from routing import router

import time

class Form3(Form3Template):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        properties["item"] = routing_context.data
        self.init_components(**properties)
        
        now = time.time()
        print(f"Form3: {self.item}")
        cached_time = self.item['form_3']
        self.text_1.text = f"{now} - {cached_time} = {now - cached_time}"