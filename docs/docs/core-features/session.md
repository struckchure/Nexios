# **Session Management in Nexios**

Session management allows you to store and persist user-specific data across multiple requests. Nexios provides a robust session interface that enables secure and configurable session handling.

---


Sessions are used to store temporary user data that persists across multiple HTTP requests. This is essential for user authentication, shopping carts, and maintaining stateful interactions in web applications.

Nexios provides a `BaseSessionInterface` that allows developers to manage sessions efficiently. It includes functionality for setting, retrieving, and deleting session data, as well as handling expiration and cookie settings.

---

## Configuring Sessions in Nexios

Before using sessions, ensure your application is configured correctly. The session configuration is stored in the `session_config` attribute of the application’s configuration.

### Example Configuration:
```python
from nexios.config import MakeConfig

config = MakeConfig({
    "secret_key","somthing-special",
    "session":{
        "session_cookie_name" :  "nexios_session",
        "session_cookie_secure" : True,  # Ensures HTTPS-only cookies
        "session_cookie_httponly" : True,  # Prevents JavaScript access
        "session_expiration_time" :1440 ,# Keeps the session persistent
        "session_permanent" : False  # Keeps the session persistent,
        "session_refresh_each_request" : False  # Refresh session on each request

    }    
})

```
### **Key Configuration Options:**
| Option                         | Description |
|---------------------------------|-------------|
| `session_cookie_name`           | Name of the session cookie |
| `session_cookie_secure`         | Enforces HTTPS-only cookies |
| `session_cookie_httponly`       | Prevents JavaScript access |
| `session_expiration_time`       | Expiration time in minutes |
| `session_permanent`             | Keeps session active even after closing the browser |
| `session_refresh_each_request`  | Refresh session expiry on every request |

---

##  Using Sessions in Nexios
Setting and Retrieving Session Data

```python

# ... 
@app.get("/endpoint")
async def manage_session(request, session):
    # Setting a session value   
    request.session.set_session("username", "Dunamis")

    # Retrieving a session value
    username = request.session.get_session("username")
    print(username)  # Output: Dunamis
```

Checking if a Session Exists
```python
if request.session.get_session("username"):
    print("Session exists")
else:
    print("Session does not exist")
```

Deleting a Session Value
```python
session.delete_session("username")
```

Retrieving All Session Data
```python
all_sessions = request.session.get_all()
print(dict(all_sessions))  # Convert items to dictionary
```

---

Session Expiration Handling

Nexios automatically manages session expiration based on the configured settings.

Checking if a Session Has Expired
```python
if request.session.has_expired():
    print("Session has expired. Please log in again.")
```

Getting Session Expiration Time
```python
expiration_time = request.session.get_expiration_time()
print(expiration_time)  # Outputs the expiration datetime
```

---



##  Session Storage Backends


By default, Nexios stores sessions in files or signed cookies:

```py
MakeConfig({
    "session_manager":"cookies" #or file
})

```

but you can implement different storage mechanisms such as

- **Database-backed sessions (MySQL, PostgreSQL)**
- **Redis-based session storage**

### **Example: Using Redis for Session Storage**
```python
from nexios.session.base import BaseSessionInterface
from redis import Redis

class RedisSession(BaseSessionInterface):
    def __init__(self, session_key: str):
        super().__init__(session_key)
        self.redis_client = Redis(host='localhost', port=6379, db=0)

    async def save(self):
        self.redis_client.set(self.session_key, self._session_cache)

    async def load(self, key: str):
        return self.redis_client.get(self.session_key)


config = MakeConfig({
    "session":{
        "backend" : RedisSession()
    }
})
```

---
## Session Security Best Practices

- **Use Secure Cookies:** Set `session_cookie_secure = True` to prevent transmission over HTTP.
- **Enable HttpOnly:** Prevents JavaScript from accessing session cookies.
- **Set Expiration:** Enforce `session_expiration_time` to prevent indefinite sessions.
- **Rotate Session Keys:** Periodically change session keys to prevent hijacking.
- **Use Encrypted Storage:** Encrypt session data when using databases or file storage.

---

## Advanced Session Use Cases

| Use Case | Implementation |
|----------|---------------|
| **Persistent Logins** | Store user authentication state in session |
| **Shopping Carts** | Keep track of items in a cart across requests |
| **Role-Based Access Control** | Store user roles and permissions in session |
| **API Rate Limiting** | Track user requests to prevent abuse |
| **CSRF Protection** | Use session tokens to validate form submissions |

---

