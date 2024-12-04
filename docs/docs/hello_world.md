# Simple Hello world example

> Here's the simplest Nexios app you can make—it's just one file. This is different from what you'd get with the Nexios CLI tool, which sets up a full app with multiple Python files and folders for different tasks.



```python

from nexios import NexioApp

app = NexioApp()
@app.route("/api/endpoint",methods = ['get'])
async def endpoint_handler(request, response):

    response.json({
        "text":"Welcome to nexios
    })

```


# Running Locally

 
1. ensure you have followed the  [Installation guide](installation.md)

2. Just like other python asgi frameworks(Fastapi,etc) Nexios uses uvicorn as it the server , you can run it as below

```bash
uvicorn main:app --reload
```

- The main should be the name of the file the app is located at 
- The app should be the nexioapp instance 
- the reload flag ensure the server listens for changes in your files

Learn more about [Uvicorn](https://www.uvicorn.org)

> [__Request Object__](core-features/request-object.md): This object contains all the information about the incoming HTTP request, such as headers, body data, query parameters, and more. You can interact with this object to retrieve the data sent by the client.

> [__Response Object__](core-features/response-object.md): This object represents the response that will be sent back to the client. You can use it to send data, set headers, and define the status code of the response.

[__Top to page__](#top)