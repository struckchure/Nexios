from nexios import get_application
from nexios.exceptions import HTTPException
from nexios.http import Request,Response
async def handle_server_error(req,res,exc):
    return res.json({"err":"Hello"})

class NotFound(HTTPException):
    pass
app = get_application(config=3)


async def handler_not_found(request: Request,response:Response, exc: Exception):
    return response.json({"ERROR":"not found"})
    
app.add_exception_handler(ValueError,handler_not_found)
@app.get("")
async def index(req, res):
    raise RecursionError("Vale error")
    return res.json({"text":"Helloo world"})