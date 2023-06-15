import urllib.request
import urllib.parse
from typing_extensions import Protocol


# See https://openweathermap.org/api/one-call-3#current
DATA_SOURCE_URL = "https://api.openweathermap.org/data/3.0/onecall"


class Fetcher(Protocol):
    def fetch(self) -> bytes: ...


class OpenWeatherFetcher:
    def __init__(
        self, appid: str, lat: float, lon: float, units: str = "imperial"
    ) -> None:
        self.params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,alerts",
            "appid": appid,
            "units": units,
        }
        self.url = DATA_SOURCE_URL + "?" + urllib.parse.urlencode(self.params)

    def fetch(self) -> bytes:
        response = urllib.request.urlopen(DATA_SOURCE_URL)
        if response.status == 200:
            value = response.read()
            print("Response is", value)
        else:
            raise ValueError(f"bad HTTP response {response.status}")

        return response


class ExampleFetcher:
    def __init__(self, response_path: str) -> None:
        with open(response_path, "rb") as f:
            self.response = f.read()

    def fetch(self) -> bytes:
        return self.response
