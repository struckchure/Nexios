from __future__ import annotations
import http
from collections.abc import Mapping


class HTTPException(Exception):
    def __init__(self, status_code, detail = None, headers = []) -> None:
        super().__init__(detail or http.HTTPStatus(status_code).phrase)
        self.status_code = status_code
        self.detail = self.args[0]  
        self.headers = headers

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.status_code}, {self.detail!r})"


class WebSocketException(Exception):
    def __init__(self, code: int, reason: str | None = None) -> None:
        super().__init__(reason or "")
        self.code = code
        self.reason = self.args[0] 

    def __str__(self) -> str:
        return f"WebSocket {self.code}: {self.reason}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.code}, {self.reason!r})"
