
---

![nexios Logo](docs/logo.svg)  
# nexios API Framework 🚀💻  

Welcome to **nexios**, an ultra-fast Python web framework crafted by **TechWithDunamix** — a visionary developer from Nigeria! 🇳🇬💡 nexios is designed to revolutionize API development by combining speed, simplicity, and a familiar, intuitive structure inspired by Express.js-style controllers. ⚡  

With nexios, developers can enjoy a clean, organized codebase that closely mirrors the lightweight yet powerful design of Express.js, making it an excellent choice for those transitioning from JavaScript or seeking a productivity-focused framework in Python.  

---  

## Why Choose nexios? 🤔  

- **⚡ Unrivaled Speed**: Deliver high-performance web applications with ease.  
- **👨‍💻 Developer-Centric**: Streamlined codebase designed for maximum productivity.  
- **🔌 Seamless Integration**: Minimal setup and configuration, perfect for developers at any level.  
- **📚 Familiar Structure**: Inspired by Express.js, nexios offers a straightforward controller style that simplifies routing and API logic.  

---  

## Quick Start 🚀  

Get up and running with nexios in just a few simple steps!  

---  

### Installation  

Install nexios using pip:  

```shell  
pip install nexios  
```  

### Basic Example  

Here’s a quick example of how easy it is to build APIs with nexios:  

```py  
from nexios.http import Request, Response  
from nexios import get_application  

app = get_application()  

@app.get("/api")  
async def get_api_resource(request: Request, response: Response):  
    return response.json({"message": "Hello, World!"})  
```  

This controller-style structure allows you to define routes and their corresponding logic seamlessly, just like in Express.js!  

### Running the Application  

Since nexios is built as an `ASGI` framework, it requires an ASGI server like `uvicorn`. Conveniently, nexios comes bundled with `uvicorn` for hassle-free deployment!  

To start your app, simply run:  

```shell  
uvicorn main:app --reload  
```  

---  

With nexios, API development becomes faster, cleaner, and more intuitive, empowering you to build scalable projects with minimal effort.