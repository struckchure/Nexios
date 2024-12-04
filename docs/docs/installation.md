

---

# Installation Guide for Nexios

To get started with **Nexios**, follow these simple steps to install the framework and set up your environment.

---

## Step 1: Install Nexios

Use `pip` to install **Nexios**. Open your terminal and run:

```bash
pip install nexios
```

This will install **Nexios** along with all necessary dependencies automatically.

---

## Step 2: Install Optional Dependencies (if needed)

If you want to use optional features like **Tortoise ORM** or **Redis** for session management, you can install them separately. However, the required libraries will be automatically installed along with **Nexios**.

To install **Tortoise ORM**:

```bash
pip install tortoise-orm
```

To install **Redis**:

```bash
pip install redis
```

---

## Step 3: Create a New Project

Create a directory for your Nexios project:

```bash
mkdir my_nexios_project
cd my_nexios_project
```

Then, create a file called `main.py` and add the following content to start a basic Nexios app:

```python
from nexios import get_application
from nexios.http import request, response

app = get_application()

@app.route("/")
async def hello_world(req: request.Request, res: response.NexioResponse):
    return res.json({"message": "Hello, Nexios!"})


```

---

## Step 4: Run Your Application

To run the Nexios application, use the following command:

```bash
uvicorn main:app --reload
```

Your application should now be running at `http://127.0.0.1:8000`.

---

## Conclusion

You’ve successfully installed **Nexios** and set up your first project! Now you’re ready to build web applications with **Nexios**. Enjoy building!

--- 

[Back to top](#top)

--- 

This setup ensures users are guided only through the installation process, with no extra details beyond what's necessary to get started.