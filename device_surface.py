# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from datetime import datetime
import json
import io
import digitalio
import busio
import board
from adafruit_epd.epd import Adafruit_EPD
from adafruit_epd.ssd1680 import Adafruit_SSD1680
from typing import Any, Dict
from PIL import Image


class DeviceSurface:
    def __init__(self, width: int, height: int):
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        ecs = digitalio.DigitalInOut(board.CE0)
        dc = digitalio.DigitalInOut(board.D22)
        rst = digitalio.DigitalInOut(board.D27)
        busy = digitalio.DigitalInOut(board.D17)

        display = Adafruit_SSD1680(
            height,
            width,
            spi,
            cs_pin=ecs,
            dc_pin=dc,
            sramcs_pin=None,
            rst_pin=rst,
            busy_pin=busy,
        )
        display.rotation = 1

        self.display = display

    def update(self, image: Image.Image) -> None:
        self.display.fill(Adafruit_EPD.WHITE)
        self.display.image(image)
        self.display.display()
