"""
This file defines the class WebConfig for managing config data around a web application.
"""
import os
import sys
from typing import Optional, Any

import yaml

from ybconfig.singleton import Singleton


class WebConfig(dict, metaclass=Singleton):
    """
    This class is responsible for managing the configuration data for a web application.
    """
    def __init__(self) -> None:
        """
        The constructor for the WebConfig class.
        """
        self._file_path: Optional[str] = None
        self._file_loaded: bool = False
        super().__init__()
        self.load()

    def get(self, key: str, file: bool = False, environ: bool = False, strict: bool = False) -> Optional[Any]:
        """
        Gets an element of data based on the key.

        :param key: (str) the key that the variable is stored under
        :param file: (bool) if set to True will force to get data from a yml file
        :param environ: (bool) if set to True will force to get data from the environment variables
        :param strict: (bool) if set to True will throw an error if the key is not present

        :return: (Optional[Any]) variable extracted from a config file or environment variable
        """
        if file is True and environ is True:
            raise KeyError("file and environ both cannot be True")
        if file is True:
            if self._file_loaded is False:
                self._load_from_file()
            return self._check_strict(value=super().get(key), strict=strict, key=key)

        if environ is True:
            return self._check_strict(value=os.environ.get(key), strict=strict, key=key)

        if self.from_file is True:
            return self._check_strict(value=super().get(key), strict=strict, key=key)
        return self._check_strict(value=os.environ.get(key), strict=strict, key=key)

    def load(self) -> None:
        """
        Loads data from a yml config file if 'ENVIRONMENT_CONFIG' is FALSE.

        :return: None
        """
        if self.from_file is True:
            self._load_from_file()

    def _load_from_file(self) -> None:
        """
        Loads the data from the yml file.

        :return: None
        """
        with open(self.file_path, "r") as file:
            self.update(yaml.safe_load(file))
            self._file_loaded = True

    @staticmethod
    def clean_memory() -> None:
        """
        Wipes the Singleton class from instances so another config can be made.

        :return: None
        """
        from ybconfig.singleton import Singleton
        Singleton._instances = {}

    @staticmethod
    def _check_strict(value: Optional[Any], strict: bool, key: str) -> Optional[Any]:
        """
        Checks to see if a variable getting retrieved should be raised if strict is True.

        :param value: (Optional[Any]) the value of the variable to be checked
        :param strict: (bool) if True an error is raised if value is None
        :param key: (str) the key of the variable being checked
        :return: (Optional[Any]) the variable value being checked
        """
        if value is None and strict is True:
            raise KeyError(f"{key} not found")
        return value

    @property
    def from_file(self) -> bool:
        if os.environ.get("ENVIRONMENT_CONFIG", "FALSE").upper() == "TRUE":
            return False
        return True

    @property
    def file_path(self) -> str:
        if self._file_path is None:
            self._file_path = sys.argv[-1]
        return self._file_path
