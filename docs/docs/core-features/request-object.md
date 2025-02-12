Request Object Documentation for Nexios   Applications

## Overview
The Request object in Nexios represents an HTTP request sent to the server. It encapsulates all the data that is sent by the client, such as headers, query parameters, form data, cookies, and more. The Request object is a central part of the request-response cycle in Nexios and provides various methods to access and manipulate the incoming data.

<hr />

## path_params

<p>
In Nexios, path parameters are typically defined in the route path using placeholders, like  /user/{user_id}. When a request is made to this route, the value for user_id will be captured and can be accessed via request.path_params.</p>
```py
from nexios import get_application

app = get_application()

#Get path param
@app.get('/user/{user_id}')
async def get_user(req):
    user_id = request.path_params.user_id  # Access path parameter 'user_id'
    return return res.text('User ID is: {user_id}')

#Get all path params at ounce
@app.get('/user/{post_id}/comment/{comment_id}')
async def get_user(req):
    path_prams = request.path_params()  # return parameters as a dict'
    return return res.json(path_prams)
```

## query_param()
Get the values of path parameters.

<p>Query parameters are the key-value pairs in the URL, typically found after the ? symbol. For example, in the URL /search?query=nexios&page=2, query and page are query parameters.
In Nexios, you would access these query parameters through the request object, often using methods or attributes designed for extracting them. For example, you might retrieve a parameter like request.query["query"] to get the value of query.</p>

```py
from nexios import get_application

app = get_application()

#Get query param
@app.get('/user')
def user(req, res):
    user_id = request.query_params.get('id')  # Access query parameters
    return res.json({"user_id":user_id})


#Get query all params
@app.get('/user')
def user(req, res):
    query_params = request.query_params()  # Access query parameters
    return res.json(query_params)

```

## headers()
<p>  Headers in HTTP are like the notes that come with a package when it's sent. They provide important details about the package (data), such as its type, how it should be handled, or any special instructions, like authentication info.

For example:

`Content-Type` tells the server what kind of data the client is sending, like saying, "I'm sending a JSON file."

`Authorization` might be like a key or password, letting the server know who the client is.
User-Agent identifies which browser or app is making the request.
Accept tells the server what type of response the client wants, like asking, "Can you send me that in JSON format?"
</p>

```py

@app.get("/headers")
async def route_handler(req, res):

    print(req.headers['key']) #return the Value for the key else raise None`
    print(req.headers.items()) #return a key value tuple in a list [(key,value),(key,value)]
```

## body()
<p> This property asynchronously retrieves the raw body content of the request. The body is typically the data sent by the client (e.g., form data, JSON). The body is retrieved in chunks, and the method ensures that all data is read before returning it.</p>

```py
@app.post("/endpoint")
async def route_handler(req, res):
  body = await request.body()
  print(body)
  return res.json({"message":"text received succesfully"})
```

## body()
<p> This property asynchronously parses Parses the request body of type application/json
 as JSON. It tries to decode the body into a Python dictionary. If the body is not valid JSON or cannot be decoded, it returns an empty dictionary. This is useful for APIs that expect JSON input.</p>

```py
@app.post("/endpoint")
async def route_handler(req, res):
  body = await request.json
  print(body)
  return res.json({"message":"text received succesfully"})
```

## form_data()
<p>This property asynchronously parses the request body as form data. It handles both multipart/form-data (used for file uploads) and application/x-www-form-urlencoded (used for standard form submissions). The method ensures that both types are handled properly and returns the parsed form data as a dictionary</p>

```py
@app.post("/endpoint")
async def route_handler(req, res):
  body = await request.form_data
  return response.json({"text":"success"})

```

##  stream()

This method asynchronously yields chunks of the request body. It is useful for handling large requests that are too big to fit into memory at once. This method can be used to stream data from the client in smaller parts, which can be processed incrementally.

```py
@app.post("/endpoint")
async def route_handler(req, res):
  
    # Start streaming the request body
    chunked_data = []
    
    async for chunk in await request.stream():
        # Collecting chunks to simulate processing
        chunked_data.append(chunk.decode())

    # Join all the chunks and return a response
    full_data = ''.join(chunked_data)
    return response.text("Data recieve successfully")

```

## content-type

Content-Type is an HTTP header that specifies the format of the data being sent, helping the server or client know how to interpret it (e.g., JSON, HTML, or file uploads).

```py
@app.get("/endpoint")
async def route_handler(req, res):

  print(request.content_type) # Returns the MIME type of the request content.
```

## client()
The `.client()` method returns a tuple with the client's host (IP address or hostname) and port (connection port). It's useful for logging, identifying request origins, or applying specific rules.

```py
@app.get("/endpoint")
async def route_handler(req, res):

  print(request.client()) #Returns client information as a tuple of (host, port).
```
## cookies


Cookies are small pieces of data stored by the browser on a user's device. They are sent between the server and client with each HTTP request, allowing the server to remember user preferences, authentication details, or session information. Cookies can be persistent (remaining for a specified duration) or session-based (deleted when the browser is closed). They are often used for things like keeping users logged in or tracking user behavior across sessions. in nexio thie attr is typically stores as dict and access as same .

```py

@app.route("/user-session")
async def route_handler(request, response):

    print(request.cookies['key']) #return the Value for the key else raise KeyError`
    print(request.cookies.items()) #return a key value tuple in a list [(key,value),(key,value)]
```

## method 
The method attribute provides the HTTP method used for the request. This is typically one of the standard HTTP methods such as GET, POST, PUT, DELETE, PATCH, HEAD, or OPTIONS.

```py
@app.route("/endpoint")
async def route_handler(req, res):
  if req.method == "POST":
      create_user()
      return res.json({"success":"user created succesfully"})
  return res.json(get_user_profile())

```

## path
The path attribute provides the path of the request URL. This is the part of the URL that comes after the domain name and port.

```py
@app.route("/endpoint")
async def route_handler(req, res):
   print(req.path)
   ...

```

## files
The files attribute provides access to uploaded files in the request. This is typically used when handling multipart/form-data requests, such as file uploads.

```py
@app.route("/endpoint")
async def route_handler(req, res):
    files = await req.files
    for field_name, file in files.items():
        print(f"Field Name: {field_name}, File Name: {file.filename}")
   ...

```
## client
The client attribute provides information about the client (user) making the request. It returns a tuple containing the client's host (IP address) and port.
```py
@app.route("/client-info")
async def client_info_handler(req, response):
    client = req.client
    if client:
        host, port = client
        print(f"Client Host: {host}, Client Port: {port}")
    else:
        print("No client information available.")

```

## build_absolute_uri
The build_absolute_uri method constructs a fully qualified absolute URI using the base URL of the request and an optional path or query parameters.
```py
@app.route("/client-info")
async def client_info_handler(req, response):
    absolute_uri = request.build_absolute_uri("/example", {"param": "value"})
    print(absolute_uri) # e.g., "https://example.com/example?param=value"

```