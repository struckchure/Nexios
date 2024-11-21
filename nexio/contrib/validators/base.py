import typing
class BaseShema(object):
    
    pass



class Field(object):

    def __init__(self, 
                 type: type,
                 min :int = None,
                 max :int = None,
                 default :typing.Any = None,
                 custom_validators :typing.List[typing.Callable] = [],
                 required = True,
                 *args , **kwargs


                  ) -> None:
        
       self.min = min
       self.max = max 
       self.default = default
       self.custom_validators = custom_validators
       self.type = type
       self.required = required
       self._validators = []




    def __repr__(self) -> str:
        return "<Nexio Validator Field >"
    

    def validate(self, 
                 func :typing.Callable,
                 error_message :str = None):
        assert callable(func), "Field validation function must be a callable"
        self._validators.append(func)

        return self
