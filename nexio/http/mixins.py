from nexio.contrib.validators.base import BaseShema,Field

import typing
class RequestValidatonMixin:
    validated = False
    validated_data = {}
    async def validate_request(self) -> bool:
        self.validated = True
        if not self._validation_schema:
            return None 
        self.schema :BaseShema = self._validation_schema

        self.schema_dict :typing.Dict = {} #track the fields

        for key,value in self.schema.__dict__.items():
            if isinstance(value,Field):
                self.schema_dict[key] = value

        self._request_data :typing.Dict = await self.data 
        self._request_files :typing.Dict = await self.files
        self.request_data = {**self._request_data, **self._request_files}


        

        for field_name, field_object in self.schema_dict.items():
            field_data :any = self.request_data.get(field_name)
            check = await self.validate_field(
                                    field_name=field_name,
                                    field_object  = field_object,
                                    field_data=field_data)

        if len(self._validation_errors.items()) > 0:
            return False 
        
        return True
    async def validate_field(self,
                             
                            field_name :str,

                            field_object :Field,

                            field_data :any):
        
        validation_errors = []
        # print(
        #     f"field is {field}",
        #     f"field data is {field_data}",
        #     f"field_type id {type(field_data)}"
        # )
        if not self.validate_type(field_value=field_data,type=field_object.type):
            validation_errors.append("Invalid type")
        if len(validation_errors) > 0:
            self._validation_errors[field_name] = validation_errors
        

    @property
    def validated_data(self):
        assert self.validated == True ,".validate_request must be called first"


    def validate_type(self, field_value, type):
        return isinstance(field_value , type)
        
        



            
        



