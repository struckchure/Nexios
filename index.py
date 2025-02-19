#type:ignore
from nexios import get_application,Router
from nexios.routing import Routes
from nexios.validator import Schema, fields, validate
from nexios.utils.validator import validate_request,ValidationError
from nexios.auth.decorator import auth 
from nexios.auth.exceptions import AuthErrorHandler,AuthenticationFailed
from nexios.auth.base import BaseUser
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.jwt import JWTAuthBackend
from nexios.config import MakeConfig

from nexios.pagination import (
    ListDataHandler,
    PageNumberPagination,
    Paginator,
    PaginatedResponse,
    AsyncDataHandler,
    AsyncPaginator,
    InvalidPageError,
    paginate
)
config = MakeConfig({
    "secret_key":"th-key",
    "cors":{
        "allow_origins" : ["*"],
        "debug":True
        
    }
})
app = get_application(config=config)
app.add_middleware(AuthenticationMiddleware(
    backend=JWTAuthBackend(authenticate_func=lambda x: None)
))

async def give_auth(r,res, cnext):
    r.scope['user'] = BaseUser,"jwt"
    await cnext()
    res.header("name","dunamis")
    res.header("names","dunamis11")
    
app.add_middleware(give_auth)
async def handle_validation(req,res,exc :ValidationError):
    return res.json(exc.messages,status_code = 422)

app.add_exception_handler(ValidationError,handle_validation)
    
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
a = Router(prefix="/a")
fake_items = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]
@app.get("/user")
# @a.get("/user")
@auth(["jwt"])
# @validate_request(UserSchema())

async def create_user(request, response) -> None:
    print(request.session)
    # request.session.set_session("heloo","hi")
    # response.headers['x-token'] = "babaric"
    res = response.file("C:/Users/dunamix/Downloads/Untitled video - Made with Clipchamp.mp4")
    response.set_cookie("a",19)
    response.set_cookie("a","b")

@app.route("/new")
async def create_new(request, response) -> None:
    
    return response.json(paginate(fake_items, request))
    
app.mount_router(a)
