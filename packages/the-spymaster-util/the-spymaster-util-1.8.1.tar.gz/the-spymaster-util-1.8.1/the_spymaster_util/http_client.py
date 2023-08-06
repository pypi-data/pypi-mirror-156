import json
import logging
from typing import Callable

import requests
from requests import Response

log = logging.getLogger(__name__)

CONTEXT_HEADER_KEY = "x-spymaster-context"
CONTEXT_ID_HEADER_KEY = "x-spymaster-context-id"


class BaseHttpClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _http_call(self, endpoint: str, method: Callable, **kwargs) -> dict:
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.pop("headers", None) or {}
        log_context = getattr(log, "context", None)
        if log_context:
            headers[CONTEXT_HEADER_KEY] = json.dumps(log_context)
        response = method(url, headers=headers, **kwargs)
        _log_data(url=url, response=response)
        response.raise_for_status()
        data = response.json()
        return data

    def _get(self, endpoint: str, data: dict) -> dict:
        return self._http_call(endpoint=endpoint, method=requests.get, params=data)

    def _post(self, endpoint: str, data: dict) -> dict:
        return self._http_call(endpoint=endpoint, method=requests.post, json=data)


def _log_data(url: str, response: Response):
    try:
        data = response.json()
    except Exception:  # noqa
        data = response.content
    log.debug(
        f"Got status code {response.status_code}.",
        extra={"status_code": response.status_code, "url": url, "data": data},
    )
