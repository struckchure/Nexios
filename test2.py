from nexio import get_application
import uvicorn
from nexio.routers import Routes
app = get_application()

async def home(req,res):
    res.json({"text" :"hello welcome to nexio"})

app.add_route(Routes("/",home))
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)