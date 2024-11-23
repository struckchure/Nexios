from .base import BaseValidator 
from .exceptions import ValidationError
from typing import Dict
from .base import BaseField
import re,json,uuid
from datetime import date,time,datetime
from nexio.http.parsers import UploadedFile
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


    def __str__(self):
        return "<IntegerField Validator>"


class BooleanField(BaseField):
    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, bool):
            raise ValidationError("Invalid type expected type 'Boolean'")
        return value

    def __str__(self):
        return "Boolean Field Validator"
    


class URLField(BaseField):
    async def validate(self, value):
        if not value:
            return
        pattern = re.compile(
            r'^(http|https)://[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=.]+$'
        )
        if not pattern.match(value):
            raise ValidationError("Invalid URL format")
        return value

    

    def __str__(self):
        return "URL Field Validator"

class JSONField(BaseField):
    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, (str, dict)):
            raise ValidationError("Invalid type expected 'string' or 'dictionary'")
        if isinstance(value, str):
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON format")
        return value

    def __str__(self):
        return "JSON Field Validator"
    

class FileField(BaseField): 
    def __init__(self, allowed_extensions=None):
        #SUGGESTION: Add more validaion eg, file max_size etc .
        self.allowed_extensions = allowed_extensions or []

    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, UploadedFile): 
            
            raise ValidationError("Invalid file format")

        if self.allowed_extensions:
            extension = value.split('.')[-1].lower()
            if extension not in self.allowed_extensions:
                raise ValidationError(
                    f"File type not allowed. Allowed extensions: {', '.join(self.allowed_extensions)}"
                )
        return value

    def __str__(self):
        return "File Field Validator"

class ImageField(FileField):
    def __init__(self):
        super().__init__(allowed_extensions=["jpg", "jpeg", "png", "gif"])

    def __str__(self):
        return "Image Field Validator"
    
class ListField(BaseField): #REMEMBER :
    def __init__(self, child_field=None):
        self.child_field = child_field

    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, list):
            raise ValidationError("Invalid type expected type 'list'")
        if self.child_field:
            for item in value:
                await self.child_field.validate(item)
        return value

    def __str__(self):
        return "List Field Validator"
    

class EmailField(BaseField):
    async def validate(self, value):
        if not value:
            return
        
        pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if not pattern.match(value):
            raise ValidationError("Invalid email address format")
        return value

    

    def __str__(self):
        return "Email Field Validator"
    

class UUIDField(BaseField):
    async def validate(self, value):
        if not value:
            return
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValidationError("Invalid UUID format")
        return value

    def __str__(self):
        return "UUID Field Validator"
    

class FloatField(BaseField):
    async def validate(self, value):
        if not value:
            return
        self.check_type(value)
        return value

    def check_type(self, value):
        if not isinstance(value, (float, int)):
            raise ValidationError("Invalid type expected type 'Float' ")

    def __str__(self):
        return "Float Field Validator"



class DateField(BaseField):
    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, date):
            raise ValidationError("Invalid type expected type 'Date'")
        return value

    def __str__(self):
        return "Date Field Validator" 
    

class TimeField(BaseField):
    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, time):
            raise ValidationError("Invalid type expected type 'Time'")
        return value

    def __str__(self):
        return "Time Field Validator"
    

class DateTimeField(BaseField):
    async def validate(self, value):
        if not value:
            return
        if not isinstance(value, datetime):
            raise ValidationError("Invalid type expected type 'DateTime'")
        return value

    def __str__(self):
        return "DateTime Field Validator"
    
class ChoiceField(BaseField):
    def __init__(self, choices):
        if not isinstance(choices, (list, tuple)) or not choices:
            raise ValueError("Choices must be a non-empty list or tuple")
        self.choices = choices

    async def validate(self, value):
        if not value:
            return
        if value not in self.choices:
            raise ValidationError(f"Invalid value. Allowed choices are: {self.choices}")
        return value

    def __str__(self):
        return "Choice Field Validator"