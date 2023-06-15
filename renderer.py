from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
from typing import Any, Dict

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
    def __init__(
        self, width: int, height: int, am_pm: bool = True, celsius: bool = True
    ) -> None:
        self.width = width
        self.height = height
        self.am_pm = am_pm
        self.celsius = celsius

        self.small_font = small_font
        self.medium_font = medium_font
        self.large_font = large_font

        self._weather_icon = ""
        self._main_text = ""
        self._temperature = ""
        self._description = ""
        self._time_text = ""

    def render(self, weather_response: bytes) -> Image.Image:
        weather = json.loads(weather_response.decode("utf-8"))

        now = datetime.now()
        self._time_text = now.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")

        # set the icon/background
        today = weather["daily"][0]
        self._weather_icon = ICON_MAP[today["weather"][0]["icon"]]

        main = today["weather"][0]["main"]
        self._main_text = main

        temperature = weather["current"]["temp"] - 273.15  # its...in kelvin
        if self.celsius:
            self._temperature = "%d °C" % temperature
        else:
            self._temperature = "%d °F" % ((temperature * 9 / 5) + 32)

        description = weather["current"]["weather"][0]["description"]
        description = description[0].upper() + description[1:]
        print(description)
        self._description = description
        # "thunderstorm with heavy drizzle"

        image = Image.new("RGB", (self.width, self.height), color=WHITE)
        draw = ImageDraw.Draw(image)

        # Draw the Icon
        (font_width, font_height) = icon_font.getsize(self._weather_icon)
        draw.text(
            (
                self.width // 2 - font_width // 2,
                self.height // 2 - font_height // 2 - 5,
            ),
            self._weather_icon,
            font=icon_font,
            fill=BLACK,
        )

        # Draw the time
        (font_width, font_height) = medium_font.getsize(self._time_text)
        draw.text(
            (5, font_height * 2 - 5),
            self._time_text,
            font=self.medium_font,
            fill=BLACK,
        )

        # Draw the main text
        (font_width, font_height) = large_font.getsize(self._main_text)
        draw.text(
            (5, self.height - font_height * 2),
            self._main_text,
            font=self.large_font,
            fill=BLACK,
        )

        # Draw the description
        (font_width, font_height) = small_font.getsize(self._description)
        draw.text(
            (5, self.height - font_height - 5),
            self._description,
            font=self.small_font,
            fill=BLACK,
        )

        # Draw the temperature
        (font_width, font_height) = large_font.getsize(self._temperature)
        draw.text(
            (
                self.width - font_width - 5,
                self.height - font_height * 2,
            ),
            self._temperature,
            font=self.large_font,
            fill=BLACK,
        )

        return image
