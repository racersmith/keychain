from ._anvil_designer import AccountTemplate
from routing import router


class Account(AccountTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        properties["item"] = routing_context.data
        self.init_components(**properties)
        self.form_data_display_1.item = self.item
        self.layout.raise_event('x-refresh')