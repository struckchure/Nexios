from .application import NexioApp 
from .sessions.middleware import SessionMiddleware
from .middlewares.logging import ErrorHandlerMiddleware
from .middlewares.common import CommonMiddleware
from .middlewares.csrf import CSRFMiddleware

from .config.base import MakeConfig
from .config import set_config,DEFAULT_CONFIG
from .routing import Router
from nexios.middlewares.errors.server_error_handler import ServerErrorMiddleware
from .middlewares.cors import CORSMiddleware

def get_application(config = DEFAULT_CONFIG,
                    middlewares = [],
                    server_error_handler = None) -> NexioApp:
    set_config(config)

    app = NexioApp(
        middlewares= [
            
            ServerErrorMiddleware(handler = server_error_handler),
            CommonMiddleware(),           
            CORSMiddleware(),
            SessionMiddleware(),
            CSRFMiddleware(),
            *middlewares

        ],
        config=config
    )
    
    
    return app

