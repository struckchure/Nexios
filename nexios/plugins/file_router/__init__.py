import importlib
import os
from typing import TypedDict

from nexios.application import NexiosApp
from nexios.logging import create_logger
from nexios.routing import Routes

logger = create_logger("nexios")


class FileRouterConfig(TypedDict):
    root: str


class FileRouterPlugin:
    """
    from nexios import get_application
    from nexios.plugins import FileRouterPlugin

    app = get_application()

    FileRouterPlugin(app, config={"root": "./routes"}).setup()
    """

    app: NexiosApp
    config: FileRouterConfig

    def __init__(self, app, config: FileRouterConfig = {"root": "./routes"}):
        self.app = app
        self.config = config

        self._setup()

    def _setup(self):
        for root, _, files in os.walk(self.config["root"]):
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.endswith("route.py"):
                    continue

                for route in self._build_route(file_path):
                    self.app.add_route(route)

    def _get_path(self, route_file_path: str) -> str:
        path = route_file_path.replace("route.py", "")
        segments = [
            "{%s}" % segment.replace("_", "") if segment.startswith("_") else segment
            for segment in path.split("/")
        ]

        return "/".join(segments)

    def _build_route(self, route_file_path: str) -> list[Routes]:
        handlers: list[Routes] = []
        path = self._get_path(route_file_path.replace(self.config["root"], ""))
        module = importlib.import_module(
            route_file_path.replace("/", ".").replace(".py", "")
        )

        get_handler = hasattr(module, "get")
        if get_handler:
            logger.debug("Mapped GET %s" % path)

            handlers.append(
                Routes(
                    path,
                    getattr(module, "get"),
                    methods=["GET"],
                )
            )

        post_handler = hasattr(module, "post")
        if post_handler:
            logger.debug("Mapped POST %s" % path)

            handlers.append(
                Routes(
                    path,
                    getattr(module, "post"),
                    methods=["POST"],
                )
            )

        patch_handler = hasattr(module, "patch")
        if patch_handler:
            logger.debug("Mapped PATCH %s" % path)

            handlers.append(
                Routes(
                    path,
                    getattr(module, "patch"),
                    methods=["PATCH"],
                )
            )

        put_handler = hasattr(module, "put")
        if put_handler:
            logger.debug("Mapped PUT %s" % path)

            handlers.append(
                Routes(
                    path,
                    getattr(module, "put"),
                    methods=["PUT"],
                )
            )

        delete_handler = hasattr(module, "delete")
        if delete_handler:
            logger.debug("Mapped DELETE %s" % path)

            handlers.append(
                Routes(
                    path,
                    getattr(module, "delete"),
                    methods=["DELETE"],
                )
            )

        return handlers
