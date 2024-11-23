import os

def create_project_structure(project_name):
    # Create the base project directory
    os.makedirs(project_name, exist_ok=True)
    os.makedirs(f"{project_name}/app", exist_ok=True)
    os.makedirs(f"{project_name}/config", exist_ok=True)
    os.makedirs(f"{project_name}/middlewares", exist_ok=True)
    os.makedirs(f"{project_name}/migrations", exist_ok=True)

    # Create the files within the app directory
    create_file(f"{project_name}/app/app.py", app_code())
    create_file(f"{project_name}/config/config.py", config_code())
    create_file(f"{project_name}/config/database.py", database_code())
    create_file(f"{project_name}/middlewares/middleware.py", middleware_code())
    create_file(f"{project_name}/migrations/__init__.py", '')  # placeholder for migrations

    print(f"Project structure for '{project_name}' created successfully!")

def create_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

def app_code():
    return '''
import uvicorn
from nexio.http.request import Request
from nexio.application import NexioHTTPApp
from nexio.routers import Routes, Router
from nexio.http.response import NexioResponse
from nexio.middlewares.base import BaseMiddleware
from nexio.config.settings import BaseConfig
from nexio.sessions.middlewares import SessionMiddleware
from nexio.middlewares.common import CommonMiddleware
from nexio.middleware.logging import ErrorHandlerMiddleware

# Import database connection from the config
from config.database import connect_db, disconnect_db

# App Setup
app = NexioHTTPApp(config=BaseConfig())

# Middleware
app.add_middleware(BaseMiddleware())
app.add_middleware(SessionMiddleware())
app.add_middleware(CommonMiddleware())
app.add_middleware(ErrorHandlerMiddleware())

@app.on_startup
async def on_startup():
    await connect_db()

@app.on_shutdown
async def on_shutdown():
    await disconnect_db()

# Routes
async def welcome(request: Request, response: NexioResponse):
    return response.json({"message": "Welcome to Nexio! 😀"})

r = Router()
r.add_route(Routes("/", welcome))
app.mount_router(r)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''

def config_code():
    return '''
class BaseConfig:
    SECRET_KEY = "your_secret_key"

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://db.sqlite3"
    },
    "apps": {
        "models": {
            "models": ["nexio.sessions.models"], 
            "default_connection": "default",
        },
    },
}
'''

def database_code():
    return '''
from tortoise import Tortoise
import os

async def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
    await Tortoise.init(db_url=f"sqlite:///{db_path}", modules={"models": ["nexio.sessions.models"]})
    await Tortoise.generate_schemas()

async def disconnect_db():
    await Tortoise.close_connections()
'''

def middleware_code():
    return '''
class BaseMiddleware:
    async def process_request(self, request, response):
        # Handle the request here
        pass
'''
