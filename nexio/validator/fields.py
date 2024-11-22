from .base import BaseValidator 
from .exceptions import ValidationError
from typing import Dict
from .base import BaseField
class StringField(BaseField):

    def __init__(self,max_length :int = None,
                      min_length :int = None) -> None:
        
        self.max_length = max_length
        self.min_length = min_length
        


    async def validate(self, value :str) -> str:
        self.check_type(value)
        self.validate_max(value)
        self.validate_min(value)

            
    def validate_max(self,value):
        if not value or not self.max_length:
            return 
        if len(value) > self.max_length:
            raise ValidationError(f"Value length must not be above {self.max_length}") 
        
    def validate_min(self,value):
        if not value or not self.min_length:
            return 
        if len(value) < self.max_length:
            raise ValidationError(f"Value length must not be below {self.min_length}") 
        
    def check_type(self, value):
        if not value :
            return 
        if not isinstance(value,str):
            raise ValidationError("Invalid type expected type 'string' ")
        

    def __str__(self) -> str:
        return "String Field Validator"


class IntegerField(BaseField):

    def __init__(self,
        max = None,
        min = None,
        max_digits = None) -> None:
        self.max = max
        self.min = min
        self.max_digits = max_digits
        super().__init__()

    async def validate(self, value):
        self.check_type(value)
        self.validate_max(value)
        self.validate_min(value)

    def check_type(self, value):

        if not value:
            return
        if not isinstance(self.cast_value(value), int):
            raise ValidationError("Invalid type expected type 'Integer' ")

    def cast_value(self, value):
        
        try:
            return int(value)

        except:
            return value
    
    def validate_max(self,value):
        if not value or not self.max:
            return

        if self.cast_value(value) > self.max:
            raise ValidationError(f"Value must not exceed {self.max}") 

    def validate_min(self,value):
        if not value or not self.min:
            return

        if self.cast_value(value) < self.min:
            raise ValidationError(f"Value must not be below {self.min}") 
        

    def valiate_max_digits(self, value):
        if not value or not self.max_digits:
            return
        
        if len(str(value)) > self.max_digits:
            raise ValidationError(f"Length of value digit must not exceed {self.max_digits}")
