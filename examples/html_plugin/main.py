import sys
from pathlib import Path

from nexios.config.base import MakeConfig
from nexios.plugins.rpc.server import RpcPlugin
from nexios.plugins.static_file import StaticFilePlugin

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from nexios import get_application
from nexios.plugins import HTMLPlugin

config = MakeConfig({"secret_key": "hello"})
config.cors = {
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["Authorization", "X-Requested-With"],
    "allow_credentials": True,
    "max_age": 600,
    "debug": True,
}
app = get_application(config)

HTMLPlugin(app, config={"root": "routes"})
StaticFilePlugin(app, config={"url": "/js", "file_dir": "./js"})
RpcPlugin(app)
