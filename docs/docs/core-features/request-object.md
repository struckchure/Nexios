# Request Object Documentation for ASGI Applications

## Overview
The `Request` class provides a high-level interface for handling HTTP requests in ASGI applications. It manages request data parsing, header handling, cookies, file uploads, and other HTTP-specific functionality.

## Basic Usage

### Creating a Request Object
```python
async def app(scope, receive, send):
    if scope["type"] == "http":
        request = Request(scope, receive, send)
        # Use request object...
```

### Key Properties

#### URL and Path Information
```python
async def handler(request):
    # Get full URL
    full_url = str(request.url)  # e.g., "https://example.com/path?query=value"
    
    # Get base URL without query parameters
    base_url = request.base_url  # e.g., "https://example.com"
    
    # Build absolute URI
    absolute_uri = request.build_absolute_uri("/new/path")
    # Result: "https://example.com/new/path"
```

#### Headers and Cookies
```python
async def handler(request):
    # Access headers
    user_agent = request.user_agent
    content_type = request.content_type
    custom_header = request.get_header("x-custom-header")
    
    # Access cookies
    session_id = request.cookies.get("session_id")
    user_prefs = request.cookies.get("user_preferences")
```

#### Query Parameters
```python
async def handler(request):
    # Get all query parameters
    all_params = request.query_params
    
    # Get specific parameter
    page = request.query_params.get("page")
    
    # Handle multiple values for same parameter
    tags = request.query_params.get("tags")
    if isinstance(tags, list):
        # Handle multiple tags
        for tag in tags:
            print(f"Processing tag: {tag}")
```

### Request Body Handling

#### JSON Data
```python
async def json_handler(request):
    if request.content_type == "application/json":
        data = await request.json
        username = data.get("username")
        email = data.get("email")
        
        return {
            "status": "success",
            "received": {
                "username": username,
                "email": email
            }
        }
```

#### Form Data
```python
async def form_handler(request):
    if request.content_type == "application/x-www-form-urlencoded":
        form_data = await request.form_data
        name = form_data.get("name")
        message = form_data.get("message")
        
        return {
            "status": "success",
            "received": {
                "name": name,
                "message": message
            }
        }
```

#### File Uploads
```python
async def file_upload_handler(request):
    if request.content_type == "multipart/form-data":
        files = await request.files
        form_data = await request.form_data
        
        # Handle uploaded file
        uploaded_file = files.get("document")
        if uploaded_file:
            filename = uploaded_file.filename
            content = uploaded_file.file.read()
            
            # Process the file...
            
            return {
                "status": "success",
                "filename": filename,
                "size": len(content)
            }
```

### Streaming Request Body
```python
async def stream_handler(request):
    async for chunk in request.stream():
        # Process chunk of data
        await process_chunk(chunk)
```

## Advanced Usage Examples

### Complete ASGI Application Example
```python
from typing import Dict, Any

class MyASGIApp:
    async def __init__(self):
        self.routes = {
            "/upload": self.handle_upload,
            "/profile": self.handle_profile,
            "/api/data": self.handle_api_data
        }

    async def __call__(self, scope: Dict[str, Any], receive, send):
        if scope["type"] != "http":
            return
            
        request = Request(scope, receive, send)
        path = scope["path"]
        
        handler = self.routes.get(path)
        if handler:
            response = await handler(request)
            # Convert response to ASGI response format...
        else:
            # Handle 404...

    async def handle_upload(self, request: Request):
        if request.method == "POST":
            files = await request.files
            form_data = await request.form_data
            
            # Process upload...
            
    async def handle_profile(self, request: Request):
        if request.method == "GET":
            user_id = request.query_params.get("id")
            # Get user profile...
            
    async def handle_api_data(self, request: Request):
        if request.method == "POST":
            json_data = await request.json
            # Process API request...
```

### Request Validation Example
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserCreateRequest:
    username: str
    email: str
    age: Optional[int] = None

async def create_user_handler(request: Request):
    try:
        # Validate content type
        if request.content_type != "application/json":
            return {"error": "Content-Type must be application/json"}
            
        # Get and validate data
        data = await request.json
        user_data = UserCreateRequest(
            username=data["username"],
            email=data["email"],
            age=data.get("age")
        )
        
        # Process validated data...
        
    except KeyError as e:
        return {"error": f"Missing required field: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
```

### Middleware Example Using Request Object
```python
class RequestMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive, send)
            
            # Add custom properties to request state
            request.state.user = await self.get_user(request)
            request.state.start_time = time.time()
            
            # Log request
            print(f"Request: {request.method} {request.url}")
            
            # Continue with request handling
            await self.app(scope, receive, send)
            
    async def get_user(self, request: Request):
        auth_header = request.get_header("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Validate token and get user...
```

## Error Handling

### Client Disconnect Detection
```python
async def long_running_handler(request: Request):
    try:
        async for chunk in request.stream():
            if await request.is_disconnected():
                # Clean up and exit
                return
                
            # Process chunk...
            
    except ClientDisconnect:
        # Handle client disconnect
        cleanup_resources()
```

## Notes and Best Practices

1. **Body Access**: The request body can only be read once. Cache the result if you need to access it multiple times.
   ```python
   # Good practice
   body_data = await request.json
   # Use body_data multiple times...
   ```

2. **Content Type Validation**: Always verify the content type before processing request body:
   ```python
   if request.content_type != expected_content_type:
       return {"error": f"Expected {expected_content_type}"}
   ```

3. **Memory Consideration**: For large file uploads, use streaming when possible:
   ```python
   async def handle_large_upload(request: Request):
       total_size = 0
       async for chunk in request.stream():
           total_size += len(chunk)
           # Process chunk without loading entire file into memory
   ```

4. **State Management**: Use request.state for request-scoped data:
   ```python
   request.state.user = current_user
   request.state.db_session = session
   ```

This documentation covers the core functionality of the Request object and provides practical examples for common use cases in ASGI applications. The Request object is designed to handle various HTTP scenarios while providing a clean, async-first API for developers.