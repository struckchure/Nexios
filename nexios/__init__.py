from .application import NexioApp 
from .sessions.middleware import SessionMiddleware
from .middlewares.logging import ErrorHandlerMiddleware
from .middlewares.common import CommonMiddleware
from .middlewares.csrf import CSRFMiddleware

from .config.base import MakeConfig
from .config import set_config
from .routing import Router
from .middlewares.cors import CORSMiddleware

def get_application(config = None) -> NexioApp:
    set_config(config)

    app = NexioApp(
        middlewares= [
            
            ErrorHandlerMiddleware(),
            CommonMiddleware(),           
            CORSMiddleware(),
            SessionMiddleware(),
            CSRFMiddleware()

        ],
        config=config
    )
    
    
    return app

