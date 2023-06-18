import urllib.request
import urllib.parse
import json
from typing import Any, Dict
from typing_extensions import Protocol


# See https://openweathermap.org/api/one-call-3#current
DATA_SOURCE_URL = "https://api.openweathermap.org/data/3.0/onecall"


class Fetcher(Protocol):
    def fetch(self) -> Dict[str, Any]:
        ...

    def url(self) -> str:
        ...


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
        self._url = DATA_SOURCE_URL + "?" + urllib.parse.urlencode(self.params)

    def fetch(self) -> Dict[str, Any]:
        response = urllib.request.urlopen(self._url)
        if response.status == 200:
            return json.load(response)
        else:
            raise ValueError(f"bad HTTP response {response.status}, body = {response.read()}")

    def url(self) -> str:
        return self._url


class ExampleFetcher:
    def __init__(self, response_path: str) -> None:
        self.response_path = response_path

    def fetch(self) -> Dict[str, Any]:
        with open(self.response_path, "rb") as f:
            return json.load(f)

    def url(self) -> str:
        return self.response_path
