import os
from typing import Optional, Union
from tortoise.fields.base import Field
from nexio.utils.files import UploadedFile
import mimetypes,asyncio,uuid
from io import BytesIO
from nexio.filestorage import LocalFileStorage



def get_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"

class FileField(Field):
    """
    Custom field for handling image uploads in Tortoise ORM.
    Supports direct Flask request.files uploads.
    """
    
    def __init__(
        self,
        upload_to: str = "uploads",
        null: bool = False,
        storage = LocalFileStorage,
        **kwargs
    ):
        super().__init__(null=null, **kwargs)
        self.upload_to = upload_to
        self.storage = storage()
        
        os.makedirs(upload_to, exist_ok=True)
    def to_db_value(
        self, 
        value: Union[UploadedFile, str, bytes, None], 
        instance
    ) -> Optional[str]:
    
        return value

    def to_python_value(
        self, 
        value: Optional[str]
    ) -> Optional[str]:

        if not value:
            return
        return value
    



