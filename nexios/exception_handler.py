from __future__ import annotations
import typing
from nexios.exceptions import HTTPException
from nexios.http import Request,Response
from nexios.websockets import WebSocket
from nexios.config import get_config
def _lookup_exception_handler(exc_handlers, exc: Exception) :
    
    for cls in type(exc).__mro__:
        if cls in exc_handlers:
            return exc_handlers[cls]
    return None
async def wrap_app_handling_exceptions(request :Request, response :Response, call_next, exception_handlers, status_handlers) -> Response:
   
    try:
        exception_handlers, status_handlers =  exception_handlers, status_handlers
    except KeyError:
        exception_handlers, status_handlers = {}, {}

    

    try:
        await call_next()
    except Exception as exc:
        handler = None

        if isinstance(exc, HTTPException):
            handler = status_handlers.get(exc.status_code)

        if handler is None:
            handler = _lookup_exception_handler(exception_handlers, exc)
            if not handler:
                raise exc
            return  await handler(request,response,exc)

       


class ExceptionMiddleware:
    def __init__(self ) -> None:
        self.debug = get_config().debug or False # TODO: We ought to handle 404 cases if debug is set.
        self._status_handlers = {}
        self._exception_handlers = {HTTPException: self.http_exception}
       
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

    async def __call__(self, request: Request,response :Response,call_next) -> Response:
        request.exception_handlers = (self._exception_handlers, self._status_handlers)

       

        return await wrap_app_handling_exceptions(
            request=request,
            response=response,
            call_next=call_next,
            exception_handlers=self._exception_handlers,
            status_handlers=self._status_handlers
            
            
        )

    async def http_exception(self, request: Request,response:Response, exc: Exception) -> Response:
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}:
            return response.empty(status_code=exc.status_code, headers=exc.headers)
        return response.text(exc.detail, status_code=exc.status_code, headers=exc.headers)

