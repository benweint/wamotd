from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
from typing import Any, Dict, Optional
import math
import random

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Screensaver:
    def __init__(self, width: int, height: int, num_stars: int = 100) -> None:
        self.width = width
        self.height = height
        self.num_stars = num_stars

    def render(self, num_stars: int = 100) -> Image.Image:
        # Create a black image
        img = Image.new("RGB", (self.width, self.height), color=BLACK)
        draw = ImageDraw.Draw(img)

        for _ in range(self.num_stars):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            draw.point((x, y), fill=WHITE)

        return img
