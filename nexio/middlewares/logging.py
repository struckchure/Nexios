import logging
import time
import traceback
from nexio.http.request import Request
from nexio.http.response import Response,NexioResponse
from .base import BaseMiddleware
# Set up advanced logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Function to log exceptions
def log_exception(exception: Exception):
    logger.error("An error occurred: %s", exception)
    logger.error("Traceback: %s", traceback.format_exc())

# Logging middleware
async def logging_middleware(request: Request, response: Response, nex):
    start_time = time.time()  # Start time to track request processing duration
    try:
        # Log the incoming request
        logger.info(f"Received {request.method} request for {request.url.path}")
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Request query params: {request.query_params}")
        if request.body:
            logger.debug(f"Request body: {await request.body()}")
        
        # Process the request
        await nex()

        # Log the outgoing response
        logger.info(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        if response.body:
            logger.debug(f"Response body: {response.body.decode()}")
        
        # Log the time taken for the request
        duration = time.time() - start_time
        logger.info(f"Request processing time: {duration:.2f} seconds")

    except Exception as e:
        # Log the exception if one occurs
        log_exception(e)

        # Optionally, set a custom error response or let the default error handler handle it
        response.status_code = 500
        response.body = b"Internal Server Error"
        logger.error(f"Error occurred while processing the request: {e}")


# Example usage of custom middleware
class LoggingMiddleware(BaseMiddleware):
    """
    Example middleware that logs request and response details.
    """
    
    async def process_request(self, request: Request, response: NexioResponse) -> None:
        print(f"Processing request to: {request.url.path}")
    
    async def process_response(self, request: Request, response: NexioResponse) -> NexioResponse:
        print(f"Processing response from: {request.url.path}")
        return response
    
    async def process_exception(self, request: Request, response: NexioResponse, exc: Exception) -> NexioResponse:
        print(f"Error processing {request.url.path}: {str(exc)}")
        return await super().process_exception(request, response, exc)