# Nexio HTTP Framework 🚀💻

Welcome to Nexio — a lightning-fast web framework built with Python and written by TechWithDunamix, a Nigerian developer! 🇳🇬💡 Whether you're building APIs, web apps, or anything in between, Nexio is here to make your life easier and faster! ⚡

## Why Nexio? 🤔

- **Blazing Fast**: Built with performance in mind. Don't blink or you might miss it! ⚡
- **Simplicity**: Write less code, get more done. You'll spend less time debugging and more time building cool stuff. 👨‍💻
- **Easy to Use**: Everything is straightforward, from routing to database setup — no complicated setups, just plug and play! 🔌🎮

## Quick Start 🚀

Ready to get started? Here's how you can set up Nexio and make your first web app in minutes:

### 1. Install Dependencies 📦

Install Nexio and the required dependencies with pip:

```bash
pip install uvicorn tortoise-orm nexio
```

### 2. Create Your First App 💻

Create a new Python file (e.g., `app.py`) and start coding:

```python
from nexio.http.request import Request
from nexio.application import NexioHTTPApp
from nexio.http.response import NexioResponse
import uvicorn
from tortoise import Tortoise as db
from nexio.config.settings import BaseConfig
from nexio.sessions.middlewares import SessionMiddleware
from nexio.routers import Routes

# Setup Tortoise ORM (SQLite in this case)
TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {"models": {"models": ["nexio.sessions.models"], "default_connection": "default"}}
}

# Initialize the app
app = NexioHTTPApp(config=BaseConfig)

@app.on_startup
async def connect_db():
    await db.init(db_url="sqlite://db.sqlite3", modules={"models": ["nexio.sessions.models"]})
    await db.generate_schemas()

@app.on_shutdown
async def disconnect_db():
    await db.close_connections()

# Define a simple route
async def home_handler(request: Request, response: NexioResponse):
    return response.json({"message": "Hello, World! 🌍"})

# Add the route to the app
app.add_route(Routes("/", home_handler))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### 3. Run Your App 🏃‍♂️

Run the app like a pro:

```bash
python app.py
```

Your app will be running at `http://127.0.0.1:8000`. Quick, right? 😎

### 4. Database Setup (Tortoise ORM) 🗄️

No more headaches setting up the database. With Tortoise ORM, just set up the connection, and you're good to go. It supports SQLite, PostgreSQL, MySQL, and more!

```python
# Tortoise ORM setup
TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {"models": {"models": ["nexio.sessions.models"], "default_connection": "default"}}
}
```

### 5. Session Management 🔐

Managing sessions? No sweat! Nexio handles sessions out-of-the-box:

```python
# Set session data
await request.session.set("user", "dunamis")

# Get session data
user = await request.session.get("user")
```

### 6. Easy Routing 🚗

With Nexio, routing is as simple as adding a decorator:

```python
app.add_route(Routes("/user/{user_id}", user_handler))
```

### 7. Validation Like a Boss 🧑‍⚖️

Want to validate incoming data? Nexio's got you covered! Use the Schema class to define your rules:

```python
from nexio.validator.base import Schema
from nexio.validator.fields import StringField, IntegerField

class UserSchema(Schema):
    username = FieldDescriptor(field=StringField(), required=True)
    age = FieldDescriptor(field=IntegerField(min=18), required=True)
```

## Key Features ✨

- **Ultra Fast**: You won't believe how fast this thing is. Blink, and the server's up and running! ⚡
- **Database Integration**: Use Tortoise ORM with minimal setup, even for complex databases. 📦
- **Built-in Session Management**: Keep track of user sessions without breaking a sweat. 🧳
- **Flexible Routing**: Add routes quickly and easily with Nexio's intuitive syntax. 🚗
- **Validation Made Easy**: Use schemas to validate user input like a pro! ✅
- **Middleware Support**: Add custom middlewares for extra features like logging, error handling, etc. 🔧

## Contributing 🤝

If you're feeling generous and want to contribute to Nexio (or just want to make it better), feel free to create a pull request or open an issue on GitHub! I'll be more than happy to review it. 🔥

## Conclusion 🎯

Nexio is a fast, flexible, and fun-to-use web framework that helps you get your ideas off the ground quickly! Whether you're building an API or a full-fledged web app, Nexio is your go-to tool. Don't waste time with complex frameworks — use Nexio and make things happen. 🚀

Got questions or feedback? Hit me up! 😎