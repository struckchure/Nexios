# Nexio Request object

The Nexios Request is an object that is provided by nexios in the handler arguments . 


## .route_params

`In Nexio, route parameters are dynamic placeholders in the URL path, enclosed in curly braces. They capture specific values from the URL and are passed as function arguments. These parameters allow you to define flexible, resource-based routes that can adapt to different inputs, such as IDs or other identifiers, making your API more versatile and dynamic.`

```py

@app.route("/posts/{post_id}")
async def route_handler(request, response):

    print(request.route_params.post_id) #return the pramater passed as `/post/90`
    print(request.route_params.items()) #return a key value tuple in a list [(key,value),(key,value)]

```

## .cookies


`Cookies are small pieces of data stored by the browser on a user's device. They are sent between the server and client with each HTTP request, allowing the server to remember user preferences, authentication details, or session information. Cookies can be persistent (remaining for a specified duration) or session-based (deleted when the browser is closed). They are often used for things like keeping users logged in or tracking user behavior across sessions. in nexio thie attr is typically stores as dict and access as same .`




```py

@app.route("/user-session")
async def route_handler(request, response):

    print(request.cookies['key']) #return the Value for the key else raise KeyError`
    print(request.cookies.items()) #return a key value tuple in a list [(key,value),(key,value)]
```

## .headers

` Headers in HTTP are like the notes that come with a package when it's sent. They provide important details about the package (data), such as its type, how it should be handled, or any special instructions, like authentication info.`

For example:

`Content-Type` tells the server what kind of data the client is sending, like saying, "I'm sending a JSON file."

`Authorization` might be like a key or password, letting the server know who the client is.
User-Agent identifies which browser or app is making the request.
Accept tells the server what type of response the client wants, like asking, "Can you send me that in JSON format?"

Essentially, headers help ensure that the server and client understand each other and can properly exchange information.`

```py

@app.route("/headers")
async def route_handler(request, response):

    print(request.headers['key']) #return the Value for the key else raise None`
    print(request.headers.items()) #return a key value tuple in a list [(key,value),(key,value)]
```

## .content-type

Content-Type is an HTTP header that specifies the format of the data being sent, helping the server or client know how to interpret it (e.g., JSON, HTML, or file uploads).

```py
@app.route("/endpoint")
async def route_handler(request, response):

  print(request.content_type) # Returns the MIME type of the request content.
```

## .client
The `.client()` method returns a tuple with the client's host (IP address or hostname) and port (connection port). It's useful for logging, identifying request origins, or applying specific rules.

```py
@app.route("/endpoint")
async def route_handler(request, response):

  print(request.client()) #Returns client information as a tuple of (host, port).
```

## .query_params
`The .query_params method extracts query parameters from a URL and returns them as a dictionary.`

For example, if the URL is:

`/search?category=books&category=electronics&sort=price`

```py
@app.route("/endpoint")
async def route_handler(request, response):

  print(request.query_params()) #The method would return: {'category': ['books', 'electronics'], 'sort': 'price'}
```

## .base_url

`the base URL refers to the root URL for the API, from which all endpoint paths are built. It's the starting point for constructing full URLs in your application.`

```py
@app.route("/endpoint")
async def route_handler(request, response):

  print(request.base_url) 

```

## .body()
`This property asynchronously retrieves the raw body content of the request. The body is typically the data sent by the client (e.g., form data, JSON). The body is retrieved in chunks, and the method ensures that all data is read before returning it.`

```py
@app.route("/endpoint")
async def route_handler(request, response):
  body = await request.body()
  print(request.query_params()) #The method would return: {'category': ['books', 'electronics'], 'sort': 'price'}

```

## .json()

`This property asynchronously parses the request body as JSON. It tries to decode the body into a Python dictionary. If the body is not valid JSON or cannot be decoded, it returns an empty dictionary. This is useful for APIs that expect JSON input.`


```py
@app.route("/endpoint")
async def route_handler(request, response):
  body = await request.json()
  print(request.query_params()) #The method would return: {'category': ['books', 'electronics'], 'sort': 'price'}

```

## .form_data()

`This property asynchronously parses the request body as form data. It handles both multipart/form-data (used for file uploads) and application/x-www-form-urlencoded (used for standard form submissions). The method ensures that both types are handled properly and returns the parsed form data as a dictionary.`

```py
@app.route("/endpoint")
async def route_handler(request, response):
  body = await request.form_data()
  return response.json({"text":"success"})

```

##  .stream()

`This method asynchronously yields chunks of the request body. It is useful for handling large requests that are too big to fit into memory at once. This method can be used to stream data from the client in smaller parts, which can be processed incrementally.`

```py
@app.route("/endpoint")
async def route_handler(request, response):
  
    # Start streaming the request body
    chunked_data = []
    
    async for chunk in await request.stream():
        # Collecting chunks to simulate processing
        chunked_data.append(chunk.decode())

    # Join all the chunks and return a response
    full_data = ''.join(chunked_data)
    return response.send("Data recieve successfully")

```