from nexios import get_application
from nexios.routing import Routes
from .config import nexios_config
from .controllers import index
app = get_application(
    config=nexios_config
)

app.add_route(Routes("/",index))


""" you can add middleware
    app.add_middleware(...)
"""