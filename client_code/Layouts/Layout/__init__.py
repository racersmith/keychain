from ._anvil_designer import LayoutTemplate


class Layout(LayoutTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
