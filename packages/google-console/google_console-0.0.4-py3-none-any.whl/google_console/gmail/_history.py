from .._pipeline import Base
from typing import List, Union


# HISTORY
class History(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        super(History, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    def list(self):
        pass
