from nexio.request import Request
from nexio.application import NexioHTTPApp
from nexio.decorators import AllowedMethods
from nexio.middlewares.logging import logging_middleware
from nexio.routers import Routes,Router
import uvicorn 
import time 
async def long_running():
    for i in range(10000):
        time.sleep(2)
        print(i)
@AllowedMethods(["GET","POST"])
async def home_handler(request: Request, response, **kwargs):
    print(request.query_params)
    
    
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
def connect_db():
    print("connected to db")
app.add_route(
    Routes("/",home_handler)
    )

r = Router()
r.add_route(Routes("/user/{id}",home_handler))
app.mount_router(r)
# Run the app with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)