"""tests base file"""

import asyncio
from unittest.mock import Mock

class AsyncMock(Mock):   
    def __call__(self, *args, **kwargs):
        sup = super(AsyncMock, self)
        async def coro():
            return sup.__call__(*args, **kwargs)
        return coro()

    def __await__(self):
        return self().__await__()


class EmptyAsyncMock(Mock):
    def __call__(self, *args, **kwargs):
        sup = super(EmptyAsyncMock, self)
        async def coro():
            return None
        return coro()

    def __await__(self):
        return self().__await__
        

def async_test(f):
    loop = asyncio.get_event_loop()
    def inner(*args, **kwargs):
        result = loop.run_until_complete(f(*args, **kwargs))
        return result
    return inner