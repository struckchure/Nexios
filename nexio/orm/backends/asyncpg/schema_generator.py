from typing import TYPE_CHECKING

from orm.backends.base_postgres.schema_generator import BasePostgresSchemaGenerator

if TYPE_CHECKING:  # pragma: nocoverage
    from .client import AsyncpgDBClient


class AsyncpgSchemaGenerator(BasePostgresSchemaGenerator):
    def __init__(self, client: "AsyncpgDBClient") -> None:
        super().__init__(client)
