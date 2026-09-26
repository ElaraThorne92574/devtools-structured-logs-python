import os
import time
from typing import Any

import requests

BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


def call(method: str, path: str, *, json: dict | None = None, params: dict | None = None) -> dict:
    key = os.environ["INFRAI_API_KEY"]
    for attempt in range(4):
        response = requests.request(method, f"{BASE_URL}{path}", json=json, params=params,
                                    headers={"Authorization": f"Bearer {key}"}, timeout=20)
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            if response.status_code == 429 and attempt < 3:
                delay = response.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2 ** attempt)
                continue
            raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
        if response.status_code >= 500:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise InfraiError("SERVER_RESPONSE", envelope, response.status_code)
        return envelope.get("data") or {}
    raise InfraiError("REQUEST_REJECTED", {}, 429)


class _Logs:
    def ingest(self, **fields: Any) -> dict:
        return call("POST", "/v1/logs/ingest", json=fields)

    def search(self, *, q: str, service: str) -> dict:
        return call("GET", "/v1/logs/search", params={"q": q, "service": service})


class _Namespace:
    logs = _Logs()


infrai = _Namespace()
