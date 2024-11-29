import uvicorn
from nexios import get_application
from nexios.routers import Routes
from tortoise import Tortoise as db
from contextlib import asynccontextmanager
import traceback
import os,asyncio
from controllers.tasks_controllers import task_routes
from nexios.routers import    Routes
from settings import AppConfig
from controllers.home_handler import home_handler
from nexios.static import StaticFilesHandler
from pathlib import Path    

app = get_application(config=AppConfig)
static_handler = StaticFilesHandler(
    directory=Path("static"),  
    url_prefix="/static/"
)


media_handler = StaticFilesHandler(
    directory=Path("media"),  
    url_prefix="/media/"
)
app.add_route(Routes("/static/*",static_handler))
@app.on_startup
async def connect_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), "database.db")
        await db.init(
            db_url=f"sqlite:///{db_path}",
            modules={"models": ["models"]},
              # Use models.py directly
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
app.mount_router(task_routes)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000,loop="asyncio")
