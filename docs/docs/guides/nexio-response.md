# Nexio Response 

`NexioResponse` is an object that represents the HTTP response sent from the server to the client in the Nexio framework. It allows for setting headers, cookies, status codes, and other response attributes.

## Core Methods

### .status(code)
Sets the HTTP status code for the response.

```python
@app.route("/status")
async def route_handler(request, response):
    return response.status(201)  # Created
```

Common status codes:
- `200`: OK (default)
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

### .send(content, status_code=200)
Sends a plain text response to the client.

```python
@app.route("/text")
async def route_handler(request, response):
    return response.send("Hello world", status_code=201)
```

### .json(data, status_code=200)
Sends a JSON response with automatic serialization.

```python
@app.route("/json")
async def route_handler(request, response):
    return response.json({
        "status": "OK",
        "data": {"user": "John"}
    })
```

### .html(content, status_code=200)
Sends an HTML response with proper content-type headers.

```python
@app.route("/html")
async def route_handler(request, response):
    return response.html("<h1>Welcome</h1>")
```

### .header(key, value)
Sets a custom HTTP header.

```python
@app.route("/headers")
async def route_handler(request, response):
    return response.header("X-Custom", "value").send("Custom Header Added")
```

## File Handling

### .file(path, filename=None, content_disposition_type="attachment")
Streams a file as response with optional custom filename.

```python
@app.route("/download")
async def route_handler(request, response):
    return response.file(
        path="files/document.pdf",
        filename="report.pdf"
    )
```

### .stream(iterator, content_type="text/plain")
Creates a streaming response for large data sets.

```python
@app.route("/stream")
async def route_handler(request, response):
    def generate():
        for i in range(100):
            yield f"data chunk {i}\n"
    
    return response.stream(generate())
```

## Cookie Management

### .set_cookie(key, value, **options)
Sets a cookie with various optional parameters.

```python
@app.route("/cookies")
async def route_handler(request, response):
    return response.set_cookie(
        "session", 
        "abc123",
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="Strict"
    )
    return response.send("Cookie Set")
```

Cookie options:
- `max_age`: Lifetime in seconds
- `expires`: Explicit expiration date
- `path`: Cookie path (default: "/")
- `domain`: Cookie domain
- `secure`: HTTPS-only flag
- `httponly`: JavaScript access prevention
- `samesite`: Cross-site request handling

### .delete_cookie(key, **options)
Removes a cookie by setting its expiration to the past.

```python
@app.route("/remove-cookie")
async def route_handler(request, response):
    response.delete_cookie("session")
    return response.send("Cookie Removed")
```

## Caching Control

### .cache(max_age=3600, private=True)
Enables response caching with specified options.

```python
@app.route("/cached")
async def route_handler(request, response):
    response.cache(
        max_age=60,  # 60 seconds
        private=True
    )
    response.json({"data": "cached"})
```

Cache properties:
- `max_age`: Cache duration in seconds
- `private`: Client-only caching
- `public`: Shared caching allowed

### .no_cache()
Disables caching for the response.

```python
@app.route("/no-cache")
async def route_handler(request, response):
    response.no_cache()
    return response.send("Not cached")
```

## Redirection

### .redirect(url, status_code=302)
Performs an HTTP redirect to the specified URL.

```python
@app.route("/redirect")
async def route_handler(request, response):
    return response.redirect("/new-location")
```



## Error Handling

When sending error responses, it's recommended to include appropriate status codes and messages:

```python
@app.route("/error")
async def route_handler(request, response):
    return response.json({
        "error": "Bad Request",
        "message": "Invalid parameters"
    },status_code = 400)
```

## Performance Considerations

1. Use streaming responses for large files or data sets
2. Enable caching for static or rarely-changing content
3. Set appropriate content-type headers
4. Use compression when possible
5. Include ETags for cache validation

## Security Best Practices

1. Always set appropriate security headers
2. Use secure cookie options for sensitive data
3. Validate and sanitize response content
4. Implement proper CORS headers when needed
5. Use HTTPS-only cookies for sensitive data

This comprehensive set of features allows you to create secure, efficient, and flexible web applications while maintaining clean and maintainable code through the fluent interface design.