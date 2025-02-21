from typing import Dict, List, Optional, Any
import re
from pydantic import BaseModel, ValidationError

class RouteParameter(BaseModel):
    name: str
    description: Optional[str] = None
    required: bool = True
    schema_type: Dict[str, Any] = {"type": "string"}

class RouteRequest(BaseModel):
    description: Optional[str] = None
    content_type: str = "application/json"
    schema_: Dict[str, Any]
    required: bool = True

class RouteResponse(BaseModel):
    status_code: str
    description: str
    schema_: Dict[str, Any]

class APIRoute(BaseModel):
    path: str
    methods: List[str]
    summary: str
    description: Optional[str] = ""
    version: str = "v1"
    tags: Optional[List[str]] = None
    parameters: Optional[List[RouteParameter]] = None
    request: Optional[RouteRequest] = None
    responses: List[RouteResponse]
    deprecated: bool = False

    @property
    def path_parameters(self) -> List[str]:
        return re.findall(r'\{(\w+)\}', self.path)

    def validate_parameters(self):
        if self.parameters:
            param_names = {p.name for p in self.parameters}
            path_params = set(self.path_parameters)
            if not path_params.issubset(param_names):
                missing = path_params - param_names
                raise ValueError(f"Missing parameters in route {self.path}: {missing}")

class VersionedAPISchema:
    def __init__(self, title: str = "API Schema", default_version: str = "v1"):
        self.title = title
        self.default_version = default_version
        self.versions: Dict[str, List[APIRoute]] = {}
        self.base_url = "/api/{version}"
        self.servers = [
            {"url": "https://api.example.com", "description": "Production server"},
            {"url": "https://sandbox.api.example.com", "description": "Sandbox server"}
        ]

    def add_route(self, route: APIRoute):
        try:
            route.validate_parameters()
        except ValidationError as e:
            raise ValueError(f"Invalid route configuration: {e}")

        version = route.version or self.default_version
        if version not in self.versions:
            self.versions[version] = []
        self.versions[version].append(route)

    def build_openapi_schema(self) -> Dict[str, Any]:
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": "1.0.0"
            },
            "servers": self.servers,
            "paths": {},
            "components": {
                "schemas": {},
                "parameters": {}
            }
        }

        for version, routes in self.versions.items():
            versioned_base = self.base_url.format(version=version)
            
            for route in routes:
                full_path = f"{versioned_base}{route.path}"
                parameters = []
                
                # Process path parameters
                for param in route.path_parameters:
                    parameters.append({
                        "name": param,
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    })

                # Add additional parameters
                if route.parameters:
                    for param in route.parameters:
                        parameters.append({
                            "name": param.name,
                            "in": "path",  # Could extend to support query/header params
                            "required": param.required,
                            "schema": param.schema_type,
                            "description": param.description
                        })

                for method in route.methods:
                    method = method.lower()
                    if full_path not in openapi_schema["paths"]:
                        openapi_schema["paths"][full_path] = {}

                    operation = {
                        "tags": route.tags or [version],
                        "summary": route.summary,
                        "description": route.description,
                        "parameters": parameters,
                        "deprecated": route.deprecated,
                        "responses": {
                            resp.status_code: {
                                "description": resp.description,
                                "content": {
                                    "application/json": {
                                        "schema": resp.schema_
                                    }
                                }
                            } for resp in route.responses
                        }
                    }

                    # Add request body for appropriate methods
                    if method in ["post", "put", "patch"] and route.request:
                        operation["requestBody"] = {
                            "description": route.request.description,
                            "content": {
                                route.request.content_type: {
                                    "schema": route.request.schema_
                                }
                            },
                            "required": route.request.required
                        }

                    openapi_schema["paths"][full_path][method] = operation

        return openapi_schema

# Usage Example
if __name__ == "__main__":
    api_schema = VersionedAPISchema(title="My API", default_version="v1")

    # Add v1 routes
    user_route_v1 = APIRoute(
        path="/users/{user_id}",
        methods=["GET", "PUT"],
        summary="User operations",
        description="Manage user information",
        version="v1",
        tags=["Users"],
        responses=[
            RouteResponse(
                status_code="200",
                description="Successful response",
                schema_={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"}
                    }
                }
            )
        ],
        request=RouteRequest(
            schema_={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        )
    )

    # Add v2 routes
    user_route_v2 = APIRoute(
        path="/users/{user_id}",
        methods=["GET"],
        summary="User operations (v2)",
        description="Enhanced user management",
        version="v2",
        tags=["Users"],
        parameters=[
            RouteParameter(
                name="user_id",
                description="UUID of the user",
                schema_type={"type": "string", "format": "uuid"}
            )
        ],
        responses=[
            RouteResponse(
                status_code="200",
                description="Successful response",
                schema_={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "email": {"type": "string"}
                    }
                }
            )
        ]
    )

    api_schema.add_route(user_route_v1)
    api_schema.add_route(user_route_v2)

    # Generate OpenAPI schema
    schema = api_schema.build_openapi_schema()
    print(schema)