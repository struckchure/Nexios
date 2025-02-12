### **Routing in Nexio**

Routing is a core feature of Nexio that allows you to define how incoming HTTP requests are handled based on the **request path** and **HTTP method**. Nexio provides a flexible and powerful routing system, including support for **path parameters**, **route validators**, and **regex-based paths**. Additionally, Nexio supports **routers** for organizing routes into modular components.

---

### **Basic Routing**
Routes are defined using the `@app.HTTP_METHOD` decorators, where `HTTP_METHOD` can be `get`, `post`, `put`, `delete`, etc.

#### **Example: Basic Route**
```python
from nexios import get_application
from nexios.http import  Request, Response

app = get_application()

@app.get("/hello")
async def hello_handler(request: Request, response :Response):
    return response.text("Hello, World!", status_code=200)

#or
@app.route("/hello",allowed_method=["GET"])
async def hello_handler(request: Request, response :Response):
    return response.text("Hello, World!", status_code=200)

```

- **Path**: `/hello`
- **HTTP Method**: `GET`
- **Handler**: `hello_handler`

---

### **Adding Routes Programmatically**
You can also add routes programmatically using the `add_route` method on the `app` or `router` object. This is useful for dynamic route registration or when working with external configurations.

#### **Example: Using `add_route`**
```python
from nexios import get_application
from nexios.http import  Request, Response

app = get_application()

async def hello_handler(request: Request, response :Response):
    return response.text("Hello, World!", status_code=200)


# Add a route programmatically
app.add_route(Routes("/hello", hello_handler, methods=["GET"]))
```

- **Path**: `/hello`
- **HTTP Method**: `GET`
- **Handler**: `hello_handler`

---

### **Path Parameters**
Path parameters allow you to capture dynamic values from the URL. They are defined using curly braces `{}`.

#### **Example: Path Parameters**
```python
@app.get("/user/{user_id}")
async def user_handler(request: Request, response :Response):
    user_id = request.path_params.user_id
    return response.text(f"User ID: {user_id}", status_code=200)
```

- **Path**: `/user/{user_id}`
- **Captured Value**: `user_id` is passed to the handler as an argument.

---

### **Adding Validators to Routes**
Validators ensure that path parameters meet specific criteria (e.g., type, format). Nexio supports built-in and custom validators.

#### **Example: Route with Validators**
```python
from nexios.validators import IsInt

@app.get("/user/{user_id}",validator={"user_id":int})
async def user_handler(request: Request, response :Response):
    user_id = request.path_params.user_id
    return response.text(f"User ID: {user_id}", status_code=200)

```

- **Validator**: `int` ensures that `user_id` is an integer.
- If the validation fails, Nexio automatically returns a `422 Unprocessable` response.

---

### **Regex in Route Paths**
Regex can be used to define complex path patterns. This is useful for advanced routing requirements.

#### **Example: Regex in Route Path**
```python
@app.get(r"/post/{post_id:\d+}")
async def post_handler(request: Request, response :Response):
    user_id = request.path_params.user_id
    return response.text(f"User ID: {user_id}", status_code=200)

```

- **Regex**: `\d+` ensures that `post_id` is a sequence of digits.
- **Path**: `/post/123` (valid), `/post/abc` (invalid).

---

### **Routers**
Routers allow you to organize routes into modular components. This is especially useful for large applications with multiple routes.

#### **Example: Using Routers**
```python
from nexios import Router

# Create a router
user_router = Router(prefix="/user") #prefix is optional

# Define routes in the router
@user_router.get("/profile")
async def profile_handler(request: Request, response :Response):
    return Response(body="User Profile", status_code=200)

@user_router.get("/settings")
async def settings_handler(request: Request, response :Response):
   return response.text(f"User ID: {user_id}", status_code=200)


# Mount the router under a prefix
app.mount_router(user_router)
```

- **Router Paths**:
  - `/user/profile`
  - `/user/settings`
- **Benefits**:
  - Modularizes route definitions.
  - Simplifies route management in large applications.

---

### **Adding Routes to Routers Programmatically**
You can also add routes to routers programmatically using the `add_route` method.

#### **Example: Adding Routes to a Router**
```python
from nexios.routing import Router Routes
from nexios.http import Request, Response
user_router = Router()

async def profile_handler(request: Request, response :Response):
    return response.text("User Profile", status_code=200)

async def settings_handler(request: Request, response :Response):
    return response.text("User Settings", status_code=200)

user_router.add_route(Routes("/profile", profile_handler, methods=["GET"]))
user_router.add_route(Routes("/settings", settings_handler, methods=["GET"]))

app.mount_router(user_router)
```

---
### **Advanced Routing Features**
1. **Wildcard Routes**:
   - Use `*` to match any path segment.
   - Example: `/files/*` matches `/files/a`, `/files/a/b`, etc.

2. **Optional Parameters**:
   - Use `?` to make a path segment optional.
   - Example: `/user/{user_id?}` matches `/user` and `/user/123`.

3. **Custom Validators**:
   - Create custom validators by subclassing `Validator` and implementing the `validate` method.

4. **Route Prefixing**:
   - Apply a common prefix to a group of routes using `Router` or `RouteGroup`.

---

### **Example: Complete Routing Setup**
```python
from nexios import Nexio, Router, Request, Response, Routes
from nexios.validators import IsInt

app = Nexio()

@app.get("/hello")
async def hello_handler(request: Request, response :Response):
    return response.text(body="Hello, World!", status_code=200)

@app.get("/user/{user_id}")
async def user_handler(request: Request, response :Response):
    user_id = request.path_params.user_id
    return response.text(f"User ID: {user_id}", status_code=200)

# Router example
user_router = Router()

@user_router.get("/profile")
async def profile_handler(request: Request, response :Response):
    return response.text("User Profile", status_code=200)

@user_router.get("/settings")
async def settings_handler(request: Request):
    return response.text("User Settings", status_code=200)



# Adding routes programmatically
async def about_handler(request: Request, response :Response):
    return Response(body="About Us", status_code=200)

app.add_route(Routes("/about", about_handler, methods=["GET"]))
```

---

### **Summary**
- **Basic Routes**: Define routes using `@app.HTTP_METHOD`.
- **Programmatic Routes**: Use `app.add_route(Routes(...))` or `router.add_route(Routes(...))`.
- **Path Parameters**: Capture dynamic values from the URL.
- **Validators**: Ensure path parameters meet specific criteria.
- **Regex**: Use regex for advanced path patterns.
- **Routers**: Organize routes into modular components.

# notes

>In Nexio, you can add middleware specific to a router. This allows you to apply middleware to all routes within a router, making it easy to modularize and reuse middleware logic for specific parts of your application.