Here's an introductory markdown documentation for Nexios based on your questions and answers:

---


# Nexios Documentation
[![GitHub stars](https://img.shields.io/github/stars/techwithdunamix/nexios.svg?style=social)](https://github.com/techwithdunamix/nexios)
[![GitHub forks](https://img.shields.io/github/forks/techwithdunamix/nexios.svg?style=social)](https://github.com/techwithdunamix/nexios)
[![GitHub issues](https://img.shields.io/github/issues/techwithdunamix/nexios.svg)](https://github.com/techwithdunamix/nexios/issues)
## Introduction
Nexios is a Python-based ASGI backend framework designed to provide flexibility, speed, and utility for building asynchronous web applications. It mimics the structure of Express.js, making it easy for developers familiar with JavaScript and Node.js to transition to Python. Nexios is designed with both Object-Oriented Programming (OOP) and Functional Programming (FP) principles, giving developers the choice to approach their code in the way that suits them best.

Nexios provides built-in utilities like middleware support, routing, session management, WebSocket handling, and asynchronous operations, making it a perfect fit for modern, fast-paced backend development. It also comes with automatic support for Tortoise ORM, making it easier to interact with databases in a non-blocking way.

## Features

### 1. **Installation**
To get started with Nexios, follow these steps:

1. **Create a new project directory**:
   ```bash
   mkdir your_project_name
   cd your_project_name
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install Nexios**:
   ```bash
   pip install nexios
   ```

5. **Verify the installation**:
   ```bash
   python -m nexios
   ```

You should see the following output, confirming the installation:
```
    🚀 Welcome to Nexios 🚀
      The sleek ASGI Backend Framework
      Version: X.X.X
```

### 2. **Hello World Example**

Create a simple "Hello World" application using Nexios:

```python
from nexios import NexioApp

app = NexioApp()

@app.route("/api/endpoint", methods=["GET"])
async def endpoint_handler(request, response):
    return response.json({"text": "Welcome to Nexios"})
```

Run the application with the command:
```bash
uvicorn main:app --reload
```

### 3. **Routing**
Nexios supports routing in both decorator and router styles.

#### Using Decorators:
```python
@app.route("/api/endpoint", methods=["GET"])
async def endpoint_handler(request, response):
    return response.send("Hello World")
```

#### Using Routers:
```python
from nexios import Router

r = Router(prefix="/api")
r.add_route("/endpoint", handler=endpoint_handler)
```

Routes can be defined with different HTTP methods like `GET`, `POST`, `PUT`, `DELETE`, etc. The handler functions will respond accordingly based on the request method.

### 4. **Middleware**
Nexios allows you to define middleware that runs before or after a request is processed.

Example of an authentication middleware:
```python
class AuthMiddleware(BaseMiddleware):
    async def before_request(self, req, res):
        token = req.headers.get("Authorization")
        if not token:
            return res.json({"error": "Unauthorized"}, status=401)
        
        user = await verify_token(token)
        req.state.user = user
        await super().before_request(req, res)
```

This middleware checks for a token in the request header and verifies it before proceeding to the handler.

### 5. **Asynchronous Support**
Nexios is built on top of ASGI, which means it's fully asynchronous and capable of handling multiple concurrent requests without blocking. This is especially useful for I/O-bound operations such as database queries, file handling, and API calls, allowing for more efficient performance compared to traditional synchronous frameworks.

By using `async` and `await` keywords, you can make non-blocking calls to databases (like Tortoise ORM) and external APIs while handling incoming HTTP requests.

### 6. **WebSocket Support**
Nexios comes with built-in WebSocket support, allowing you to handle real-time communication in your application easily. This feature can be useful for building chat applications, live notifications, or other real-time features.

### 7. **Session Management**
Nexios supports both file-based and signed cookie sessions. It also has a built-in session manager that helps with storing and retrieving session data securely. This is useful for maintaining user states, especially in authentication systems.

## Conclusion
Nexios is a powerful and flexible framework that allows developers to build modern web applications efficiently. It leverages the power of ASGI for asynchronous operations, offers easy-to-use routing and middleware systems, and comes with built-in utilities like WebSocket and session management to help you develop faster and smarter. Whether you prefer Object-Oriented or Functional Programming, Nexios has you covered, making it a versatile choice for backend development.

For more detailed information, refer to the complete [Nexios documentation](#).

--- 

This markdown provides an introduction to Nexios, covering installation, basic routing, middleware, asynchronous support, and other key features of the framework. Let me know if you want to add more details or need further customization!