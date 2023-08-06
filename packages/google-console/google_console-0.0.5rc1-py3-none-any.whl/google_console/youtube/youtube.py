from .._pipeline import Base
from ._mixin import YouTubeMixin
from typing import List, Union


class YouTube(Base, YouTubeMixin):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = ""):
        super(YouTube, self).__init__("youtube", api_version, client_secret_file, scopes, prefix, suffix, token_dir)
