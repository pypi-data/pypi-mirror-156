import asyncio
import functools
from typing import Callable, Union, Any

cache_map = {}
lock = asyncio.Lock()

def format_key(*args: tuple, **kwargs: dict) -> int:
    return hash(str(args) + str(kwargs))


def clear_cache(key: str | int):
    cache_map.pop(key, None)


class Caller:
    def __init__(self):
        self.cond: "asyncio.Condition" = asyncio.Condition()
        self.value: Any = None
        self.err: BaseException = None  # type: ignore
        self.done: bool = False

    async def result(self):
        async with self.cond:
            while not self.done:
                await self.cond.wait()
        if self.err:
            raise self.err
        return self.value

    async def notify(self):
        async with self.cond:
            self.done = True
            self.cond.notify_all()


def ttl_cache(
    wrapped: Union[Callable, None] = None,
    key: Callable = format_key,
    ttl: int | float = 2
) -> Callable:

    def wrapper(func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"{func} is not coroutine function.")

        @functools.wraps(func)
        async def inner(*args, **kwargs):
            cache_key = key(args, kwargs)

            await lock.acquire()

            if cache_map.get(cache_key):
                call = cache_map[cache_key]
                lock.release()
                return await call.result()
            else:
                call = Caller()
                cache_map[cache_key] = call
                lock.release()
                try:
                    call.value = await func(*args, **kwargs)
                except Exception as e:
                    call.err = e
                finally:
                    await call.notify()
                event_loop = asyncio.get_event_loop()
                event_loop.call_later(ttl, clear_cache, cache_key)
                return await call.result()
        return inner
    if not wrapped:
        return wrapper
    elif callable(wrapped):
        return wrapper(wrapped)
