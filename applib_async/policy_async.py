"""..."""
import asyncio
from asyncio import BaseEventLoop
from functools import partial
from concurrent.futures import ThreadPoolExecutor


async def policy_async(*args, loop: BaseEventLoop = None, **kwargs):
    executor = kwargs.pop('executor', None)
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=1)

    loop = loop or asyncio.get_event_loop()
    func_loop = kwargs.pop('func_loop', None)
    if func_loop is not None:
        kwargs['loop'] = func_loop

    return await loop.run_in_executor(executor, partial(*args, **kwargs))
