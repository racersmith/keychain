from ._anvil_designer import cache_displayTemplate

from routing.router import _cached
from ...data_finder.data_finder import _GLOBAL_CACHE

import json

class cache_display(cache_displayTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.refresh()

    def refresh(self, *args, **kwargs):
        lines = ["==router cached data=="]
        for key, value in _cached.CACHED_DATA.items():
            lines.append(f"{key}:\n{json.dumps(value.data, indent=4)}\n")

        lines.append("==Global Cache==")
        for key, value in _GLOBAL_CACHE.items():
            lines.append(f"{key}: {value}\n")
        self.text_1.text = "\n".join(lines)
