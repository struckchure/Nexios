from nexios import get_application,NexioApp
from nexios.exceptions import HTTPException
from nexios.http import Request,Response
async def handle_server_error(req :Request,res :Response,exc :Exception):
    return res.json({"err":"Hello"})

class NotFound(HTTPException):
    pass
app :NexioApp = get_application()
async def handler_not_found(request: Request,response:Response, exc: Exception):
    return response.json({"ERROR":"not found"})
    
app.add_exception_handler(ValueError,handler_not_found)
@app.get("")
async def index(req:Request, res:Response) -> Response:
    # raise RecursionError("Vale error")
    return res.json({"text":"Helloo world"})