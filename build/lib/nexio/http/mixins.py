#TODO : implment vlidated data dict 

import asgiref.sync
import warnings
import typing
import asgiref
class RequestValidatonMixin:
    validated = False
    _validation_schema = None
    _validation_errors = {}
    _validated_data = {}

    