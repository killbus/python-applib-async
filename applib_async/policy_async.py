"""..."""
import asyncio
from asyncio import BaseEventLoop
from functools import partial
from concurrent.futures import ThreadPoolExecutor


async def policy_async(*args, loop: BaseEventLoop = None, **kwargs):
    executor = kwargs.pop('executor', None)
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=1)

    if not loop:
        loop = asyncio.get_event_loop()

    return await loop.run_in_executor(executor, partial(*args, **kwargs))