from nexios import get_application,NexiosApp
import pytest
from nexios.http import Request,Response
from nexios.testing import Client
app :NexiosApp = get_application()
@app.get("/response/text")
async def send_text_response(req: Request, res :Response):
    return res.text("Hello from nexios")

@app.get("/response/bytes")
async def send_byes_response(req: Request, res :Response):
    return res.resp(b"XXXX",content_type="image/png")

@app.get("/response/json-none")
async def send_json_none_response(req: Request, res :Response):
    return res.json(None) #type:ignore

@app.get("/response/redirect")
async def send_redirect_response(req: Request, res :Response):
    return res.redirect("http://google.com")

@pytest.fixture
async def async_client():
    async with  Client(app) as c:
        yield c 
        
        
async def test_text_response(async_client :Client):
    response  = await async_client.get("/response/text")
    assert response.text == "Hello from nexios"
    assert response.status_code == 200
    
    
async def test_byte_response(async_client :Client):
    response  = await async_client.get("/response/bytes")
    assert response.content == b"XXXX"
    assert response.status_code == 200
    
async def test_json_none_response(async_client :Client):
    response  = await async_client.get("/response/json-none")
    assert response.json () is None
    assert response.status_code == 200 
    
    
async def test_redirect_response(async_client :Client):
    response  = await async_client.get("/response/redirect")
    assert response.url == "http://google.com"
    
    