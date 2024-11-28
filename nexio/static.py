from pathlib import Path
import mimetypes
import os
from typing import Union, Optional
from nexio.http.response import NexioResponse
import aiofiles
import stat

class StaticFileResponse(NexioResponse):
    def __init__(self, 
                 file_path: Union[str, Path], 
                 chunk_size: int = 8192,
                 filename: Optional[str] = None,
                 content_type: Optional[str] = None):
        super().__init__()
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.filename = filename or self.file_path.name
        
        # Determine content type
        if content_type is None:
            content_type, _ = mimetypes.guess_type(str(file_path))
        self.content_type = content_type or 'application/octet-stream'
        
    async def __call__(self, scope, receive, send):
        if not self.file_path.exists():
            response = NexioResponse(status_code=404)
            await response(scope, receive, send)
            return

        file_size = self.file_path.stat().st_size
        
        # Set headers
        headers = [
            (b"content-type", self.content_type.encode()),
            (b"content-length", str(file_size).encode()),
            (b"content-disposition", f'attachment; filename="{self.filename}"'.encode()),
        ]

        # Send initial response
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": headers
        })

        # Stream file contents
        async with aiofiles.open(self.file_path, mode='rb') as file:
            while chunk := await file.read(self.chunk_size):
                await send({
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True
                })

        # Send final empty chunk
        await send({
            "type": "http.response.body",
            "body": b"",
            "more_body": False
        })

class StaticFilesHandler:
    def __init__(self, directory: Union[str, Path], url_prefix: str = "/static/"):
        self.directory = Path(directory)
        self.url_prefix = url_prefix.strip("/") + "/"
        
        if not self.directory.exists():
            raise ValueError(f"Directory {directory} does not exist")
        
        if not self.directory.is_dir():
            raise ValueError(f"{directory} is not a directory")

    async def __call__(self, request, response, **kwargs):
        # Remove url prefix and clean path
        path = request.url.path.replace("/" + self.url_prefix, "", 1)
        file_path = (self.directory / path).resolve()
        
        # Security check - ensure file is within base directory
        try:
            file_path.relative_to(self.directory)
        except ValueError:
            
            return  response.json("Not Found",status_code = 404)

        if not file_path.exists() or not file_path.is_file():
            return  response.json("Not Found",status_code = 404)
            

        return await StaticFileResponse(file_path)(
            request.scope, request.receive, request.send
        )