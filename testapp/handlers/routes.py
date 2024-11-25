from nexio.http.request import Request
from nexio.http.response import NexioResponse

async def home_handler(request: Request, response: NexioResponse, **kwargs):
    return response.json({
        "message": "Welcome to your new Nexio application!",
        "docs": "https://nexio.example.com/docs"  # Update with actual docs URL
    })
