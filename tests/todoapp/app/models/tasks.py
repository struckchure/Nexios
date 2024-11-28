from .base import BaseModel
from tortoise import fields
from .utils import FileField
from enum import Enum
# from nexio.utils.db.fields import FileField


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskModel(BaseModel):

    name = fields.CharField(max_length = 120)
    detail = fields.TextField()
    completed = fields.BooleanField(default = False)
    image = FileField(null = True)
    date_completed = fields.DatetimeField(null = True)
    priority = fields.CharEnumField(TaskPriority,default = TaskPriority.MEDIUM)




    class Meta:
        abstract = False
        table = "Tasks"