import asyncio
from typing import Coroutine, TypeVar

T = TypeVar('T')


def wrap_async(coro: Coroutine[None, None, T]) -> T:
    """Run an async coroutine synchronously. Do not call from within a running event loop."""
    return asyncio.run(coro)
