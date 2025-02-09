from nexios import get_application

async def handle_server_error(req,res,exc):
    return res.json({"err":"Hello"})
app = get_application()
@app.get("")
async def index(req, res):
    print(name)
    return res.json({"text":"Helloo world"})