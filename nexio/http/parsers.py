#NOTE: be careful arrounf here thise gave me a tough time abeg
from typing import Tuple,Dict,Any
import re
from io import BytesIO
from urllib.parse import unquote_plus
from nexio.utils.files import UploadedFile


async def parse_multipart_data(self) -> Tuple[Dict[str, str], Dict[str, any]]:
        if self._form_data is None or self._files is None:
            content_type = self.headers.get('content-type', '')
            if not content_type.startswith('multipart/form-data'):
                return {}, {}
            
            match = re.search(r'boundary=((?:[^;"]+|"[^"]+"))', content_type)
            if not match:
                return {}, {}
            
            boundary = match.group(1).strip('"').strip()
            if boundary.startswith('--'):
                boundary = boundary[2:]
            
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
        self.prefixed_boundary = b'--' + self.boundary
        self.possible_boundaries = [
            b'\r\n--' + self.boundary,  # Standard boundary with CRLF
            b'\n--' + self.boundary,    # Unix-style newline
            b'--' + self.boundary,      # No newline prefix
            self.boundary               # Raw boundary
        ]
    
    def parse_headers(self, headers_raw: bytes) -> Dict[str, str]:
        """Parse the headers section of a multipart part."""
        headers = {}
        for header_line in headers_raw.split(b'\r\n'):
            if not header_line:
                continue
            if b':' in header_line:
                name, value = header_line.split(b':', 1)
                headers[name.decode().lower().strip()] = value.decode().strip()
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

    def split_parts(self, body: bytes) -> list:
        """Split the body into parts using any valid boundary format."""
        # First try splitting with most common boundary format
        parts = body.split(b'\r\n--' + self.boundary)
        
        # If that didn't work (only one part), try other formats
        if len(parts) == 1:
            for boundary in self.possible_boundaries:
                parts = body.split(boundary)
                if len(parts) > 1:
                    break
        
        return parts

    async def parse(self, body: bytes) -> Tuple[Dict[str, str], Dict[str, UploadedFile]]:
        """Parse multipart form data into fields and files."""
        form_data = {}
        files = {}
        
        if not body:
            return form_data, files

        # Split into parts using flexible boundary matching
        parts = self.split_parts(body)
        
        # Process each part
        for part in parts:
            # Skip empty parts and the final boundary marker
            if not part or part.strip() in [b'', b'--']:
                continue
            
            # Clean up part boundaries
            part = part.strip(b'\r\n')
            if not part:
                continue
            
            # Split headers and content
            headers_end = part.find(b'\r\n\r\n')
            if headers_end == -1:
                continue
                
            headers_raw = part[:headers_end]
            content = part[headers_end + 4:]
            
            # Clean up any trailing boundaries
            for boundary in self.possible_boundaries:
                if content.endswith(boundary + b'--'):
                    content = content[:-len(boundary + b'--')]
                elif content.endswith(boundary):
                    content = content[:-len(boundary)]
            
            headers = self.parse_headers(headers_raw)
            disposition = self.get_content_disposition(headers)
            
            if not disposition.get('name'):
                continue
                
            field_name = disposition['name']
            
            if 'filename' in disposition:
                # This is a file upload
                filename = disposition['filename']
                content_type = headers.get('content-type', 'application/octet-stream')
                file_obj = BytesIO(content.strip())
                uploaded_file = UploadedFile(
                    filename=filename,
                    content_type=content_type,
                    body=file_obj,
                    size=len(content.strip())
                )
                files[field_name] = uploaded_file
            else:
                # This is a regular form field
                form_data[field_name] = content.strip().decode()
        
        return form_data, files