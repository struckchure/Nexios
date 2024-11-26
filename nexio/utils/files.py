from io import BytesIO
from dataclasses import dataclass
@dataclass
class UploadedFile:
    """Represents an uploaded file in the request."""
    filename: str
    content_type: str
    body: BytesIO
    size: int
    
    async def read(self) -> bytes:
        """Read the entire file content."""
        return self.body.read()
    
    async def save(self, path: str) -> None:
        """Save the file to the specified path."""
        with open(path, 'wb') as f:
            f.write(await self.read())

    
    def __repr__(self) -> str:
        return f"<Uploded file name={self.filename}"
    
    def __str__(self) -> str:
        return f"<Uploded file name={self.filename}>"