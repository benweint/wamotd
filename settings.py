import os

DISPLAY_WIDTH=250
DISPLAY_HEIGHT=122
OPEN_WEATHER_TOKEN = os.environ.get("OPEN_WEATHER_TOKEN")
COORDINATES = os.environ.get("COORDINATES")  # format is <lat>,<lng>
LAT, LON = COORDINATES.split(",")
RESPONSE_PATH = os.getenv("RESPONSE_PATH")
RENDER_INTERVAL = int(os.environ.get('RENDER_INTERVAL', '60'))
WEATHER_REFRESH_INTERVAL = int(os.environ.get('WEATHER_REFRESH_INTERVAL', '300'))
EXAMPLE_RESPONSE = os.getenv('EXAMPLE_RESPONSE')
