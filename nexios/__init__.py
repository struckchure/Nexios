from .application import NexioApp 
from .sessions.middleware import SessionMiddleware
from .middlewares.logging import ErrorHandlerMiddleware
from .middlewares.common import CommonMiddleware
from .config.base import MakeConfig
from .config import set_config
from .routing import Router
from .middlewares.cors import CORSMiddleware
import os

def get_application(config = None) -> NexioApp:
    print("condif if",config)
    set_config(config)

    app = NexioApp(
        middlewares= [
            
            ErrorHandlerMiddleware(),
            CommonMiddleware(),           
            CORSMiddleware(),
            SessionMiddleware(),

        ],
        config=config
    )
    
    
    return app

