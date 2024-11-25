#UNFINISHED:

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any
import mimetypes,os
from enum import Enum


class FileStorageBackend(ABC):
    """
    Abstract class for file storage backends.
    """

    @abstractmethod
    def save(self, file: BytesIO, file_name: str) -> str:
        """
        Save the file to the backend.
        Returns the URL or path to access the saved file.
        """
        pass

    @abstractmethod
    def validate_file(self, file: BytesIO) -> bool:
        """
        Validate the file (size, type, etc.).
        Returns True if valid, False otherwise.
        """
        pass


class LocalFileStorage(FileStorageBackend):
    def __init__(self, config:Enum):
        if hasattr(config,"media_root"):

            self.upload_dir = config.media_root
        else:
            self.upload_dir = "upload"
        os.makedirs(self.upload_dir, exist_ok=True)

    def validate_file(self, file: BytesIO) -> bool:

        
        return True

    def save(self, file: BytesIO, file_name: str) -> str:
        if not self.validate_file(file):
            raise ValueError("Invalid file type")

        file_path = os.path.join(self.upload_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(file.read())
        return file_path