from .application import NexioApp 
from .sessions.middleware import SessionMiddleware
from .middlewares.logging import ErrorHandlerMiddleware
from .middlewares.common import CommonMiddleware
from .config.base import MakeConfig
from .config import set_config
from .routing import Router
from .middlewares.cors import CORSMiddleware
from .libs.auth.backends.http_auth import BasicAuthBackend
from .libs.auth.middleware import AuthenticationMiddleware
import os

def get_application(config = None) -> NexioApp:
    set_config(config)

    app = NexioApp(
        middlewares= [
            
            ErrorHandlerMiddleware(),
            CommonMiddleware(),           
            CORSMiddleware(),
            SessionMiddleware(),
            AuthenticationMiddleware(BasicAuthBackend())

        ],
        config=config
    )
    
    
    return app

