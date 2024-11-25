from nexio.http.request import Request
from nexio import get_application
from nexio.decorators import AllowedMethods
from nexio.routers import Routes,Router
from nexio.http.response import NexioResponse
import uvicorn
from nexio.exception_handlers import ErrorHandler
from tortoise import Tortoise as db
from nexio.middlewares.base import BaseMiddleware
from nexio.sessions.models import Session
import traceback
import os
from tests import Aerichaq
from contextlib import asynccontextmanager
from nexio.sessions.backends.db import SessionStore
from nexio.config.settings import BaseConfig
from nexio.sessions.middlewares import SessionMiddleware
from nexio.middlewares.common import CommonMiddleware
from nexio.decorators import validate_request
from nexio.validator.base import Schema
from nexio.validator.descriptor import FieldDescriptor
from nexio.validator.fields import StringField,IntegerField,BooleanField,ChoiceField,FileField
# from tests import User

TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{os.path.join(os.path.dirname(__file__), 'db.sqlite3')}"
    },
    "apps": {
        "models": {
            "models": ["tests", "aerich.models","nexio.sessions.models"], 
            "default_connection": "default",
        },
    },
}



class UserSchame(Schema):
    a = FieldDescriptor(field=StringField(max_length = 3),required=True)
    b = FieldDescriptor(field=FileField(),required=True)
    c = FieldDescriptor(field=ChoiceField(choices=[
        "name","dunamis"
    ]),required=True)


    async def validate(self):
        if self.a:
            self._errors['username'] = "rhis"
            
    
    


a = UserSchame()
@validate_request(Schema)
@AllowedMethods(["GET","POST"])
async def home_handler(request: Request, response :NexioResponse, **kwargs):
    
    
    # response.set_cookie(key = "session",value="dunamis")
    # response.set_cookie(key = "session2",value="dunamis101")
    # d = await request.files
    data = await request.data
    files = await request.files
    # print("file is ",type(files['b']) == UploadedFile)
    b = await a(data, files)
    print(request.headers['Origin'])
    if not b.is_valid():
        return response.json(b.errors)
    
    return response.json({})

async def about_handler(request: Request, response, **kwargs):
    return response.json({"message": "This is the About Page."})

async def contact_handler(request: Request, response, **kwargs):
    return response.json({"message": "Contact us at contact@example.com"})

async def user_handler(request: Request, response, id: str):
    return response.json({"error": "error"},status_code=500)



async def  middleware(request,response,nex):
    #print("Hello world")
    await nex()
    return 
class AppConfig(BaseConfig):
    SECRET_KEY = "dunamis winner"
app = get_application(config=AppConfig)

class LogRequestMiddleware(BaseMiddleware):
    async def process_request(self, request, response):
        print(f"Incoming request: {request.method} {request.url.path}")

app.add_middleware(LogRequestMiddleware())
@app.on_startup
async def connect_db():
    cwd = os.getcwd()
    #print(cwd)

    try:
       db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
       await db.init(db_url=f"sqlite:///{db_path}",
        modules={"models": ["tests","nexio.sessions.models"]})
       await db.generate_schemas()
       print("connected")

    except Exception as e:
       print(traceback.format_exc())
       print(f"exceptint {e}")
       
    # #print( await User.all().filter())


@app.on_shutdown
async def disconnect_db():
    #print("hello")
    try:
        await db.close_connections()
        #print("disconnecsted")
        #print("Databases connections closed successfully")
    except Exception as e:
        print(f"Error closing database connections: {e}")
        print(traceback.format_exc())

# @app.on_shutdown
# async def test_closing():
#     #print("restaring")
@asynccontextmanager
async def lifespan():
    
    try:
        await connect_db()
        yield
    finally:
        await disconnect_db()
    
app.add_middleware(middleware)

app.add_route(
    Routes("/",home_handler)
    )

r = Router()
r.add_route(Routes("/user/{user_id}/{id}",home_handler))
app.mount_router(r)

        
        


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)





