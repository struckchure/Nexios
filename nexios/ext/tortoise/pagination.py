try:
    import tortoise
except ImportError:
    raise ImportError("Install Tortoise ORM to use Tortoise data handler for pagination.")

from typing import List, Optional, Type
from tortoise.models import Model
from tortoise.expressions import Q
from nexios.pagination import AsyncDataHandler



class AsyncTortoiseDataHandler(AsyncDataHandler):
    def __init__(self, model: Type[Model], query: Optional[Q] = None):
        """
        Initialize the handler with a Tortoise ORM model and an optional query.

        :param model: The Tortoise ORM model to paginate.
        :param query: An optional Tortoise ORM query (Q object) to filter the data.
        """
        self.model = model
        self.query = query

    async def get_total_items(self) -> int:
        """
        Get the total number of items in the database that match the query.

        :return: The total number of items.
        """
        query = self.model.all()
        if self.query:
            query = query.filter(self.query)
        return await query.count()

    async def get_items(self, offset: int, limit: int) -> List[Model]:
        """
        Get a paginated list of items from the database.

        :param offset: The starting index for the pagination.
        :param limit: The maximum number of items to return.
        :return: A list of Tortoise ORM model instances.
        """
        query = self.model.all().offset(offset).limit(limit)
        if self.query:
            query = query.filter(self.query)
        return await query