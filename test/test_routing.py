from nexios import get_application, NexiosApp
import pytest
from nexios.testing import Client
from nexios.http import Request, Response
from nexios.routing import Router,Routes

app: NexiosApp = get_application()

@pytest.fixture(autouse=True)
async def async_client():
    async with Client(app, log_requests=True) as c:
        yield c

async def test_route_decorator(async_client: Client):
    # Define routes
    @app.get("/get")
    async def handle_get(req: Request, res: Response):
        return res.json({"method": req.method})

    @app.post("/post")
    async def handle_post(req: Request, res: Response):
        return res.json({"method": req.method})

    @app.delete("/delete")
    async def handle_delete(req: Request, res: Response):
        return res.json({"method": req.method})

    @app.put("/put")
    async def handle_put(req: Request, res: Response):
        return res.json({"method": req.method})

    @app.patch("/patch")  # Corrected from @app.put to @app.patch
    async def handle_patch(req: Request, res: Response):
        return res.json({"method": req.method})

    # Test GET request
    get_response = await async_client.get("/get")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test POST request
    post_response = await async_client.post("/post")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}

    # Test DELETE request
    delete_response = await async_client.delete("/delete")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"method": "DELETE"}

    # Test PUT request
    put_response = await async_client.put("/put")
    assert put_response.status_code == 200
    assert put_response.json() == {"method": "PUT"}

    # Test PATCH request
    patch_response = await async_client.patch("/patch")
    assert patch_response.status_code == 200
    assert patch_response.json() == {"method": "PATCH"}
    
    
    
    
async def test_add_route_method(async_client: Client):
    # Define route handlers
    async def handle_get(req: Request, res: Response):
        return res.json({"method": req.method})

    async def handle_post(req: Request, res: Response):
        return res.json({"method": req.method})

    async def handle_delete(req: Request, res: Response):
        return res.json({"method": req.method})

    async def handle_put(req: Request, res: Response):
        return res.json({"method": req.method})

    async def handle_patch(req: Request, res: Response):
        return res.json({"method": req.method})

    # Add routes with their respective methods
    app.add_route(Routes("/get", handle_get, methods=["GET"]))
    app.add_route(Routes("/post", handle_post, methods=["POST"]))
    app.add_route(Routes("/delete", handle_delete, methods=["DELETE"]))
    app.add_route(Routes("/put", handle_put, methods=["PUT"]))
    app.add_route(Routes("/patch", handle_patch, methods=["PATCH"]))

    # Test GET request
    get_response = await async_client.get("/get")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test POST request
    post_response = await async_client.post("/post")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}

    # Test DELETE request
    delete_response = await async_client.delete("/delete")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"method": "DELETE"}

    # Test PUT request
    put_response = await async_client.put("/put")
    assert put_response.status_code == 200
    assert put_response.json() == {"method": "PUT"}

    # Test PATCH request
    patch_response = await async_client.patch("/patch")
    assert patch_response.status_code == 200
    assert patch_response.json() == {"method": "PATCH"}
    
    
async def test_route_decorator_allowed_methods(async_client: Client):
    # Define a route with allowed methods (GET and POST)
    @app.route("/test", methods=["GET", "POST"])
    async def handle_test(req: Request, res: Response):
        return res.json({"method": req.method})

    # Test allowed GET request
    get_response = await async_client.get("/test")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test allowed POST request
    post_response = await async_client.post("/test")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}

    # Test disallowed PUT request
    put_response = await async_client.put("/test")
    assert put_response.status_code == 405  # Method Not Allowed
    assert "Allow" in put_response.headers  # Ensure the Allow header is present
    assert put_response.headers["Allow"] == "GET, POST"  # Ensure the allowed methods are listed

    # Test disallowed DELETE request
    delete_response = await async_client.delete("/test")
    assert delete_response.status_code == 405  # Method Not Allowed
    assert "Allow" in delete_response.headers  # Ensure the Allow header is present
    assert delete_response.headers["Allow"] == "GET, POST"  # Ensure the allowed methods are listed

    # Test disallowed PATCH request
    patch_response = await async_client.patch("/test")
    assert patch_response.status_code == 405  # Method Not Allowed
    assert "Allow" in patch_response.headers  # Ensure the Allow header is present
    assert patch_response.headers["Allow"] == "GET, POST"  # Ensure the allowed methods are listed
    
    
    
async def test_routers_no_prefix(async_client: Client):
    
    router = Router()
    
    @router.get("/")
    async def handle_get(req:Request, res:Response):
        return res.text("i love you")
    
    app.mount_router(router)
    
    
    
    response = await async_client.get("/")
    
    assert response.status_code == 200
    
    
async def test_routers_with_prefix(async_client: Client):
    
    router = Router(prefix="/api")
    
    @router.get("/resource")
    async def handle_get(req:Request, res:Response):
        return res.text("i love you")
    
    app.mount_router(router)
    
    
    
    response = await async_client.get("/api/resource")
    
    assert response.status_code == 200
    


async def test_path_prams(async_client :Client):
    @app.get("/item/{id}")
    async def get_items(req:Request, res:Response):
        id = req.path_params.id
        return res.text(id)
    
    
    response = await async_client.get("/item/4")
    assert response.text == "4"
    
    
async def test_duplicate_params(async_client :Client):
    async def get_items(req:Request, res:Response):
        id = req.path_params.id
        return res.text(id)
    
    with pytest.raises(
        ValueError,
        match="Duplicated param name id at path /{id}/{id}",
    ):
        Routes("/{id}/{id}", get_items)
    
    
    response = await async_client.get("/item/4") 
    assert response.text == "4"