Middleware works after/before Handler. We can get Request before dispatching or manipulate Response after dispatching.


Here’s a rephrased version of the definition of middleware and handlers, with improved clarity and flow:

---

### **Definition of Middleware and Handlers**

1. **Handler**:
   - A **handler** is a function that processes an HTTP request and **must return a `Response` object**.
   - Only **one handler** is invoked per request, based on the route and HTTP method.

   ```py
    async def log_request(req,res):
        return res.text("Hanler from nexios")
   ```

2. **Middleware**:
   - A **middleware** is a function that processes a request **before it reaches the handler**.
   - Middleware functions **do not return a value**. Instead, they call `await next()` to pass control to the next middleware or the final handler.
   - Multiple middleware functions can be chained together to perform tasks like authentication, logging, or request modification.

   ```py
    async def log_request(req,res, call_next):
        #run before handler
        await call_next()
        #run after handler
   ```

3. **Registration**:
   - Middleware and handlers can be registered using:
     - `app.add_middleware(middleware_handler)`: Registers middleware for all routes.
---

### **Key Differences**
| **Aspect**       | **Handler**                              | **Middleware**                          |
|-------------------|------------------------------------------|-----------------------------------------|
| **Purpose**       | Processes the request and sends a response. | Processes the request before it reaches the handler. |
| **Return Value**  | Must return a `Response` object.          | Does not return a value; calls `await next()` to proceed. |
| **Invocation**    | Only one handler is called per request.   | Multiple middleware functions can be chained. |

---
## Execution order
The order in which Middleware is executed is determined by the order in which it is registered. The process before the next of the first registered Middleware is executed first, and the process after the next is executed last. See below.

```py

from nexios import get_application()

app = get_application()

async def middleware_1(request,response, call_next):
    print("middleware 1 start")
    response = await call_next()  # Proceed to the next middleware or handler
    print("middleware 1 end")
    return response

async def middleware_2(request,response, call_next):
    print("middleware 2 start")
    response = await call_next()  # Proceed to the next middleware or handler
    print("middleware 2 end")
    return response

async def middleware_3(request,response, call_next):
    print("middleware 3 start")
    response = await call_next()  # Proceed to the next middleware or handler
    print("middleware 3 end")
    return response

@app.get("/")
async def handler(request,response):
    print("handler")
    return Response(body="Hello!", status_code=200)
app.add_middleware(middleware_1)
app.add_middleware(middleware_2)
app.add_middleware(middleware_3)
```

Result is the following

```rs
middleware 1 start
    middleware 2 start
        middleware 3 start
            handler
        middleware 3 end
    middleware 2 end
middleware 1 end

```

## **Modify the Response After `next()`**

Middleware in Nexio can not only process requests **before** they reach the handler but also **modify responses** after the handler has processed the request. This is achieved by capturing the response returned by `await next(request)` and making changes to it before returning it further up the middleware chain.

---

### **How It Works**
1. **Capture the Response**:
   - When `await call_next()` is called, the middleware waits for the next middleware or handler to process the request and return a response.
   - The response is then captured and can be modified.

2. **Modify the Response**:
   - You can modify the response's body, headers, status code, or any other property before returning it.

3. **Return the Modified Response**:
   - The modified response is returned to the previous middleware or sent back to the client.

---

### **Example: Adding a Custom Header**
Here’s an example of a middleware that adds a custom header to the response:

```python
@app.use
async def add_header_middleware(request,response, call_next):
    response = await call_next()

    # Modify the response by adding a custom header
    response.header("X-Custom-Header", "Modified by Middleware")

    return response
```

---

### **Example: Logging Response Status**
Here’s an example of a middleware that logs the response status code:

```python
@app.use
async def log_status_middleware(request,response, call_next):
    # Proceed to the next middleware or handler
    response = await call_next()

    # Log the response status code
    print(f"Response Status: {response.status_code}")

    return response
```

---

### **Key Points**
- **Flexibility**: Middleware can modify responses to add headers, change the body, or even replace the entire response.
- **Order Matters**: Since middlewares are executed in reverse order after the handler, modifications made in earlier middlewares will take precedence.
- **Use Cases**:
  - Adding security headers (e.g., `Content-Security-Policy`).
  - Logging response details.
  - Transforming the response body (e.g., compressing data).

---

### **Important Note**
When modifying responses, ensure that the changes are consistent with the application's requirements and do not break the client's expectations. For example, avoid modifying the response body if the client expects a specific format (e.g., JSON).

---

This note explains how middleware can modify responses after `await next(request)` and provides practical examples. Let me know if you need further clarification or additional examples!

Here’s a rewritten version of the previous note, focusing on the **class-based middleware** approach where the user can decide when to call `next`. This version is concise, clear, and structured for better readability.

---

### **Class-Based Middleware in Nexio**

In Nexio, you can create **class-based middlewares** by inheriting from a `BaseMiddleware` class. This approach provides a structured way to define middleware logic, with the flexibility to decide **when to call `next`** to proceed to the next middleware or handler.

---

### **BaseMiddleware Class**
The `BaseMiddleware` class serves as a template for creating custom middlewares. It includes two key methods:
1. **`process_request(request, next)`**: Executed before the request reaches the handler or the next middleware. The user can decide when to call `next()`.
2. **`process_response(request, response)`**: Executed after the request has been processed, allowing modification of the response before it is returned to the client.

---

### **Key Features**
1. **Flexibility**:
   - The user decides when to call `call_next()` in `process_request`, enabling custom logic like short-circuiting or conditional processing.
2. **Separation of Concerns**:
   - `process_request` handles pre-processing of the request.
   - `process_response` handles post-processing of the response.
3. **Reusability**:
   - Middleware logic can be reused across multiple routes or applications.

---


### **Creating a Custom Middleware**
To create a custom middleware, inherit from `BaseMiddleware` and override the `process_request` and `process_response` methods.

#### **Example: Logging Middleware**
This middleware logs the request method and path before processing and logs the response status code after processing.

```python
from nexios.base import BaseMiddleware
class LoggingMiddleware(BaseMiddleware):
    async def process_request(self, request, next):
        print(f"Request: {request.method} {request.path}")
        # Call next() to proceed to the next middleware or handler
        return await next(request)

    async def process_response(self, request, response):
        print(f"Response: {response.status_code}")
        return response
```

---

#### **Example: Authentication Middleware**
This middleware checks for an API key in the request headers before processing and short-circuits the request cycle if the key is invalid.

```python
from nexios.base import BaseMiddleware
class AuthMiddleware(BaseMiddleware):
    async def process_request(self, request, next):
        api_key = request.headers.get("x-api-key")
        if api_key != "your-secret-key":
            # Short-circuit the request cycle and return a 401 response
            return Response(body="Unauthorized", status_code=401)
        # Call next() to proceed to the next middleware or handler
        return await next(request)
```

---

### **Registering Class-Based Middleware**
To use a class-based middleware, instantiate it and register it with the Nexio app using `app.use`.

```python
app = get_application()

app.add_middleware(LoggingMiddleware())
app.add_middleware(AuthMiddleware())

# Define a route
@app.get("/")
async def handler(request, response):
    return response.json(body="Hello, World!", status_code=200)
```

---

### **Execution Flow**
1. **Request Phase**:
   - The `process_request` method is called.
   - The user can decide when to call `next()` to proceed to the next middleware or handler.
   - If `next()` is not called, the middleware can short-circuit the request cycle by returning a `Response` directly.

2. **Response Phase**:
   - The `process_response` method is called after `next()` has been called.
   - The user can modify the response before it is returned to the client.

---

### **Advantages**
1. **Control Over Flow**:
   - The user decides when to proceed to the next middleware or handler.
2. **Modularity**:
   - Middleware logic is encapsulated in reusable classes.
3. **Separation of Concerns**:
   - Pre-processing and post-processing logic are clearly separated.

---

### **Example Output**
For the `LoggingMiddleware` and `AuthMiddleware` example:
- If the API key is valid:
  ```
  Request: GET /
  Response: 200
  ```
- If the API key is invalid:
  ```
  Request: GET /
  Response: 401
  ```

---

This note explains how to create and use class-based middlewares in Nexio, with examples and a clear explanation of the execution flow. Let me know if you need further clarification!
