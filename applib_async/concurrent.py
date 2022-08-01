import asyncio
from typing import List, Iterable, AsyncGenerator

async def sure_release(semaphore: asyncio.Semaphore, func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    finally:
        semaphore.release()

async def add_task(semaphore: Semaphore, func, *args, **kwargs) -> asyncio.Task:
    """Decrement the semaphore, schedule an increment, and then work"""
    await semaphore.acquire()
    task = asyncio.create_task(sure_release(semaphore, func, *args, **kwargs))
    return task
    # logic here


async def ordinary_tasks(tasks: Iterable[asyncio.Task], loop: asyncio.AbstractEventLoop = None) -> AsyncGenerator[asyncio.Task, None]:
    """Add id to the task and then work

    https://stackoverflow.com/questions/50028465/python-get-reference-to-original-task-after-ordering-tasks-by-completion
    """
    wrappers: List[asyncio.Future] = []
    loop = loop or tasks[0].get_loop()
    for index, task in enumerate(tasks):
        task.idx = index + 1
        # Wrap the task in a future that completes when the
        # task does, but whose result is the task object itself.
        wrapper = loop.create_future()
        task.add_done_callback(wrapper.set_result)
        wrappers.append(wrapper)


    # 获取一个迭代器，这个迭代器会在future运行结束后返回future
    for t in asyncio.as_completed(wrappers):
        # yield completed tasks
        yield await t
