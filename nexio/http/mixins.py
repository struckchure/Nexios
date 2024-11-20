#TODO : implment vlidated data dict 

import asgiref.sync
from nexio.contrib.validators.base import BaseShema,Field
import warnings
import typing
import asgiref
class RequestValidatonMixin:
    validated = False
    _validation_schema = None
    _validation_errors = {}
    _validated_data = {}

    def check_validation(self):
        flag = True
        for _,value in self._validatation_errors.items():
            if len(value) > 0:
                flag = False

        return flag
    async def validate_request(self) -> bool:
        self.validated = True
        self._validatation_errors = {}
        if not self._validation_schema:
            return None 
        self.schema :BaseShema = self._validation_schema

        self.schema_dict :typing.Dict = {} #track the fields

        for key,value in self.schema.__dict__.items():
            if isinstance(value,Field):
                self.schema_dict[key] = value
                self._validatation_errors[key] = []

        self._request_data :typing.Dict = await self.data 
        self._request_files :typing.Dict = await self.files
        self.request_data = {**self._request_data, **self._request_files}


        

        for field_name, field_object in self.schema_dict.items():
            field_data :any = self.request_data.get(field_name)
            value = await self.validate_field(
                                    field_name=field_name,
                                    field_object  = field_object,
                                    field_data=field_data)
            
            for _validators in field_object._validators:
                try:
                    _validators(field_data)
                except Exception as e:
                    self._validation_errors[field_name] = []
                    self._validation_errors[field_name].append(str(e))
        return self.check_validation()
        
    async def validate_field(self,
                             
                            field_name :str,

                            field_object :Field,

                            field_data :any):
        
        
        #make base validation below
        value = self.validate_required(field_name=field_name, # reasign the variable'value' for chain validation
                               field_value=field_data,
                               field=field_object)
        self.validate_type(field_name=field_name,
                           
                           field_value=value,

                           type=field_object.type)
        
        self.validate_min(field_name=field_name,
                          
                          field_value=value,

                          field=field_object)
        
        self.validate_max(field_name=field_name,
                          
                          field_value=value,
                          
                          field=field_object)
        
        
        



       
    def _try_casting(self,field_type, field_value):
        if not field_value:
            return field_value
        try:
            return field_type(field_value)
        except :
            return field_value

    def validate_type(self,field_name,field_value, type):
        if not field_value:
            return 
        casted_data = self._try_casting(field_type=type,field_value = field_value)
        if not isinstance(casted_data , type):
            self._validatation_errors[field_name].append("Invalid type")
            return 
        return field_value


    def validate_required(self, field_name, field_value, field :Field):
        
        if field.required == False:
            return field_value
        

        if field.default != None:
            
            return field.default
        
        if field_value == None:
            self._validatation_errors[field_name].append(f"{field_name} is required .")
            return
        return field_value


    
    def validate_min(self, field_name, field_value, field :Field ): #TODO :few errors i need to handle here
        field_value = self._try_casting(field_type=field.type,field_value = field_value)
        
        if field.min == None:
            return field_value
        print(type(field_value))
        print("min not found",field_value == None)
        
        if not field_value:
            return field_value
        

        if not getattr(field_value,"__len__",None):
            #ensure field value is an iterable
            return field_value
        
        if not isinstance(field.min,int) and not isinstance(field.min,float):
            
            return field_value

        min_value = field.min
        if isinstance(field_value,int) or isinstance(field_value, float):
            if field_value < min_value:

                self._validatation_errors[field_name].append(
                    f"{field_name}  must not be smaller than {min_value}"
                    
                    )
                
            return 
        
        if len(field_value) < min_value:
            self._validatation_errors[field_name].append(
                    f"{field_name} length must not be smaller than {min_value}"
                    
                    )
            return 
        return field_value
    def validate_max(self, field_name, field_value, field :Field ): #TODO :few errors i need to handle here
        

        field_value = self._try_casting(field_type=field.type,field_value = field_value)

        # if not getattr(field_value,"__len__",None):
        #     print(f"{field_value} is None")
        #     return field_value
        
        if field.max == None:
            return field_value
        
        if not field_value:
            return field_value
        if not isinstance(field.max,int) or not isinstance(field.max,float):
            return 

        max_value = field.max
        
        print("max excedede")
        if isinstance(field_value,int) or isinstance(field_value, float):
            if field_value > max_value:

                self._validatation_errors[field_name].append(
                    f"{field_name}  must not be larger than {max_value}"
                    
                    )
                
            return 
        
        if len(field_value) < max_value:
            self._validatation_errors[field_name].append(
                    f"{field_name} length must not be larger than {max_value}"
                    
                    )
            return
        return field_value
                
                
        
        #TODO :Implement max validation
        #TODO :IMPLEMENT cusotm validation input


        
    @property
    def validation_errors(self):
        assert self.validated == True ,".validate_request must be called first"

        dict_ = {}
        for key,value in self._validatation_errors.items():
            if len(value) > 0:
                dict_[key] = value
        return dict_
    
    
    async def __get_validated_data(self):
        data = {}
        for field_name, field_value in self.schema_dict.items():

            data[field_name] = self.request_data.get(field_name,field_value.default)
        return data
    
    @property
    async def validated_data(self):
        assert self.validated == True ,".validate_request must be called first"
        assert len(self._validation_errors.items()) == 0, "Validation error , can not access validated data ."

        return await self.__get_validated_data()




    
    
    

    



        
        



            
        




