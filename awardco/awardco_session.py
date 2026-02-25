import json
import logging

import httpx
from typing import Callable, Any

from httpx import HTTPStatusError


async def raise_on_error(res: httpx.Response):
    await res.aread()
    try:
        res.raise_for_status()
    except HTTPStatusError as err:
        err.add_note(res.text)
        raise err

async def log_request(request: httpx.Request):
    logging.info(f"Request URL: {request.method}: {request.url}")
    body = request.content.decode()
    if body != '':
        logging.info(f"Request body: {json.dumps(json.loads(body), indent=2)}")

async def log_response(res: httpx.Response):
    await res.aread()
    logging.info(f"Status Code: {res.status_code} from {res.request.method}: {res.request.url}")
    logging.info(f"Response body: {res.text}")

class AwardcoSession(httpx.AsyncClient):
    def __init__(self, api_key: str, base_url: str = None, *args, **kwargs):
        transport = httpx.AsyncHTTPTransport(retries=3)
        event_hooks = {
            'response': [log_response, raise_on_error],
            'request': [log_request],
        }
        super().__init__(base_url=base_url, transport=transport, event_hooks=event_hooks, *args, **kwargs)
        self.headers['apiKey'] = api_key
