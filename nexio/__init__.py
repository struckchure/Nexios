from .application import NexioApp 
from .sessions.middlewares import SessionMiddleware
from .middlewares.logging import ErrorHandlerMiddleware
from .middlewares.common import CommonMiddleware
from .config.settings import BaseConfig
from .routers import Router
from .middlewares.cors import CORSMiddleware
def get_application(config = BaseConfig) -> NexioApp:
    config=config()
    
    app = NexioApp(
        middlewares= [
            ErrorHandlerMiddleware(),
            CommonMiddleware(),
            CORSMiddleware(allow_origins="http://127.0.0.1:5500")

        ],
        config=config
    )

    return app