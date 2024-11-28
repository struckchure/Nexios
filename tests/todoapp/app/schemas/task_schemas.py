from nexio.validator import Schema,fields,FieldDescriptor
from models.tasks import TaskPriority
class CreateTaskSchema(Schema):

    name = FieldDescriptor(
        fields.StringField(max_length=130)
    )
    detail = FieldDescriptor(
        fields.StringField()
    )
    
    image = FieldDescriptor(
        fields.FileField(),required=False
    )
    
    priority = FieldDescriptor(
        fields.ChoiceField(choices=[priority.name for priority in TaskPriority]),
        required=False

    )

    async def validate_priority(self,value):
        return value.lower()
    


class UpdateTaskSchema(Schema):

    name = FieldDescriptor(
        fields.StringField(max_length=130),
        required=False
    )
    detail = FieldDescriptor(
        fields.StringField(),
        required=False

    )
    
    image = FieldDescriptor(
        fields.FileField(),required=False
    )
    
    priority = FieldDescriptor(
        fields.ChoiceField(choices=[priority.name for priority in TaskPriority]),
        required=False

    )

    async def validate_priority(self,value):
        return value.lower()