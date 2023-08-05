from .._pipeline import Base
from ._mixin import DriveMixin
from typing import List, Union


class Drive(Base, DriveMixin):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = ""):
        super(Drive, self).__init__("drive", api_version, client_secret_file, scopes, prefix, suffix, token_dir)
