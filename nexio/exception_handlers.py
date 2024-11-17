import traceback
import typing
from .http.request import Request
from .http.response import NexioResponse




async def ErrorHandler(request: Request, response :NexioResponse, call_next: typing.Callable):
    try:
        
        response = await call_next()
        return response 
    
    
    except Exception as e:
        # Capture and log the exception details
        error_details = traceback.format_exc()
        print(error_details)

        # Set response status to 500 (Internal Server Error)
        response.status(500)
        return response
