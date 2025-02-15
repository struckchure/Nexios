# **Handling Fatal Errors in Nexios with `HTTPException`**

In **Nexios**, when a fatal error occurs—such as an **authentication failure**—the framework requires raising an `HTTPException`. This ensures that the API responds with the appropriate HTTP status code and message, providing a structured and consistent error response.

---

## **Raising an `HTTPException` in Middleware**
In middleware, you can raise an `HTTPException` when an error occurs, such as when authentication fails.

### **Example: Authentication Middleware**
```python
from nexios import HTTPException

# Middleware for authentication
async def authenticate(req, res, call_next):
    authorized = req.headers.get("Authorization") == "Bearer VALID_TOKEN"
    
    if not authorized:
        raise HTTPException(401, detail="Unauthorized")

    return await call_next(req, res)
```
Here, if the `Authorization` header is missing or invalid, an `HTTPException` with a `401 Unauthorized` status code is raised.

---

## **Handling `HTTPException`**
To catch and handle `HTTPException`, use `app.add_exception_handler`. This ensures a uniform error response.

### **Example: Handling Exceptions Globally**
```python
# Exception handler
async def handle_exception(req, res, exc):
    if exc.status_code == 401:
        res.status_code = 401
        res.json({"error": "Unauthorized", "message": exc.detail})
    else:
        res.status_code = exc.status_code
        res.json({"error": "An error occurred", "message": exc.detail})

# Register exception handler
app.add_exception_handler(Exception,handle_exception)
```
This function ensures that all `HTTPException` responses are formatted consistently.

---

## **Creating Custom Exceptions**
For better code organization, you can create custom exception classes that extend `HTTPException`. This allows you to define reusable error types.

### **Example: Custom Authentication Exception**
```python
class AuthenticationError(HTTPException):
    def __init__(self, detail="Authentication failed"):
        super().__init__(status_code=401, detail=detail)
```

Now, instead of raising `HTTPException` manually, you can do:
```python
raise AuthenticationError()
```
This simplifies error handling and keeps the code clean.

---

## **Example: Handling Multiple Custom Exceptions**
You can register exception handlers for specific custom exceptions.

```python
class ForbiddenError(HTTPException):
    def __init__(self, detail="Access Denied"):
        super().__init__(status_code=403, detail=detail)

class NotFoundError(HTTPException):
    def __init__(self, detail="Resource not found"):
        super().__init__(status_code=404, detail=detail)

async def handle_auth_error(req, res, exc):
    res.status_code = 401
    res.json({"error": "Unauthorized", "message": exc.detail})

async def handle_forbidden_error(req, res, exc):
    res.status_code = 403
    res.json({"error": "Forbidden", "message": exc.detail})

async def handle_not_found_error(req, res, exc):
    res.status_code = 404
    res.json({"error": "Not Found", "message": exc.detail})

app.add_exception_handler(AuthenticationError, handle_auth_error)
app.add_exception_handler(ForbiddenError, handle_forbidden_error)
app.add_exception_handler(NotFoundError, handle_not_found_error)
```
Now, when you raise `AuthenticationError`, `ForbiddenError`, or `NotFoundError`, Nexios will automatically use the corresponding handler.

