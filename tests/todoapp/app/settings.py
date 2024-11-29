from nexios.config.settings import BaseConfig
import os
migration = {
    "connections": {
        "default": f"sqlite://{os.path.join(os.path.dirname(__file__), 'database.db')}"
    },
    "apps": {
        "models": {
            "models": ["nexio.sessions.models","aerich.models","models"], 
            "default_connection": "default",
        },
    },
}

class AppConfig(BaseConfig):
    SECRET_KEY = "your-secret-key"
    CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:5500"]
