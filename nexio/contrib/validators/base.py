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
                 nullable = False,
                 *args , **kwargs


                  ) -> None:
        
       self.min = min
       self.max = max 
       self.default = default
       self.custom_validators = custom_validators
       self.type = type
       self.nullable = nullable




    def __repr__(self) -> str:
        return "<Nexio Validator Field >"