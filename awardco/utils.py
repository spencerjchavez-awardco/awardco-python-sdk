import asyncio
import threading
from typing import Coroutine, TypeVar

T = TypeVar('T')

_loop: asyncio.AbstractEventLoop | None = None
_loop_lock = threading.Lock()


def _get_loop() -> asyncio.AbstractEventLoop:
    global _loop
    with _loop_lock:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            thread = threading.Thread(target=_loop.run_forever, daemon=True)
            thread.start()
    return _loop


def wrap_async(coro: Coroutine[None, None, T]) -> T:
    """Submit a coroutine to the persistent background event loop and block until complete.
    This never closes the loop, so httpx.AsyncClient connection
    pools are reused across multiple synchronous calls.
    """
    return asyncio.run_coroutine_threadsafe(coro, _get_loop()).result()
