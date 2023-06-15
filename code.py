import time
from renderer import Renderer
import os
from terminal_surface import TerminalSurface
from fetchers import ExampleFetcher, Fetcher, OpenWeatherFetcher

OPEN_WEATHER_TOKEN = os.getenv("OPEN_WEATHER_TOKEN")

# COORDINATES env var format is <lat>,<lng>
COORDINATES = os.getenv("COORDINATES")
assert COORDINATES is not None
LAT, LON = COORDINATES.split(",")

RESPONSE_PATH = os.getenv('RESPONSE_PATH')


fetcher : Fetcher
if RESPONSE_PATH:
    fetcher = ExampleFetcher(RESPONSE_PATH)
else:
    assert OPEN_WEATHER_TOKEN is not None
    fetcher = OpenWeatherFetcher(OPEN_WEATHER_TOKEN, float(LAT), float(LON))

renderer = Renderer(500, 300, am_pm=True, celsius=False)
surface = TerminalSurface(renderer)
weather_refresh = None

while True:
    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        # TODO: exception handling
        response = fetcher.fetch()
        surface.update(response)
        weather_refresh = time.monotonic()

    # surface.update()
    time.sleep(300)  # wait 5 minutes before updating anything again
