import asyncio
import functools
from typing import Any, Callable


cache_map = {}


def format_key(*args: tuple, **kwargs: dict) -> int:
    def _hash(param: Any):
        if isinstance(param, tuple):
            return tuple(map(_hash, param))
        if isinstance(param, dict):
            return tuple(map(_hash, param.items()))
        elif hasattr(param, '__dict__'):
            return str(vars(param))
        else:
            return str(param)

    return hash(_hash(args) + _hash(kwargs))


def clear_cache(key: str | int):
    cache_map.pop(key, None)


def ttl_cache(key: Callable = format_key, ttl: int = 2) -> Callable:

    def wrapper(func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"{func} is not coroutine function.")

        @functools.wraps(func)
        async def inner(*args, **kwargs):
            cache_key = key(args, kwargs)

            if cache_map.get(cache_key):
                result = cache_map[cache_key]
            else:
                result = await func(*args, **kwargs)
                cache_map[cache_key] = result
                event_loop = asyncio.get_event_loop()
                event_loop.call_later(ttl, clear_cache, cache_key)
            return result
        return inner

    return wrapper
