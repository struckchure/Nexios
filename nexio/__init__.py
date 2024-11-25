from .application import NexioApp 
from .sessions.middlewares import SessionMiddleware
from .middlewares.logging import ErrorHandlerMiddleware
from .middlewares.common import CommonMiddleware
from .config.settings import BaseConfig
from .routers import Router
from .middlewares.base import BaseMiddleware
def get_application(config = BaseConfig):
    app = NexioApp(
        middlewares= [
            ErrorHandlerMiddleware(),
            CommonMiddleware()
        ],
        config=config()
    )

    return app