import os
import argparse
import sys

def create_project_structure(project_name: str):
    """Create the basic project structure for a Nexio application."""
    
    # Base directories
    directories = [
        f"{project_name}",
        f"{project_name}/config",
        f"{project_name}/handlers",
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        create_file(f"{directory}/__init__.py", "")
    
    # Create main application files
    create_file(f"{project_name}/main.py", main_code())
    create_file(f"{project_name}/config/database.py", database_code())
    create_file(f"{project_name}/config/settings.py", settings_code())
    create_file(f"{project_name}/handlers/routes.py", routes_code())
    
    print(f"\n✨ Created new Nexio project: {project_name}")
    print("\nProject structure:")
    print(f"""
{project_name}/
├── config/
│   ├── __init__.py
│   ├── database.py
│   └── settings.py
├── handlers/
│   ├── __init__.py
│   └── routes.py
└── main.py
    """)
    
    print("\nTo get started:")
    print(f"1. cd {project_name}")
    print("2. pip install nexio tortoise-orm uvicorn")
    print("3. python main.py")
    print("\nYour app will be available at http://localhost:8000")

def create_file(file_path: str, content: str):
    """Create a file with the given content."""
    with open(file_path, "w") as f:
        f.write(content)

def main_code():
    return '''import uvicorn
from nexio import get_application
from nexio.routers import Routes
from tortoise import Tortoise as db
from contextlib import asynccontextmanager
import traceback
import os

from config.settings import AppConfig
from handlers.routes import home_handler

# Initialize app
app = get_application(config=AppConfig)

@app.on_startup
async def connect_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
        await db.init(
            db_url=f"sqlite:///{db_path}",
            modules={"models": ["nexio.sessions.models"]}
        )
        await db.generate_schemas()
        print("Database connected")
    except Exception as e:
        print(f"Database connection error: {e}")
        print(traceback.format_exc())

@app.on_shutdown
async def disconnect_db():
    try:
        await db.close_connections()
        print("Database disconnected")
    except Exception as e:
        print(f"Database disconnect error: {e}")

@asynccontextmanager
async def lifespan():
    try:
        await connect_db()
        yield
    finally:
        await disconnect_db()

# Add single route
app.add_route(Routes("/", home_handler))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''

def database_code():
    return '''import os

TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{os.path.join(os.path.dirname(__file__), '../db.sqlite3')}"
    },
    "apps": {
        "models": {
            "models": ["nexio.sessions.models"], 
            "default_connection": "default",
        },
    },
}
'''

def settings_code():
    return '''from nexio.config.settings import BaseConfig

class AppConfig(BaseConfig):
    SECRET_KEY = "your-secret-key"  # Change this in production!
'''

def routes_code():
    return '''from nexio.http.request import Request
from nexio.http.response import NexioResponse

async def home_handler(request: Request, response: NexioResponse, **kwargs):
    return response.json({
        "message": "Welcome to your new Nexio application!",
        "docs": "https://nexio.example.com/docs"  # Update with actual docs URL
    })
'''

