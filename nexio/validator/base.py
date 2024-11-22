from abc import ABC,abstractmethod
import typing
from .descriptor import FieldDescriptor
from .exceptions import ValidationError
class SchemaMeta(type):
    def __new__(cls, name, bases, dct):
        cls._fields = {}
        
        for key,value in dct.items():
            if isinstance(value, FieldDescriptor):

                cls._fields[key] = value
        return super().__new__(cls, name, bases, dct)


class BaseField:

    async def validate(self, value):
        pass


class Schema(metaclass = SchemaMeta):
    

    def validate(self, 
                 attrs :typing.Dict[str,any]
                 ) -> None:
        
        pass 


    
    def is_valid(self):
        
        if not hasattr(self,"_errors"):
            return True
        return False
   
    
    async def __call__(self, data :typing.Dict) -> typing.Any:
        
        self.declared_fields :typing.Dict[str,typing.Type[FieldDescriptor]] = self.__class__._fields
        self.cheking = True
        
        for field_name, descriptor in self.declared_fields.items():
            try:
                await descriptor.validate(data.get(field_name))
            except ValidationError as e:
                self.is_valid = False

           

        
        return self
    
    async def get_errors(self):
        self.declared_fields :typing.Dict[str,typing.Type[FieldDescriptor]] = self.__class__._fields
        errors = {}
        for key, val in self.declared_fields.items():
            errors[key] = val._errors

        return errors
            
        
    




class BaseValidator:

    """
    Base validation class which all other validators will inherit from
    """
    
    def __init__(self, **kwargs):
        pass 

    
    @abstractmethod
    async def validate(self, value):
        pass 

    @abstractmethod
    async def get_error_message(self):
        pass 



