from typing import Coroutine, Iterable
from tortoise import  Model,transactions
from tortoise import fields
from nexios.utils import timezone
import uuid
class BaseModel(Model):
    id = fields.UUIDField(default = uuid.uuid4,primary_key = True)
    date_created = fields.DatetimeField()

    class Meta:
        abstract = True

    async def save(self,**kwargs):
        del kwargs['using_db']
        try:
            async with transactions.in_transaction() as conn:
                if id:
                    self.date_created = timezone.now()
            
                return await super().save(using_db=conn,**kwargs)
        except Exception as e:
            print(str(e))
            raise

