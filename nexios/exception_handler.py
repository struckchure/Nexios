from __future__ import annotations

import typing

from nexios._exception_handler import (
    ExceptionHandlers,
    StatusHandlers,
    wrap_app_handling_exceptions,
)
from nexios.exceptions import HTTPException, WebSocketException
from nexios.requests import Request
from nexios.responses import PlainTextResponse, Response
from nexios.websockets import WebSocket


class ExceptionMiddleware:
    def __init__(
        self,
        app: typing.Callable[[Request], Response],
        handlers: typing.Mapping[typing.Any, typing.Callable[[Request, Exception], Response]] | None = None,
        debug: bool = False,
    ) -> None:
        self.app = app
        self.debug = debug  # TODO: We ought to handle 404 cases if debug is set.
        self._status_handlers: StatusHandlers = {}
        self._exception_handlers: ExceptionHandlers = {
            HTTPException: self.http_exception,
            WebSocketException: self.websocket_exception,
        }
        if handlers is not None:
            for key, value in handlers.items():
                self.add_exception_handler(key, value)

    def add_exception_handler(
        self,
        exc_class_or_status_code: int | type[Exception],
        handler: typing.Callable[[Request, Exception], Response],
    ) -> None:
        if isinstance(exc_class_or_status_code, int):
            self._status_handlers[exc_class_or_status_code] = handler
        else:
            assert issubclass(exc_class_or_status_code, Exception)
            self._exception_handlers[exc_class_or_status_code] = handler

    async def __call__(self, request: Request) -> Response:
        request.exception_handlers = (self._exception_handlers, self._status_handlers)

        if isinstance(request, WebSocket):
            conn: WebSocket = request
        else:
            conn: Request = request

        return await wrap_app_handling_exceptions(self.app, conn)

    def http_exception(self, request: Request, exc: Exception) -> Response:
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}:
            return Response(status_code=exc.status_code, headers=exc.headers)
        return PlainTextResponse(exc.detail, status_code=exc.status_code, headers=exc.headers)

    async def websocket_exception(self, websocket: WebSocket, exc: Exception) -> None:
        assert isinstance(exc, WebSocketException)
        await websocket.close(code=exc.code, reason=exc.reason)  # pragma: no cover
