"""Client HTTP du worker vers le coordinateur."""

import httpx

from common.schemas import (
    RegisterRequest,
    RegisterResponse,
    ResultSubmission,
    SubmitResponse,
    WorkBatch,
)


class CoordinatorClient:
    def __init__(self, base_url: str):
        self._http = httpx.Client(base_url=base_url, timeout=30.0)
        self._api_key: str | None = None

    def set_api_key(self, api_key: str) -> None:
        self._api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {"X-API-Key": self._api_key} if self._api_key else {}

    def register(self, device_name: str) -> RegisterResponse:
        resp = self._http.post(
            "/devices/register",
            json=RegisterRequest(device_name=device_name).model_dump(),
        )
        resp.raise_for_status()
        creds = RegisterResponse(**resp.json())
        self.set_api_key(creds.api_key)
        return creds

    def get_work(self, n: int) -> WorkBatch:
        resp = self._http.get("/work", params={"n": n}, headers=self._headers())
        resp.raise_for_status()
        return WorkBatch(**resp.json())

    def submit(self, results: list[ResultSubmission]) -> SubmitResponse:
        resp = self._http.post(
            "/results",
            json={"results": [r.model_dump() for r in results]},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return SubmitResponse(**resp.json())

    def close(self) -> None:
        self._http.close()
