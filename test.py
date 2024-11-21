from nexio.http.request import Request
from nexio.application import NexioHTTPApp
from nexio.decorators import AllowedMethods
from nexio.routers import Routes,Router
from nexio.http.response import NexioResponse
import uvicorn
from nexio.exception_handlers import ErrorHandler
from tortoise import Tortoise as db
from nexio.middlewares.base import BaseMiddleware
from nexio.contrib.sessions.models import Session
import traceback
import os
from tests import Aerichaq
from contextlib import asynccontextmanager
from nexio.contrib.sessions.backends.db import SessionStore
from nexio.config.settings import BaseConfig
from nexio.contrib.sessions.middlewares import SessionMiddleware
from nexio.decorators import validate_request
from nexio.contrib.validator import validate,Schema,fields,post_load,ValidationError
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


class UserSchema(Schema):
    """
    Comprehensive user data validation schema
    """
    # Basic string field with validation
    username = fields.Str(
        required=True,  # Must be present
        validate=[
            validate.Length(min=3, max=30),  # Length constraints
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error='Username must be alphanumeric')
        ]
    )

    # Email field with built-in email validation
    email = fields.Email(
        required=True,
        validate=validate.Email(error='Invalid email format')
    )

    # Age with numeric range validation
    age = fields.Int(
        required=True,
        validate=[
            validate.Range(min=18, max=120, 
            error='Age must be between 18 and 120')
        ]
    )

    # Nested validation for address
    address = fields.Nested('AddressSchema')

    # Enumeration validation
    account_type = fields.Str(
        validate=validate.OneOf(['free', 'premium', 'enterprise'])
    )

    # List with nested validation
    skills = fields.List(
        fields.Str(validate=validate.Length(min=2, max=50)), 
        validate=validate.Length(max=10)  # Max 10 skills
    )

    # Optional field with default
    is_active = fields.Bool(missing=True)

    # Complex validation method
    @post_load
    def validate_user_data(self, data, **kwargs):
        """
        Additional complex validation logic
        """
        # Custom validation rule: premium accounts must have at least 3 skills
        if (data.get('account_type') == 'premium' and 
            (not data.get('skills') or len(data.get('skills', [])) < 3)):
            raise ValidationError('Premium accounts must have at least 3 skills')
        return data


@AllowedMethods(["GET","POST"])
async def home_handler(request: Request, response :NexioResponse, **kwargs):
    
    # response.set_cookie(key = "session",value="dunamis")
    # response.set_cookie(key = "session2",value="dunamis101")
    # d = await request.files

    # # await request.session.set_session("current_proce",110)
    # # a =  await request.session.get_session("session_data")
    # print(f"username is {d}")
    data = await request.data
    schema = UserSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return response.json(err.messages)
    
    

    print(Schema)
    return response.json()

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
app = NexioHTTPApp(config=AppConfig())

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
        modules={"models": ["tests","nexio.contrib.sessions.models"]})
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

        
        


app.add_middleware(ErrorHandler)
app.add_middleware(SessionMiddleware())
# app.add_middleware(LoggingMiddleware)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)





