from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
from typing import Any, Dict, Optional
import math

small_font = ImageFont.truetype("./resources/DejaVuSans-Bold.ttf", 16)
medium_font = ImageFont.truetype("./resources/DejaVuSans.ttf", 20)
large_font = ImageFont.truetype("./resources/DejaVuSans-Bold.ttf", 24)
icon_font = ImageFont.truetype("./resources/meteocons.ttf", 48)

# Map the OpenWeatherMap icon code to the appropriate font character
# See http://www.alessioatzeni.com/meteocons/ for icons
ICON_MAP = {
    "01d": "B",
    "01n": "C",
    "02d": "H",
    "02n": "I",
    "03d": "N",
    "03n": "N",
    "04d": "Y",
    "04n": "Y",
    "09d": "Q",
    "09n": "Q",
    "10d": "R",
    "10n": "R",
    "11d": "Z",
    "11n": "Z",
    "13d": "W",
    "13n": "W",
    "50d": "J",
    "50n": "K",
}

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Renderer:
    def __init__(self, width: int, height: int, motd: Optional[str] = None) -> None:
        self.width = width
        self.height = height
        self.motd = motd

    def format_temperature(self, temp: float) -> str:
        return "%d°" % temp

    def render_text(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        text: str,
        font: ImageFont.FreeTypeFont,
        xalign: Optional[str] = None,
        yalign: Optional[str] = None,
    ) -> None:
        (text_width, text_height) = font.getsize(text)

        if not xalign:
            xalign = "left" if x >= 0 else "right"

        if not yalign:
            yalign = "top" if y >= 0 else "bottom"

        if x < 0:
            x += self.width
        if y < 0:
            y += self.height

        if xalign == "right":
            x -= text_width
        elif xalign == "center":
            x -= text_width // 2

        if yalign == "bottom":
            y -= text_height
        elif yalign == "center":
            y -= text_height // 2

        draw.text((x, y), text, font=font, fill=BLACK)

    def render(self, weather: Dict[str, Any]) -> Image.Image:
        now = datetime.now()
        time_text = now.strftime("%A, %B %d").replace(" 0", " ")

        # set the icon/background
        today = weather["daily"][0]
        todays_weather = today["weather"][0]

        weather_icon = ICON_MAP[todays_weather["icon"]]
        main_text = todays_weather["main"]
        description = todays_weather["description"].capitalize()
        high_temp = self.format_temperature(today["temp"]["max"])

        image = Image.new("RGB", (self.width, self.height), color=WHITE)
        draw = ImageDraw.Draw(image)

        # Draw the time (top center)
        centerx = self.width // 2
        self.render_text(draw, centerx, 4, time_text, small_font, xalign="center")
        draw.line([(0, 25), (self.width, 25)], fill=BLACK)

        # Draw the icon
        self.render_text(draw, 5, 30, weather_icon, icon_font)

        # Draw the main text
        self.render_text(draw, 65, 35, main_text, large_font)
        self.render_text(draw, 65, 65, description, small_font)

        # Draw the temperature
        self.render_text(draw, -5, 30, high_temp, large_font)

        if self.motd:
            self.render_text(draw, centerx, -5, self.motd, small_font, xalign="center")

        return image
