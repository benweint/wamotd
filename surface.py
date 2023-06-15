from PIL.Image import Image
from typing import Any, Dict
from typing_extensions import Protocol


class Surface(Protocol):
    def render(self, weather_rsp: bytes) -> Image:
        ...
