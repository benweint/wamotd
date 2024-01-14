from typing import Dict, Optional, Protocol
import json
import os


class Store(Protocol):
    def get(self, key: str) -> Optional[str]:
        ...

    def set(self, key: str, value: str) -> None:
        ...


class FileStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self.cache = {}  # type: Dict[str,str]
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write("{}")

        with open(self.path, "r") as file:
            data = json.load(file)

        for key in data:
            self.cache[key] = str(data[key])

    def get(self, key: str) -> Optional[str]:
        return self.cache[key]

    def set(self, key: str, value: str) -> None:
        self.cache[key] = value
        with open(self.path, "w") as file:
            json.dump(self.cache, file)
