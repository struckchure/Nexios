import traceback
import typing
from .http.request import Request



async def ErrorHandler(request: Request, response, call_next: typing.Callable):
    try:
        # Await call_next and assign the response from the next handler
        response = await call_next()
        return response 
    
    except Exception as e:
        # Capture and log the exception details
        error_details = traceback.format_exc()
        print(error_details)

        # Set response status to 500 (Internal Server Error)
        response.status(500)
        return response
