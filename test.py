from nexio.http.request import Request
from nexio.application import NexioHTTPApp
from nexio.decorators import AllowedMethods
from nexio.routers import Routes,Router
from nexio.http.response import NexioResponse
import uvicorn
from nexio.exception_handlers import ErrorHandler
from tortoise import Tortoise as db
from nexio.middlewares.logging import LoggingMiddleware
import traceback
import os
from contextlib import asynccontextmanager
# from tests import User

TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{os.path.join(os.path.dirname(__file__), 'db.sqlite3')}"
    },
    "apps": {
        "models": {
            "models": ["tests", "aerich.models","nexio.contrib.sessions.models"], 
            "default_connection": "default",
        },
    },
}


@AllowedMethods(["GET","POST"])
async def home_handler(request: Request, response :NexioResponse, **kwargs):
    
    # print(request.url.param)
    a = await request.files
    print(request.meta)
    print(request.cookies)
    print(request.url.include_query_params())
    print(request.url_params)
    print(request.app_config)
    response.cookie(
        
        key="1",value="101"


    )
    return response.json({"hell":"hi"})

async def about_handler(request: Request, response, **kwargs):
    return response.json({"message": "This is the About Page."})

async def contact_handler(request: Request, response, **kwargs):
    return response.json({"message": "Contact us at contact@example.com"})

async def user_handler(request: Request, response, id: str):
    return response.json({"error": "error"},status_code=500)


app = NexioHTTPApp()

async def  middleware(request,response,nex):
    print("Hello world")
    await nex()
    return 
app.add_middleware(middleware)


    
@app.lifespan_context
async def connect_db():
    cwd = os.getcwd()
    print(cwd)
    try:
       db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
       await db.init(db_url=f"sqlite:///{db_path}",
        modules={"models": ["tests"]})
       await db.generate_schemas()
    except Exception as e:
       print(traceback.format_exc())
       print(f"exceptint {e}")
       
    print("connected")
    # print( await User.all().filter())


@app.on_shutdown
async def disconnect_db():
    try:
        await db.close_connections()
        print("disconnecsted")
        print("Databases connections closed successfully")
    except Exception as e:
        print(f"Error closing database connections: {e}")
        print(traceback.format_exc())
app.add_route(
    Routes("/",home_handler)
    )

r = Router()
r.add_route(Routes("/user/{user_id}/{id}",home_handler))
class AuthMiddleware:

    def __init__(self, request, response,callnext):
        self.request = request
        self.response = response
        self.callnext = callnext

    async def __call__(self, *args ,**kwds):

        print(self.request)
        await self.callnext()

        return
app.mount_router(r)
app.add_middleware(ErrorHandler)
# app.add_middleware(LoggingMiddleware)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)




