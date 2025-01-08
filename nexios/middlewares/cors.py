import re
from nexios.middlewares.base import BaseMiddleware
from nexios.http.response import NexioResponse
from nexios.http.request import Request
from nexios.config import get_config
from typing import Callable, Optional

ALL_METHODS = ("DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT")
BASIC_HEADERS = {"Accept", "Accept-Language", "Content-Language", "Content-Type"}
SAFELISTED_HEADERS = {"Accept", "Accept-Language", "Content-Language", "Content-Type"}

class CORSMiddleware(BaseMiddleware):
    def __init__(self):
        config = get_config().cors

        # Load configuration from the CORS object
        self.allow_origins = config.allow_origins or []
        self.blacklist_origins = config.blacklist_origins or []
        self.allow_methods = config.allow_methods or ALL_METHODS
        self.allow_headers = config.allow_headers or []
        self.blacklist_headers = config.blacklist_headers or []
        self.allow_credentials = config.allow_credentials if config.allow_credentials is not None else True
        self.allow_origin_regex = re.compile(config.allow_origin_regex) if config.allow_origin_regex else None
        self.expose_headers = config.expose_headers or []
        self.max_age = config.max_age or 600
        self.strict_origin_checking = config.strict_origin_checking or False
        self.dynamic_origin_validator: Optional[Callable[[str], bool]] = getattr(config, "dynamic_origin_validator", None)
        self.debug = config.debug or False
        self.custom_error_status = config.custom_error_status or 400
        self.custom_error_messages = getattr(config, "custom_error_messages", {}) or {}

        # Prepare headers
        self.simple_headers = {}
        if self.allow_credentials:
            self.simple_headers["Access-Control-Allow-Credentials"] = "true"
        if self.expose_headers:
            self.simple_headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        self.preflight_headers = {
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Max-Age": str(self.max_age),
        }
        if self.allow_credentials:
            self.preflight_headers["Access-Control-Allow-Credentials"] = "true"

    async def process_request(self, request: Request, response):
        origin = request.origin
        method = request.scope["method"]

        if not origin and self.strict_origin_checking:
            if self.debug:
                print("Request denied: Missing 'Origin' header.")
            return response.json(self.get_error_message("missing_origin"), status_code=self.custom_error_status)

        if method.lower() == "options" and "access-control-request-method" in request.headers:
            return await self.preflight_response(request, response)
        return None

    async def process_response(self, request: Request, response: NexioResponse):
        origin = request.origin

        if origin and self.is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin

            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

    def is_allowed_origin(self, origin: str) -> bool:
        if origin in self.blacklist_origins:
            if self.debug:
                print(f"Request denied: Origin '{origin}' is blacklisted.")
            return False

        if "*" in self.allow_origins:
            return True

        if self.allow_origin_regex and self.allow_origin_regex.fullmatch(origin):
            return True

        if self.dynamic_origin_validator and callable(self.dynamic_origin_validator):
            return self.dynamic_origin_validator(origin)

        return origin in self.allow_origins

    async def preflight_response(self, request: Request, response: NexioResponse) -> NexioResponse:
        origin = request.headers.get("origin")
        requested_method = request.headers.get("access-control-request-method")
        requested_headers = request.headers.get("access-control-request-headers")

        headers = self.preflight_headers.copy()

        # Check origin
        if not self.is_allowed_origin(origin):
            if self.debug:
                print(f"Preflight request denied: Origin '{origin}' is not allowed.")
            return response.json(self.get_error_message("disallowed_origin"), status_code=self.custom_error_status)

        headers["Access-Control-Allow-Origin"] = origin

        # Check method
        if requested_method not in self.allow_methods:
            if self.debug:
                print(f"Preflight request denied: Method '{requested_method}' is not allowed.")
            return response.json(self.get_error_message("disallowed_method"), status_code=self.custom_error_status)

        # Handle headers
        if requested_headers:
            requested_header_list = [h.strip().lower() for h in requested_headers.split(",")]
            if "*" in self.allow_headers:
                headers["Access-Control-Allow-Headers"] = "*"
            else:
                for header in requested_header_list:
                    if header not in self.allow_headers or header in self.blacklist_headers:
                        if self.debug:
                            print(f"Preflight request denied: Header '{header}' is not allowed.")
                        return response.json(self.get_error_message("disallowed_header"), status_code=self.custom_error_status)
                headers["Access-Control-Allow-Headers"] = requested_headers

        return response.json("OK", status_code=201, headers=headers)

    def get_error_message(self, error_type: str) -> str:
        return self.custom_error_messages.get(error_type, "CORS request denied.")
