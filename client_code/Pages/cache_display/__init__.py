from ._anvil_designer import cache_displayTemplate

from routing.router import _cached
from ...data_finder.auto_load import _GLOBAL_CACHE, _GLOBAL_KEYS

import json

class cache_display(cache_displayTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.refresh()

    def refresh(self, *args, **kwargs):
        lines = ["==Router Cached Form Data=="]
        for key, value in _cached.CACHED_DATA.items():
            lines.append(f"{key}:\n{json.dumps(value.data, indent=4)}\n")

        lines.append("==Global Keys==")
        lines.append("\n".join(_GLOBAL_KEYS))
        
        lines.append("\n==Global Cache==")
        lines.append(json.dumps(_GLOBAL_CACHE, indent=4))
        self.text_1.text = "\n".join(lines)
