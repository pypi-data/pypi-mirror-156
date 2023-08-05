from .._pipeline import Base
from ._mixin import PhotosMixin
from typing import List, Union


class Photos(Base, PhotosMixin):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = ""):
        super(Photos, self).__init__("photos", api_version, client_secret_file, scopes, prefix, suffix, token_dir)
