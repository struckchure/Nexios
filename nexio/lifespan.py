from typing import TypeVar


_T = TypeVar("NexioLIfeSpan")
class _DefaultLifespan:
    def __init__(self):
        return 

    async def __aenter__(self) -> None:
        
        pass

    async def __aexit__(self, *exc_info: object) -> None:
        pass

    def __call__(self: _T) -> _T:
        return self
    