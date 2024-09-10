import requests
import json
from typing import Any, Dict, Union
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
        self.params: Dict[str, Union[float, str]] = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,alerts",
            "appid": appid,
            "units": units,
        }
        self._url = DATA_SOURCE_URL

    def fetch(self) -> Dict[str, Any]:
        response = requests.get(self._url, params=self.params)
        if response.status_code == 200:
            decoded = response.json()
            assert isinstance(decoded, Dict)
            return decoded
        else:
            raise ValueError(
                f"bad HTTP response {response.status_code}, body = {response.text}"
            )

    def url(self) -> str:
        return self._url


class ExampleFetcher:
    def __init__(self, response_path: str) -> None:
        self.response_path = response_path

    def fetch(self) -> Dict[str, Any]:
        with open(self.response_path, "rb") as f:
            decoded = json.load(f)
            assert isinstance(decoded, Dict)
            return decoded

    def url(self) -> str:
        return self.response_path
