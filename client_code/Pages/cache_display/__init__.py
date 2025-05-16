from ._anvil_designer import cache_displayTemplate

from routing.router import _cached
from ...routes import _GLOBAL_CACHE

class cache_display(cache_displayTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.refresh()

    def refresh(self, *args, **kwargs):
        lines = ["==router cached data=="]
        for key, value in _cached.CACHED_DATA.items():
            lines.append(f"{key}")
            lines.append(f"{value}\n")

        lines.append("==Global Cache==")
        for key, value in _GLOBAL_CACHE.items():
            lines.append(f"{key}")
            lines.append(f"{value}\n")
        
        self.text_1.text = "\n".join(lines)