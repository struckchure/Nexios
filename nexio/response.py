from starlette.responses import Response,JSONResponse
class CustomResponse:
    def __init__(self):
        self._status_code = 200
        self._body = None
        self._media_type = "application/json"
        self._response = None

    def send(self, content, status_code=200):
        self._status_code = status_code
        self._body = content
        self._media_type = "text/plain"
        return self

    def json(self, data, status_code=200):
        self._status_code = status_code
        self._body = data
        self._media_type = "application/json"
        

    def status(self, status_code):
        self._status_code = status_code
        

    def get_response(self):
        if self._response is None:
            if self._media_type == "application/json":
                self._response = JSONResponse(
                    content=self._body,
                    status_code=self._status_code
                )
            else:
                self._response = Response(
                    content=self._body,
                    status_code=self._status_code,
                    media_type=self._media_type
                )
        return self._response

    async def __call__(self, scope, receive, send):
        response = self.get_response()
        await response(scope, receive, send)
