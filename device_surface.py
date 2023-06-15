# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from datetime import datetime
import json
import io
import digitalio
import busio
import board
from renderer import Renderer
from adafruit_epd.epd import Adafruit_EPD
from adafruit_epd.ssd1680 import Adafruit_SSD1680
from typing import Any, Dict


class DeviceSurface:
    def __init__(self, display: Any, renderer: Renderer):
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        ecs = digitalio.DigitalInOut(board.CE0)
        dc = digitalio.DigitalInOut(board.D22)
        rst = digitalio.DigitalInOut(board.D27)
        busy = digitalio.DigitalInOut(board.D17)

        display = Adafruit_SSD1680(
            122,
            250,
            spi,
            cs_pin=ecs,
            dc_pin=dc,
            sramcs_pin=None,
            rst_pin=rst,
            busy_pin=busy,
        )
        display.rotation = 1

        self.display = display
        self.renderer = renderer

    def update(self, weather_response: bytes) -> None:
        image = self.renderer.render(weather_response)
        self.display.fill(Adafruit_EPD.WHITE)
        self.display.image(image)
        self.display.display()
