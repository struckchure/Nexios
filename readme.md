![Nexio Logo](docs/logo.svg)

# Nexio HTTP Framework 🚀💻

Welcome to Nexio — a lightning-fast web framework built with Python and written by TechWithDunamix, a Nigerian developer! 🇳🇬💡 Whether you're building APIs, web apps, or anything in between, Nexio is here to make your life easier and faster! ⚡

## Why Nexio? 🤔

- **Blazing Fast**: Built with performance in mind. Don't blink or you might miss it! ⚡
- **Simplicity**: Write less code, get more done. You'll spend less time debugging and more time building cool stuff. 👨‍💻
- **Easy to Use**: Everything is straightforward, from routing to database setup — no complicated setups, just plug and play! 🔌🎮

## Quick Start 🚀

Ready to get started? Here's how you can set up Nexio and make your first web app in minutes:


### 1. Install Dependencies 📦

Install Nexio and the required dependencies with pip:

```bash
pip install git+https://github.com/TechWithDunamix/Nexio.git
```

### 2. Create Your First App 💻

```bash
nexio create <app_name>
```
##### Outputs
```md
To get started
1. cd <app_name>
    
2. cd <app_name>
    
3. Your app will be available at http://localhost:8000
```
# Folder structure

```txt
project_name/
├── config/
│   ├── __init__.py
│   ├── database.py
│   └── settings.py
├── handlers/
│   ├── __init__.py
│   └── routes.py
└── main.py
```


###  Basic Example

```python
from nexio import get_application
import uvicorn
from nexio.routers import Routes
app = get_application()

async def home(req,res):
    res.json({"text" :"hello welcome to nexio"})

app.add_route(Routes("/",home))
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```


# Nexio Project Structure Documentation


```
project_name/
├── config/
│   ├── __init__.py
│   ├── database.py
│   └── settings.py
├── handlers/
│   ├── __init__.py
│   └── routes.py
└── main.py
```

## File Descriptions

### main.py
The application entry point and core configuration file.
```python
# Key responsibilities:
- Initializes the Nexio application
- Sets up database connections
- Configures startup/shutdown hooks
- Mounts routes
- Starts the ASGI server
```

Key features:
- `get_application()`: Creates the main ASGI application instance
- `connect_db()`: Database connection setup on startup
- `disconnect_db()`: Clean database shutdown
- Uvicorn server configuration

### config/database.py
Database configuration and connection settings.
```python
# Key responsibilities:
- Defines database connection parameters
- Configures ORM settings
- Sets up model locations
```

Key components:
- `TORTOISE_ORM`: ORM configuration dictionary
  - Database URL configuration
  - Model locations and namespacing
  - Connection settings

### config/settings.py
Application-wide configuration and settings.
```python
# Key responsibilities:
- Defines core application settings
- Manages security configurations
- Sets environment-specific variables
```

Key settings:
- `AppConfig`: Application configuration class
- `SECRET_KEY`: Security key for sessions/encryption
- Can be extended for additional settings:
  - Debug modes
  - API versions
  - Environment configurations

### handlers/routes.py
HTTP request handlers and route definitions.
```python
# Key responsibilities:
- Defines endpoint handlers
- Processes HTTP requests
- Returns responses
```

Key components:
- `home_handler`: Example route handler
- Request processing logic
- Response formatting
- URL parameter handling

## Usage Notes

1. **Configuration Priority**:
   - `settings.py` loads first
   - `database.py` uses settings for configuration
   - `main.py` brings everything together

2. **Database Management**:
   - Uses Tortoise ORM
   - Automatic schema generation
   - Connection lifecycle management

3. **Request Flow**:
```
Request → main.py → routes.py → handler → response
```

4. **Development Workflow**:
   1. Modify settings in `config/`
   2. Add routes in `handlers/routes.py`
   3. Run application from `main.py`

## Common Extensions

The basic structure can be extended with:

1. **Additional Directories**:
   - `models/`: Database models
   - `middlewares/`: Custom middleware
   - `schemas/`: Data validation
   - `services/`: Business logic

2. **Configuration Files**:
   - `logging.py`: Logging configuration
   - `middleware.py`: Middleware settings
   - `constants.py`: Application constants

## Best Practices

1. **Configuration**:
   - Keep sensitive data in environment variables
   - Use different settings for development/production
   - Document all configuration options

2. **Route Handlers**:
   - Keep handlers focused and simple
   - Use type hints for better code clarity
   - Return consistent response formats

3. **Database**:
   - Use migrations for schema changes
   - Implement proper connection pooling
   - Handle connection errors gracefully

## Quick Start
```bash
# 1. Install dependencies
pip install git+https://github.com/TechWithDunamix/Nexio.git


# 2. Run the application
uvicorn main:app --reload

# 3. Access the API
curl http://localhost:8000
```

The application will be available at `http://localhost:8000` with:
- Database auto-configuration
- Basic route setup
- Error handling
- Clean shutdown support