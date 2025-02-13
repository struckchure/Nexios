
## **`NexioResponse` Class**
The `NexioResponse` class is a fluent interface for creating and customizing HTTP responses in a Nexio application. It supports various response types, including plain text, JSON, HTML, files, streaming, and redirects. It also provides methods for setting headers, cookies, and caching behavior.

---
<small>
<i>
The NexioResponse class is a fluent interface and abstraction layer that simplifies the creation and customization of HTTP responses in a Nexio application. Instead of directly instantiating specific response classes like Response, JSONResponse, FileResponse, etc., developers can use NexioResponse to handle all response types in a consistent and intuitive way.
</i>

</small>

## **Methods**

## **`send(content: Any, status_code: Optional[int] = None, headers: Dict[str, Any] = {})`**
Sends a plain text or HTML response.

- **Parameters**:
  - `content`: The response body (can be any type).
  - `status_code`: The HTTP status code (default: `200`).
  - `headers`: Additional headers to include in the response.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.send("Hello, World!", status_code=200)
  ```

---

## **`text(content, status_code,headers)`**
Sends a plain text response.

- **Parameters**:
  - `content`: The response body (can be `str`, `dict`, `list`, etc.).
  - `status_code`: The HTTP status code (default: `200`).
  - `headers`: Additional headers to include in the response.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.text("Hello, World!", status_code=200)
  ```

---

## **`json(content, status_code,headers)`**
Sends a JSON response.

- **Parameters**:
  - `data`: The JSON-serializable data to send.
  - `status_code`: The HTTP status code (default: `200`).
  - `headers`: Additional headers to include in the response.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.json({"message": "Hello, World!"}, status_code=200)
  ```

---

## **`empty(status_code headers)`**
Sends an empty response with no body.

- **Parameters**:
  - `status_code`: The HTTP status code (default: `200`).
  - `headers`: Additional headers to include in the response.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.empty(status_code=204)
  ```

---

## **`html(content, status_code ,headers)`**
Sends an HTML response.

- **Parameters**:
  - `content`: The HTML content to send.
  - `status_code`: The HTTP status code (default: `200`).
  - `headers`: Additional headers to include in the response.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.html("<h1>Hello, World!</h1>", status_code=200)
  ```

---

## **`file(path, filename, content_disposition_type)`**
Sends a file as a response.

- **Parameters**:
  - `path`: The path to the file on the server.
  - `filename`: The name of the file to send (default: the file's basename).
  - `content_disposition_type`: The type of content disposition (`"attachment"` or `"inline"`).
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.file("/path/to/file.pdf", filename="document.pdf")
  ```

---

## **`stream(iterator, content_type)`**
Sends a streaming response.

- **Parameters**:
  - `iterator`: An iterator that yields chunks of data (`str` or `bytes`).
  - `content_type`: The content type of the stream (default: `"text/plain"`).
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  async def generate_data():
      yield "Hello, "
      yield "World!"
  response.stream(generate_data())
  ```

---

## **`redirect(url ,status_code)`**
Sends a redirect response.

- **Parameters**:
  - `url`: The URL to redirect to.
  - `status_code`: The HTTP status code (default: `302`).
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.redirect("/new-location", status_code=302)
  ```

---

## **`status(status_code)`**
Sets the HTTP status code for the response.

- **Parameters**:
  - `status_code`: The HTTP status code.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.status(404)
  ```

---

## **`header(key, value)`**
Sets a header in the response.

- **Parameters**:
  - `key`: The header name.
  - `value`: The header value.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.header("X-Custom-Header", "value")
  ```

---

## **`set_cookie(key, value , max_age, expires, path, domain, secure, httponly, samesite)`**
Sets a cookie in the response.

- **Parameters**:
  - `key`: The cookie name.
  - `value`: The cookie value.
  - `max_age`: The maximum age of the cookie in seconds.
  - `expires`: The expiration date of the cookie.
  - `path`: The path for the cookie (default: `"/"`).
  - `domain`: The domain for the cookie.
  - `secure`: Whether the cookie is secure (default: `True`).
  - `httponly`: Whether the cookie is HTTP-only (default: `False`).
  - `samesite`: The `SameSite` attribute for the cookie.
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.set_cookie("session_id", "12345", max_age=3600)
  ```

---

## **`delete_cookie(key, value , max_age, expires, path, domain, secure, httponly, samesite)`**
Deletes a cookie by setting its expiration to the past.

- **Parameters**:
  - `key`: The cookie name.
  - `value`: The cookie value (optional).
  - `max_age`: The maximum age of the cookie in seconds (optional).
  - `expires`: The expiration date of the cookie (optional).
  - `path`: The path for the cookie (default: `"/"`).
  - `domain`: The domain for the cookie (optional).
  - `secure`: Whether the cookie is secure (default: `False`).
  - `httponly`: Whether the cookie is HTTP-only (default: `False`).
  - `samesite`: The `SameSite` attribute for the cookie (optional).
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.delete_cookie("session_id")
  ```

---

## **`cache(max_age, private)`**
Enables caching for the response.

- **Parameters**:
  - `max_age`: The maximum age of the cache in seconds (default: `3600`).
  - `private`: Whether the cache is private (default: `True`).
- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.cache(max_age=3600)
  ```

---

## **`no_cache()`**
Disables caching for the response.

- **Returns**: `self` (for method chaining).
- **Example**:
  ```python
  response.no_cache()
  ```


---

## **Example Usage**
```python
@app.route("/client-info")
async def client_info_handler(req, response):
    response.set_cookie("session_id", "12345", max_age=3600)
    response.header("X-Custom-Header", "value")
    response.cache(max_age=3600)
    response.json({"message": "Hello, World!"}, status_code=200)
```
