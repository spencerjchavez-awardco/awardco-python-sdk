import json
import logging
import httpx
from httpx import HTTPStatusError, URL
from typing import Callable, Any, Mapping

logger = logging.getLogger(__name__)


async def raise_on_error(res: httpx.Response):
    await res.aread()
    try:
        res.raise_for_status()
    except HTTPStatusError as err:
        err.add_note(res.text)
        raise err

async def log_request(request: httpx.Request):
    await request.aread()
    logger.info("Request: %s %s", request.method, request.url)

async def log_response(res: httpx.Response):
    await res.aread()
    logger.info("Response: %s %s %s", res.status_code, res.request.method, res.request.url)

class AwardcoSession(httpx.AsyncClient):
    def __init__(self, api_key: str, base_url: URL | None = None, *args, **kwargs):
        transport = httpx.AsyncHTTPTransport(retries=3)
        event_hooks: Mapping[str, list[Callable[..., Any]]] = {
            'response': [log_response, raise_on_error],
            'request': [log_request],
        }
        super().__init__(base_url=base_url or URL(), transport=transport, event_hooks=event_hooks, *args, **kwargs)
        self.headers['apiKey'] = api_key
