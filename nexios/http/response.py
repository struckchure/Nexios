from datetime import datetime, timedelta
from email.utils import formatdate
from typing import Any, Dict, List, Optional, Tuple, Union, Sequence, Generator
from pathlib import Path
import json
from base64 import b64encode
from hashlib import sha1
import mimetypes
import typing
import os
import anyio
from typing import AsyncIterator
from anyio import AsyncFile
Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class Response:
    """
    Base ASGI-compatible Response class with support for cookies, caching, and custom headers.
    """
    
    STATUS_CODES = {
        200: "OK",
        201: "Created",
        204: "No Content",
        301: "Moved Permanently",
        302: "Found",
        304: "Not Modified",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    }

    def __init__(
        self,
        body: Union[JSONType, Any] = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "text/plain",
    ):
        self.status_code: int = status_code
        self._headers: Dict[str, Any] = {}
        self._cookies: List[Tuple[str, str, Dict[str, Any]]] = []
        
        self.headers = headers or {}
        
        if isinstance(body, dict):
            self._body = json.dumps(body).encode('utf-8')
            self.content_type = "application/json"
        elif isinstance(body, str):
            self._body = body.encode('utf-8')
            self.content_type = content_type
        elif isinstance(body, bytes):
            self._body = body
            self.content_type = content_type
        else:
            raise TypeError("Body must be str, bytes, or dict")

        self.headers['content-length'] = str(len(self._body))
        self.headers['content-type'] = self.content_type

    def set_cookie(
        self,
        key: str,
        value: Optional[Union[str, None]],
        max_age: Optional[int] = None,
        expires: Optional[Union[str, datetime, int]] = None,
        path: Optional[str] = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Optional[str] = None
    ) -> None:
        """Set a cookie with the given parameters."""
        cookie_options: Dict[str, Any] = {}
        
        if max_age is not None:
            cookie_options['max-age'] = str(max_age)
        
        if expires is not None:
            if isinstance(expires, datetime):
                cookie_options['expires'] = formatdate(expires.timestamp(), usegmt=True)
            else:
                cookie_options['expires'] = expires
        
        if path is not None:
            cookie_options['path'] = path
            
        if domain is not None:
            cookie_options['domain'] = domain
            
        if secure:
            cookie_options['secure'] = True
            
        if httponly:
            cookie_options['httponly'] = True
            
        if samesite is not None:
            cookie_options['samesite'] = samesite
            
        self._cookies.append((key, value, cookie_options))  # type: ignore

    def delete_cookie(self, key: str, path: str = "/", domain: Optional[str] = None) -> None:
        """Delete a cookie by setting its expiry to the past."""
        self.set_cookie(
            key=key,
            value=None,
            max_age=0,
            expires=0,
            path=path,
            domain=domain
        )

    def enable_caching(self, max_age: int = 3600, private: bool = True) -> None:
        """Enable caching with the specified max age (in seconds)."""
        cache_control: List[str] = []
        if private:
            cache_control.append("private")
        else:
            cache_control.append("public")
            
        cache_control.append(f"max-age={max_age}")
        self.headers["cache-control"] = ", ".join(cache_control)
        
        etag = self._generate_etag()
        self.headers["etag"] = etag
        
        expires = datetime.utcnow() + timedelta(seconds=max_age)  # type: ignore
        self.headers["expires"] = formatdate(expires.timestamp(), usegmt=True)

    def disable_caching(self) -> None:
        """Disable caching for this response."""
        self.headers["cache-control"] = "no-store, no-cache, must-revalidate, max-age=0"
        self.headers["pragma"] = "no-cache"
        self.headers["expires"] = "0"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Make the response callable as an ASGI application."""
        self.status_code = 200 if scope["method"].lower() == "options" else self.status_code

        headers: List[Sequence[Union[str, bytes]]] = []
        for k, v in self.headers.items():
            if k == 'set-cookie':
                if isinstance(v, list):
                    for cookie in v:
                        headers.append([b'set-cookie', cookie.encode('utf-8')])
                else:
                    headers.append([b'set-cookie', v.encode('utf-8')])
            else:
                headers.append([k.encode('utf-8'), v.encode('utf-8')])
        
        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': headers,
        })
        
        await send({
            'type': 'http.response.body',
            'body': self._body,
        })

    def _serialize_cookie(self, key: str, value: str, options: Dict[str, Any]) -> str:
        """Serialize a single cookie into a Set-Cookie header value."""
        cookie = f"{key}={value}"
        for opt_key, opt_value in options.items():
            if isinstance(opt_value, bool):
                if opt_value:
                    cookie += f"; {opt_key}"
            else:
                cookie += f"; {opt_key}={opt_value}"
        return cookie

    def _generate_etag(self) -> str:
        """Generate an ETag for the response content."""
        content_hash = sha1()
        content_hash.update(self._body)
        return f'W/"{b64encode(content_hash.digest()).decode("utf-8")}"'


class JSONResponse(Response):
    """
    Response subclass for JSON content.
    """
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        indent: Optional[int] = None,
        ensure_ascii: bool = True,
    ):
        try:
            body = json.dumps(
                content,
                indent=indent,
                ensure_ascii=ensure_ascii,
                allow_nan=False,
                default=str
            )
        except (TypeError, ValueError) as e:
            raise ValueError(f"Content is not JSON serializable: {str(e)}")
            
        super().__init__(
            body=body,
            status_code=status_code,
            headers=headers,
            content_type="application/json"
        )


class HTMLResponse(Response):
    """
    Response subclass for HTML content.
    """
    def __init__(
        self,
        content: Union[str, JSONType],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            body=content,
            status_code=status_code,
            headers=headers,
            content_type="text/html; charset=utf-8"
        )


class FileResponse(Response):
    """
    Enhanced FileResponse class with AnyIO for asynchronous file streaming,
    support for range requests, and multipart responses.
    """
    chunk_size = 64 * 1024  # 64KB chunks

    def __init__(
        self,
        path: Union[str, Path],
        filename: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_disposition_type: str = "attachment",
    ):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not self.path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        self.filename = filename or self.path.name
        self.content_disposition_type = content_disposition_type
        self.status_code = status_code

        self.headers = headers or {}
        content_type, _ = mimetypes.guess_type(str(self.path))
        self.headers['content-type'] = content_type or 'application/octet-stream'
        self.headers['content-disposition'] = f'{content_disposition_type}; filename="{self.filename}"'
        self.headers['accept-ranges'] = 'bytes'  
        self.headers['content-length'] = str(self.path.stat().st_size)

        self._ranges: List[Tuple[int, int]] = []
        self._multipart_boundary: Optional[str] = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle the ASGI response, including range requests."""
        
        range_header = dict(scope.get('headers', {})).get('range')
        
        if range_header:
            self._handle_range_header(range_header)

        await self._send_response(scope, receive, send)

    def _handle_range_header(self, range_header: str) -> None:
        """Parse and validate the Range header."""
        file_size = self.path.stat().st_size
        try:
            unit, ranges = range_header.strip().split('=')
            if unit != 'bytes':
                raise ValueError("Only byte ranges are supported")

            self._ranges = []
            for range_str in ranges.split(','):
                start, end = range_str.split('-')
                start = int(start) if start else 0
                end = int(end) if end else file_size - 1

                if start < 0 or end >= file_size or start > end:
                    raise ValueError("Invalid range")

                self._ranges.append((start, end))

            if len(self._ranges) == 1:
                start, end = self._ranges[0]
                self.headers['content-range'] = f'bytes {start}-{end}/{file_size}'
                self.headers['content-length'] = str(end - start + 1)
                self.status_code = 206 

            elif len(self._ranges) > 1:
                self._multipart_boundary = self._generate_multipart_boundary()
                self.headers['content-type'] = f'multipart/byteranges; boundary={self._multipart_boundary}'
                self.status_code = 206  

        except ValueError as _:
            self.headers['content-range'] = f'bytes */{file_size}'
            self.status_code = 416  

    async def _send_response(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Send the file response, handling range requests and multipart responses."""
        headers: List[Sequence[Union[str, bytes]]] = []
        for k, v in self.headers.items():
            if k == 'set-cookie':
                if isinstance(v, list):
                    for cookie in v:
                        headers.append([b'set-cookie', cookie.encode('utf-8')])
                else:
                    headers.append([b'set-cookie', v.encode('utf-8')])
            else:
                headers.append([k.encode('utf-8'), v.encode('utf-8')])

        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': headers,
        })

        if self.status_code == 416: 
            await send({
                'type': 'http.response.body',
                'body': b'',
            })
            return

        async with await anyio.open_file(self.path, 'rb') as file:
            
            if self._multipart_boundary:
                for start, end in self._ranges:
                    await self._send_multipart_chunk(file, start, end, send)
                await send({
                    'type': 'http.response.body',
                    'body': f'--{self._multipart_boundary}--\r\n'.encode('utf-8'),
                    'more_body': False,
                })
            elif self._ranges:
                start, end = self._ranges[0]
                await self._send_range(file, start, end, send) #type:ignore
            else:
                await self._send_full_file(file, send) #type:ignore

    async def _send_full_file(self, file: AsyncIterator[bytes], send: Send) -> None:
        """Send the entire file in chunks using AnyIO."""
        while True:
            chunk = await file.read(self.chunk_size) #type:ignore
            if not chunk:
                break
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True,
            })
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False,
        })

    async def _send_range(self, file: AsyncFile[bytes], start: int, end: int, send: Send) -> None:
        """Send a single range of the file using AnyIO."""
        await file.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk_size = min(self.chunk_size, remaining)
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True,
            })
            remaining -= len(chunk)
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False,
        })

    async def _send_multipart_chunk(self, file: AsyncFile[bytes], start: int, end: int, send: Send) -> None:
        """Send a multipart chunk for a range using AnyIO."""
        await file.seek(start)
        remaining = end - start + 1

        boundary = f'--{self._multipart_boundary}\r\n'
        headers = f'Content-Type: {self.headers["content-type"]}\r\nContent-Range: bytes {start}-{end}/{self.path.stat().st_size}\r\n\r\n'
        await send({
            'type': 'http.response.body',
            'body': (boundary + headers).encode('utf-8'),
            'more_body': True,
        })

        while remaining > 0:
            chunk_size = min(self.chunk_size, remaining)
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True,
            })
            remaining -= len(chunk)

    def _generate_multipart_boundary(self) -> str:
        """Generate a unique multipart boundary string."""
        return f"boundary_{os.urandom(16).hex()}"


class StreamingResponse(Response):
    """
    Response subclass for streaming content.
    """
    def __init__(
        self,
        content: AsyncIterator[Union[str, bytes]],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "text/plain",
    ):
        self.content_iterator = content
        self.status_code = status_code
        self._headers: Dict[str, Any] = {}
        self._cookies: List[Tuple[str, str, Dict[str, Any]]] = []
        
        self.headers = headers or {}
        self.content_type = content_type
        self.headers['content-type'] = self.content_type
        
        self.headers.pop('content-length', None)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Stream the content."""
        headers: List[Sequence[Union[str, bytes]]] = []
        for k, v in self.headers.items():
            if k == 'set-cookie':
                if isinstance(v, list):
                    for cookie in v:
                        headers.append([b'set-cookie', cookie.encode('utf-8')])
                else:
                    headers.append([b'set-cookie', v.encode('utf-8')])
            else:
                headers.append([k.encode('utf-8'), v.encode('utf-8')])

        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': headers,
        })

        async for chunk in self.content_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True
            })
            
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False
        })


class RedirectResponse(Response):
    """
    Response subclass for HTTP redirects.
    """
    def __init__(
        self,
        url: str,
        status_code: int = 302,
        headers: Optional[Dict[str, str]] = None,
    ):
        if not 300 <= status_code < 400:
            raise ValueError("Status code must be a valid redirect status")
            
        headers = headers or {}
        headers['location'] = str(url)
        
        super().__init__(
            body="",
            status_code=status_code,
            headers=headers
        )


class NexiosResponse:
    """
    A wrapper class that provides a fluent interface for different response types.
    """
    def __init__(self):
        self._status_code = 200
        self._body: Optional[JSONType] = None
        self._content_type = "application/json"
        self.headers: Dict[str, Any] = {}
        self._response: Optional[Response] = None
        self._cookies: List[Dict[str, Any]] = []
        self._delete_cookies: List[Dict[str, Any]] = []

    def send(self, content: Any, status_code: Optional[int] = None, headers: Dict[str, Any] = {}):
        """Send plain text or HTML content."""
        self._status_code = status_code or self._status_code or 200  # type: ignore
        self.headers.update(headers)
        self._body = content
        self._content_type = "text/plain"
        return self
    
    def text(self, content: JSONType, status_code: Optional[int] = None, headers: Dict[str, Any] = {}):
        """Send plain text or HTML content."""
        self._status_code = status_code or self._status_code or 200  # type: ignore
        self.headers.update(headers)
        self._body = content
        self._content_type = "text/plain"
        return self

    def json(self, data: Union[str, List[Any], Dict[str, Any]], status_code: Optional[int] = None, headers: Dict[str, Any] = {}):
        """Send JSON response."""
        self._status_code = status_code or self._status_code or 200  # type: ignore
        self.headers.update(headers)

        self._body = data
        self._content_type = "application/json"
        return self

    def empty(self, status_code: Optional[int] = None, headers: Dict[str, Any] = {}):
        """Send an empty response."""
        self._status_code = status_code or self._status_code or 200  # type: ignore
        self.headers.update(headers)

        self._body = None
        self._content_type = "application/json"
        return self
        
    def html(self, content: str, status_code: Optional[int] = None, headers: Dict[str, Any] = {}):
        """Send HTML response."""
        self._status_code = status_code or self._status_code or 200  # type: ignore
        self.headers.update(headers)
        
        self._body = content
        self._content_type = "text/html; charset=utf-8"
        return self

    def file(self, path: str, filename: Optional[str] = None, content_disposition_type: str = "attachment"):
        """Send file response."""
        self._response = FileResponse(
            path=path,
            filename=filename,
            status_code=self._status_code,  # type: ignore
            headers=self.headers,
            content_disposition_type=content_disposition_type,
        )
        return self

    def stream(self, iterator: Generator[Union[str, bytes]], content_type: str = "text/plain"):
        """Send streaming response."""
        self._response = StreamingResponse(
            content=iterator,  # type: ignore
            status_code=self._status_code,
            headers=self.headers,
            content_type=content_type
        )
        return self

    def redirect(self, url: str, status_code: int = 302):
        """Send redirect response."""
        self._response = RedirectResponse(
            url=url,
            status_code=status_code,
            headers=self.headers
        )
        return self

    def status(self, status_code: int):
        """Set response status code."""
        self._status_code = status_code
        return self

    def header(self, key: str, value: str):
        """Set a response header."""
        self.headers[key.lower()] = str(value)
        return self

    def set_cookie(
        self,
        key: str,
        value: Optional[str],
        max_age: Optional[int] = None,
        expires: Optional[Union[str, datetime, int]] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = True,
        httponly: bool = False,
        samesite: Optional[str] = None
    ):
        """Set a response cookie."""
        self._cookies.append({
            'key': key,
            'value': value,
            'max_age': max_age,
            'expires': expires,
            'path': path,
            'domain': domain,
            'secure': secure,
            'httponly': httponly,
            'samesite': samesite
        })
        return self
    
    def delete_cookie(
        self,
        key: str,
        value: Optional[str] = None,
        max_age: Optional[int] = None,
        expires: Optional[Union[str, datetime]] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Optional[str] = None
    ):
        """Delete a response cookie."""
        self._delete_cookies.append({
            'key': key,
            'value': value,
            'max_age': max_age,
            'expires': expires,
            'path': path,
            'domain': domain,
            'secure': secure,
            'httponly': httponly,
            'samesite': samesite
        })
        return self

    def cache(self, max_age: int = 3600, private: bool = True):
        """Enable response caching."""
        if self._response is None:
            self._get_base_response().enable_caching(max_age, private)
        else:
            self._response.enable_caching(max_age, private)
        return self

    def no_cache(self):
        """Disable response caching."""
        if self._response is None:
            self._get_base_response().disable_caching()
        else:
            self._response.disable_caching()
        return self

    def resp(
        self,
        body: Union[JSONType, Any] = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "text/plain",
    ):
        """
        Provides access to the purest form of the response object.
        """
        _resp = Response(
            body=body,
            status_code=status_code,
            headers=headers,
            content_type=content_type
        )
        self._response = _resp
        return self

    def _get_base_response(self) -> Response:
        """Get the appropriate response type based on content type."""
        if self._response is not None:
            return self._response

        if self._content_type == "application/json":
            self._response = JSONResponse(
                content=self._body,
                status_code=self._status_code,
                headers=self.headers
            )
        elif self._content_type == "text/html; charset=utf-8":
            self._response = HTMLResponse(
                content=self._body,
                status_code=self._status_code,
                headers=self.headers
            )
        else:
            self._response = Response(
                body=self._body,
                status_code=self._status_code,
                headers=self.headers,
                content_type=self._content_type
            )

        for cookie in self._cookies:
            self._response.set_cookie(**cookie)

        if len(self._delete_cookies) > 0:
            for cookie in self._delete_cookies:
                self._response.delete_cookie(**cookie)

        return self._response

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Make the response ASGI-compatible."""
        self._status_code = 200 if scope['method'].lower() == "options" else self._status_code
        response = self._get_base_response()
        await response(scope, receive, send)
        
    def __str__(self):
        return f"Response [{self._status_code} {self._body}]"