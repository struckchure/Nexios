from typing import Tuple,Dict,Any
import re
from dataclasses import dataclass
from io import BytesIO
from urllib.parse import quote_plus,unquote_plus

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

async def parse_multipart_data(self) -> Tuple[Dict[str, str], Dict[str, any]]:
        """Parse multipart form data, returning both form fields and files."""
        if self._form_data is None or self._files is None:
            content_type = self.headers.get('content-type', '')
            if not content_type.startswith('multipart/form-data'):
                return {}, {}
            
            # Extract boundary from content type
            match = re.search(r'boundary=([^;]+)', content_type)
            if not match:
                return {}, {}
            
            boundary = match.group(1)
            body = await self.body
            
            parser = MultipartParser(boundary)
            self._form_data, self._files = await parser.parse(body)
        
        return {**self._form_data, **self._files}

def parse_form_urlencoded(body: str) -> Dict[str, Any]:
    """
    Parse application/x-www-form-urlencoded data into a dictionary.
    Handles multiple values for the same key by returning them in a list.
    """
    parsed_data = {}
    if not body:
        return parsed_data
        
    pairs = body.split('&')
    for pair in pairs:
        if '=' not in pair:
            continue
        key, value = pair.split('=', 1)
        key = unquote_plus(key)
        value = unquote_plus(value)
        
        if key in parsed_data:
            if isinstance(parsed_data[key], list):
                parsed_data[key].append(value)
            else:
                parsed_data[key] = [parsed_data[key], value]
        else:
            parsed_data[key] = value
            
    return parsed_data

class MultipartParser:
    """Parser for multipart/form-data content."""
    def __init__(self, boundary: str):
        self.boundary = boundary.encode()
        self.boundary_length = len(self.boundary)
    
    def parse_headers(self, headers_raw: bytes) -> Dict[str, str]:
        """Parse the headers section of a multipart part."""
        headers = {}
        for header_line in headers_raw.split(b'\r\n'):
            if b':' in header_line:
                name, value = header_line.split(b':', 1)
                headers[name.decode().lower()] = value.decode().strip()
        return headers
    
    def get_content_disposition(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Parse content-disposition header to get field name and filename."""
        if 'content-disposition' not in headers:
            return {}
        
        disposition = headers['content-disposition']
        params = {}
        for param in disposition.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip()] = value.strip().strip('"\'')
        return params

    async def parse(self, body: bytes) -> Tuple[Dict[str, str], Dict[str, UploadedFile]]:
        """Parse multipart form data into fields and files."""
        form_data = {}
        files = {}
        
        parts = body.split(b'--' + self.boundary)
        
        # Skip the first empty part and the last boundary mark
        for part in parts[1:-1]:
            # Remove leading/trailing whitespace and CRLF
            part = part.strip(b'\r\n')
            if not part:
                continue
            
            # Split headers and content
            headers_end = part.find(b'\r\n\r\n')
            if headers_end == -1:
                continue
                
            headers_raw = part[:headers_end]
            content = part[headers_end + 4:]
            
            headers = self.parse_headers(headers_raw)
            disposition = self.get_content_disposition(headers)
            
            if not disposition.get('name'):
                continue
                
            field_name = disposition['name']
            
            if 'filename' in disposition:
                # This is a file upload
                filename = disposition['filename']
                content_type = headers.get('content-type', 'application/octet-stream')
                file_obj = BytesIO(content)
                uploaded_file = UploadedFile(
                    filename=filename,
                    content_type=content_type,
                    body=file_obj,
                    size=len(content)
                )
                files[field_name] = uploaded_file
            else:
                # This is a regular form field
                form_data[field_name] = content.decode()
        
        return form_data, files 