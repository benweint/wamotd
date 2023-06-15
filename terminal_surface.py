import json
import io
import sys
from surface import Surface
from subprocess import Popen, PIPE
from typing import Any, Dict


class TerminalSurface:
    def __init__(self, renderer: Surface) -> None:
        self.renderer = renderer

    def update(self, weather_response: bytes) -> None:
        image = self.renderer.render(weather_response)
        image_buf = io.BytesIO(b"")
        image.save(image_buf, format="png")
        image_buf.seek(0)

        p = Popen(["kitty", "+kitten", "icat"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data = p.communicate(input=image_buf.read())[0]
        print(stdout_data)
