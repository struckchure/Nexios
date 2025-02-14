# Nexios ASGI Backend Framework: Application Entry Point

Nexios is a modern, high-performance ASGI (Asynchronous Server Gateway Interface) backend framework designed for building scalable and efficient web applications and APIs. It provides a lightweight, flexible, and extensible foundation for developing asynchronous web services. This document provides a comprehensive guide to the application entry point in Nexios, explaining how to set up, configure, and run a Nexios application.

---

## Introduction to the Nexios Application Entry Point

The application entry point is the core of any Nexios application. It serves as the central hub where all incoming requests are processed, routed to the appropriate handlers, and responses are returned. The entry point is typically defined in your main application file (e.g., `main.py`) and is responsible for initializing the application, defining routes, adding middleware, and managing application lifecycle events.

The Nexios framework is built with simplicity and performance in mind, making it an excellent choice for developers who want to build modern web applications without the overhead of more complex frameworks.

---

## Key Features of the Nexios Application Entry Point

1. **ASGI Compatibility**: Nexios is fully compliant with the ASGI specification, ensuring compatibility with ASGI servers like Uvicorn, Hypercorn, and Daphne.
2. **Routing**: Easily define routes and attach them to the application.
3. **Middleware Support**: Add middleware to process requests and responses globally.
4. **Lifespan Events**: Handle application startup and shutdown events for resource management.
5. **Extensibility**: Customize and extend the application with additional functionality as needed.
6. **Asynchronous by Design**: Built to handle asynchronous operations, making it ideal for high-performance applications.

---



## Creating the Application Entry Point

Create a new Python file (e.g., `main.py`) and define your Nexios application. Here’s an example: or use the nexios cli tool

```python
from nexios import NexioApp #or get_application
from nexios.routing import Route

# Define a route handler for the home page
async def home(req, res):
    return res.json({"message": "Welcome to Nexios!"})

# Define a route handler for the about page
async def about(req, res):
    return res.josn({"message": "About Nexios"})

# Create the Nexios application
app = NexioApp() #or get_application

# Add routes to the application
app.add_route(Route("/", home, methods=["GET"]))
app.add_route(Route("/about", about, methods=["GET"]))

# Optional: Add middleware
# app.add_middleware(...)

# Optional: Add lifespan event handlers
@app.on_startup()
async def startup():
    print("Application is starting up...")

@app.on_evon_shutdownent()
async def shutdown():
    print("Application is shutting down...")
```

## Run the Application

To run the Nexios application, you need an ASGI server like Uvicorn. Follow these steps:

1. Install Uvicorn:
   ```bash
   pip install uvicorn
   ```

2. Run the application using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

   - `main:app` refers to the `app` object in the `main.py` file.
   - The `--reload` flag enables auto-reloading during development.

3. Access the application in your browser or via an HTTP client:
   - `http://127.0.0.1:8000/` → Returns `{"message": "Welcome to Nexios!"}`
   - `http://127.0.0.1:8000/about` → Returns `{"message": "About Nexios"}`

---


##  The `NexiosApp` Class

The `Nexios` class is the core of your application. It is responsible for managing routes, middleware, and lifecycle events. When you instantiate the `Nexios` class, you create an application object that serves as the entry point for all incoming requests.

```python
app = Nexios()
```
get_application is a function that simplifies application creation. Instead of manually instantiating NexiosApp and configuring it, this function:

## Defining Route Handlers

Route handlers are asynchronous functions that process incoming requests and return responses. Each handler takes a `request` ans a `response` object as an argument and returns a response. In the example above, the `home` and `about` handlers return JSON responses.

```python
async def home(request, response):
    return response.json({"message": "Welcome to Nexios!"})
```

## Adding Routes

Routes are added to the application using the `add_route` method. This method take `Routes` as a parameter which takes the following parameters:
- `path`: The URL path for the route.
- `handler`: The function that handles the request.
- `methods`: A list of HTTP methods supported by the route (e.g., `["GET"]`).

```python
app.add_route(Routes("/", home, methods=["GET"]))
```

##  **Middleware**

Middleware allows you to process requests and responses globally. You can add middleware to the application using the `add_middleware` method. Middleware is useful for tasks like authentication, logging, and request/response modification.

```python
# Example of adding middleware
# app.add_middleware(SomeMiddlewareClass)
```

## **Lifespan Events**

Lifespan events allow you to execute code during the application's startup and shutdown phases. These events are useful for tasks like initializing database connections, loading configuration, or cleaning up resources.

```python
@app.on_startup()
async def startup():
    print("Application is starting up...")

@app.on_shutdown("shutdown")
async def shutdown():
    print("Application is shutting down...")
```

---

## Advanced Configuration

**Customizing the Application**

The `Nexios` ionstance class provides several options for customizing your application. For example, you can configure the application to use custom exception handlers, enable debugging, or set default headers.

```python
from nexios.config import MakeConfig

config = MakeConfig({
    "debug" : True
})
app = Nexios(config=config)
```





## Best Practices for Using the Application Entry Point

1. **Organize Routes**: Group related routes together and consider usingm Router for better modularity.
2. **Use Middleware Wisely**: Middleware can add overhead to your application, so use it only when necessary.
3. **Handle Lifespan Events**: Use startup and shutdown events to manage resources efficiently.
4. **Enable Debugging in Development**: Set `debug=True` during development to get detailed error messages.
5. **Test Your Application**: Use tools like `pytest` to write tests for your application.

---
