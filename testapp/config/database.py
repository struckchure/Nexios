import os

TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{os.path.join(os.path.dirname(__file__), '../db.sqlite3')}"
    },
    "apps": {
        "models": {
            "models": ["nexio.sessions.models"], 
            "default_connection": "default",
        },
    },
}
