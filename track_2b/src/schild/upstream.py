import httpx


class UpstreamError(Exception):
    pass


class Upstream:
    """An external OpenAI-compatible model. It only ever receives redacted messages."""

    def __init__(self, base_url, api_key, model, *, timeout=120.0, transport=None):
        self.model = model
        self._url = base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = httpx.Client(timeout=timeout, headers=headers, transport=transport)

    def complete(self, messages: list[dict]) -> dict:
        try:
            response = self._client.post(self._url, json={"model": self.model, "messages": messages})
        except httpx.HTTPError as exc:
            raise UpstreamError(str(exc)) from exc
        if response.status_code >= 400:
            raise UpstreamError(f"upstream returned HTTP {response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise UpstreamError("upstream did not return JSON") from exc
