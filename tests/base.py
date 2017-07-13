"""tests base file"""

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
        return self().__await__()