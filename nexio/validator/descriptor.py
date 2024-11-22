import typing
from .exceptions import ValidationError
class FieldDescriptor:

    def __init__(
            self,
            field ,
            validators :typing.Dict[str,typing.Callable] = [],
            required :bool = True,
            default :typing.Any = None
                 ) -> None:
        
        self.field = field
        self.required = required
        self.default = default
        self.vaidators = validators
        
        
        print("field is ",field)



    async def validate(self,value):
        self._errors :typing.List = []
        if not self.required and not value:
            return
        try:

            await self.validate_required(value)
            
            await self.validate_type(value)
        except ValidationError as e:
            self._errors.append(str(e))

    async def validate_required(self, value):
        if self.required == True and not value and not self.default:
            self._errors.append("Required Field")

    async def validate_type(self,value):
        from .base import BaseField #to avoid circular imports
        
        print("fiel type is", self.field)
        if not isinstance(self.field,BaseField):
            return 
        
        print("fiel type is", self.field)

        #TODO :CHECK IF IT IS A VALID FIELD
        await self.field.validate(value)
