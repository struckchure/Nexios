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
                setattr(cls,key,value)
        return super().__new__(cls, name, bases, dct)
    
    

class BaseField:

    async def validate(self, value):
        pass


class Schema(metaclass = SchemaMeta):
    
    _errors = {}
    _data = {}
    _called = False
    def __getattr__(self, name):
        """Intercepts all method calls until __call__ is invoked."""
        if not self._called:
            raise AttributeError("You must call '__call__' before accessing any methods.")
        else:
            # Call the actual method or attribute once __call__ has been invoked
            return super().__getattr__(name)

    def validate(self, 
                 attrs :typing.Dict[str,any]
                 ) -> None:
        
        pass 


    
    def is_valid(self):
        
        if not hasattr(self,"errors"):
            return True
        return False
   
    
    async def __call__(self, *_data_dicts :typing.Dict) -> typing.Any:
        data  = {k: v for d in _data_dicts for k, v in d.items()}
        
            
        self.declared_fields :typing.Dict[str,typing.Type[FieldDescriptor]] = self.__class__._fields
        self.cheking = True
        
        for field_name, descriptor in self.declared_fields.items():
            try:
                await descriptor.validate(data.get(field_name))
            except ValidationError as e:
                setattr(self,"error",True)

           
            setattr(self,field_name,data.get(field_name)) #Expose field for external validation
        
        await self.validate()
        self._called = True
        return self
    
    #REVIEW: Review the code below
    
    def get_errors(self):
        self.declared_fields :typing.Dict[str,typing.Type[FieldDescriptor]] = self.__class__._fields
        errors = {}
        for key, val in self.declared_fields.items():
            errors[key] = val._errors

        return {**errors,**self._errors}

    @property
    def errors(self):
        errors = {}
        for key,value in self.get_errors().items():
            if isinstance(value, list) and len(value) > 0:
                errors.setdefault(key,value)

            if isinstance(value,str):
                errors.setdefault(key,value)

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



