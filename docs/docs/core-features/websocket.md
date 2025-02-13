
WebSockets allow for **full-duplex communication** between a client and a server over a single, long-lived connection. This makes them ideal for real-time applications like chat apps, live notifications, and gaming.

Nexios provides built-in support for WebSockets through its `WebSocket` class and the `@app.websocket_route` decorator. These tools make it easy to create WebSocket endpoints and handle real-time communication.

---

## Basic WebSocket Endpoint

A basic WebSocket endpoint in Nexios can be created using the `@app.websocket_route` decorator. Here’s an example:

```python

from nexios.websockets import WebSocket, WebSocketDisconnect
# ...

@app.websocket_route("/ws") #or router.ws_route
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    try:
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            # Send a response back to the client
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        # Handle client disconnection
        print("Client disconnected")

if __name__ == "__main__":
    app.run()
```

### Explanation:

- **`@app.websocket_route("/ws")`**: This decorator defines a WebSocket route at the path `/ws`.
- **`websocket.accept()`**: Accepts the WebSocket connection. This is required to establish the connection.
- **`websocket.receive_text()`**: Waits for a text message from the client.
- **`websocket.send_text()`**: Sends a text message back to the client.
- **`WebSocketDisconnect`**: An exception that is raised when the client disconnects. You can use this to clean up resources or log the disconnection.

---

##  Class-Based WebSocket Controller

For more complex applications, you can use **class-based controllers** to encapsulate WebSocket logic. This approach improves code organization and reusability.

Here’s an example of a class-based WebSocket controller:

```python
from nexios.websockets import WebSocket
from nexios.websocket.consumer import WebSocketEndpoint
from nexios.routing import WebsocketRoutes
#.....
class WebSocketController:
 

    async def on_connect(self, websocket: WebSocket):
        """Accept the WebSocket connection."""
        await websocket.accept()
        print("WebSocket connection accepted.")

    async def on_receive(self, websocket: WebSocket):
        """Handle incoming WebSocket messages."""
        try:
            while True:
                # Receive a message from the client
                data = await websocket.receive_text()
                print(f"Received message: {data}")
                # Send a response back to the client
                await self.send_text(f"Echo: {data}")
        except WebSocketDisconnect:
            # Handle client disconnection
            print("Client disconnected.")

app.add_ws_route(WebSocketController())


```

### Explanation:

- **`WebSocketController`**: A class that encapsulates WebSocket logic.
- **`aawait websocket.accept()`**: Accepts the WebSocket connection.
- **`on_receive`**: Handles incoming messages 
- **`send_text`**: Sends a message back to the client.

---

## Handling JSON Data

WebSockets often exchange JSON data for structured communication. Here’s how you can handle JSON messages in Nexios:

```python
from nexios.websockets import WebSocket, WebSocketDisconnect

#...

@app.websocket_route("/ws/json")
async def websocket_json_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"response": "JSON received"})
    except WebSocketDisconnect:
        print("Client disconnected")
```


- **`receive_json`**: Parses incoming JSON data into a Python dictionary.
- **`send_json`**: Converts a Python dictionary into a JSON string.

---

## Broadcasting Messages

To broadcast messages to all connected clients, you can maintain a list of active WebSocket connections:

```python
from nexios.websockets import WebSocket, WebSocketDisconnect

active_connections = []

@app.websocket_route("/ws/broadcast")
async def websocket_broadcast_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Add the connection to the list of active connections
    active_connections.append(websocket)
    try:
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            # Broadcast the message to all active connections
            for connection in active_connections:
                await connection.send_text(f"Broadcast: {data}")
    except WebSocketDisconnect:
        # Remove the connection from the list of active connections
        active_connections.remove(websocket)
        print("Client disconnected")
```


- **`active_connections`**: A list to store all active WebSocket connections.
- **Broadcasting**: Iterates over all connections and sends the same message.

---

## Error Handling

Handle errors gracefully in WebSocket endpoints:

```python

from nexios.websockets import WebSocket, WebSocketDisconnect

app = Nexios()

@app.websocket_route("/ws/error")
async def websocket_error_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "error":
                # Simulate an error
                raise ValueError("Simulated error")
            await websocket.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        # Handle other exceptions
        print(f"Error: {e}")
        await websocket.send_text(f"Error: {str(e)}")

```

---

##  Authentication and Authorization

You can implement authentication by validating tokens or credentials during the WebSocket handshake:

```python

from nexios.websockets import WebSocket, WebSocketDisconnect

app = Nexios()

@app.websocket_route("/ws/secure")
async def websocket_secure_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Get the token from the query parameters
    token = websocket.query_params.get("token")
    if token != "secret-token":
        # Close the connection if the token is invalid
        await websocket.close(code=1008, reason="Unauthorized")
        return
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Secure message: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

```


## WebSocket Router and Middleware in Nexios  

### **WebSocket Router**  

In **Nexios**, the `WebsocketRoutes` class helps manage multiple WebSocket endpoints efficiently. Instead of defining WebSocket routes directly on `app`, you can organize them using `WebsocketRoutes` and mount them to the app.

#### **Example: Using WebSocket Router**
```python
from nexios.websockets import WebSocket, WebSocketDisconnect
from nexios.routing import WSRouter

ws_router = WSRouter()

@ws_router.ws_route("/chat")
async def chat_websocket(websocket: WebSocket):
    """Handles WebSocket connections for chat."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Chat Message: {data}")
    except WebSocketDisconnect:
        print("Chat client disconnected")

@ws_router.ws_route("/notifications")
async def notifications_websocket(websocket: WebSocket):
    """Handles WebSocket connections for notifications."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Notification received: {data}")
    except WebSocketDisconnect:
        print("Notification client disconnected")

# Mount the WebSocket router to the main app
app.mount_ws_router(ws_router)
```

### **Benefits of Using `WSRouter`**
- **Organized Structure**: Groups multiple WebSocket endpoints together.
- **Reusability**: Can be reused across different parts of the app.
- **Easy Integration**: Mounted to the main app using `app.include_ws_router()`.

---

### **WebSocket Middleware**
Middleware in **Nexios** allows you to modify WebSocket requests **before** they reach the route handler. This is useful for **authentication, logging, or custom processing**.

#### **Example: WebSocket Authentication Middleware**
```python
from nexios.websockets import WebSocket

async def auth_check(websocket: WebSocket, call_next):
"""Middleware to check authentication token in WebSocket connections."""
    token = websocket.query_params.get("token")
    if token != "valid-token":
        await websocket.close(code=1008, reason="Unauthorized")
        return
    print("Client authenticated.")
   await call_next()

# Apply middleware to WebSocket routes
app.add_ws_middleware(auth_check)
```


### **Combining Routers and Middleware**
You can **combine routers and middleware** for a structured WebSocket setup:

```python
ws_router = WSRouter()

@ws_router.ws_route("/secured-chat")
async def secured_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Secure Chat: {data}")

app.mount_ws_router(ws_router)
app.add_ws_middleware(AuthMiddleware)  # Protect all WebSocket routes
```

---

### **Summary**
| Feature | Purpose | Example Use Case |
|---------|---------|------------------|
| **WebSocket Router (`WSRouter`)** | Groups multiple WebSocket endpoints | Chat, Notifications, Broadcasting |
| **WebSocket Middleware (`WebSocketMiddleware`)** | Pre-processes WebSocket connections | Authentication, Logging, Custom Headers |

This setup ensures **scalability, maintainability, and security** in real-time applications. Let me know if you need more details! 