from nexio.http.request import Request
from nexio.application import NexioHTTPApp
from nexio.decorators import AllowedMethods
from nexio.routers import Routes,Router
import uvicorn
from nexio.exception_handlers import ErrorHandler
from nexio.orm import NexioOrm as db
from nexio.orm import models,fields
import traceback
import os

@AllowedMethods(["GET","POST"])
async def home_handler(request: Request, response, **kwargs):
    
    # print(request.url.param)
    a = await request.files
    
    print(request.cookies)
    print(request.url.include_query_params())
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
@app.on_start
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


app.add_route(
    Routes("/",home_handler)
    )

r = Router()
r.add_route(Routes("/user/{user_id}/{id}",home_handler))
app.mount_router(r)
app.add_middleware(ErrorHandler)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)