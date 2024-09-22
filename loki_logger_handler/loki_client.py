import requests
import gzip
from typing import Dict

from loki_logger_handler.models import LokiRequest


class LokiClient:
    # TODO: support auth
    def __init__(self, url: str, compressed: bool = False, additional_headers: Dict[str, str] = dict()):
        self.url: str = url
        self.compressed: bool = compressed
        self.headers: Dict[str, str] = additional_headers
        self.headers["Content-type"] = "application/json"
        self.session: requests.Session = requests.Session()

    def send(self, request: LokiRequest) -> None:
        response = None
        try:
            if self.compressed:
                self.headers["Content-Encoding"] = "gzip"
                request = gzip.compress(bytes(request, "utf-8"))

            response = self.session.post(self.url, data=request, headers=self.headers)
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Error while sending logs: {e}")

        finally:
            if response:
                response.close()
