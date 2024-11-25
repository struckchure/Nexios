import uvicorn
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



app.add_route(Routes("/", home_handler))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
