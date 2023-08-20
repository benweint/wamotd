from renderer import Renderer
from typing import Any, Dict


class DeviceSurface:
    def __init__(self, width: int, height: int, renderer: Renderer) -> None:
        ...

    def update(self, weather_response: Dict[str, Any]) -> None:
        ...
