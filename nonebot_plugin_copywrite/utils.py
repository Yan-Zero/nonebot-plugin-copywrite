import functools
from typing import Callable


def to_await(call: Callable):
    async def _(method: Callable, *args, **kwargs):
        return method(*args, **kwargs)

    return functools.partial(_, method=call)
