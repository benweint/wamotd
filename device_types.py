from renderer import Renderer
from typing import Any, Dict, Protocol
from PIL import Image


class Surface(Protocol):
    def __init__(self, width: int, height: int) -> None:
        ...

    def update(self, image: Image.Image) -> None:
        ...
