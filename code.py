# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example queries the Open Weather Maps site API to find out the current
weather for your location... and display it on a eInk Bonnet!
"""

import time
import urllib.request
import urllib.parse
import digitalio
import busio
import board
from adafruit_epd.ssd1680 import Adafruit_SSD1680
from weather_graphics import Weather_Graphics

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)

OPEN_WEATHER_TOKEN = os.getenv('OPEN_WEATHER_TOKEN')

# Format: <cityname>, <country-code>, where countrycode is ISO3166 format.
LOCATION = os.getenv('LOCATION', default="Portland, US")

DATA_SOURCE_URL = "http://api.openweathermap.org/data/2.5/weather"

if len(OPEN_WEATHER_TOKEN) == 0:
    raise RuntimeError('Please set the OPEN_WEATHER_TOKEN env var.')

# Set up where we'll be fetching data from
params = {"q": LOCATION, "appid": OPEN_WEATHER_TOKEN}
data_source = DATA_SOURCE_URL + "?" + urllib.parse.urlencode(params)
print(f'Will use Open Weather base API URL: {DATA_SOURCE_URL}')

display = Adafruit_SSD1680(
    122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None, rst_pin=rst, busy_pin=busy,
)
display.rotation = 1

gfx = Weather_Graphics(display, am_pm=True, celsius=False)
weather_refresh = None

while True:
    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        # TODO: exception handling
        response = urllib.request.urlopen(data_source)
        if response.getcode() == 200:
            value = response.read()
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        else:
            print("Unable to retrieve data at {}".format(url))

    gfx.update_time()
    time.sleep(300)  # wait 5 minutes before updating anything again
