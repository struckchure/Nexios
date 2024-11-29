from nexios.http.request import Request
from nexios.http.response import NexioResponse

async def home_handler(request: Request, response: NexioResponse, **kwargs):
    return response.json({
        "message": "Welcome to your new Nexio application!",
        "docs": "https://nexio.example.com/docs"  
    })
