from .._pipeline import Base
from typing import List, Union


# SETTINGS DELEGATES
class SettingsDelegates(Base):
    
    def __init__(self, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super(SettingsDelegates, self).__init__("gmail", api_version, client_secret_file, scopes, prefix, suffix, token_dir)
    
    def create(self):
        pass
    
    def get(self):
        pass
    
    def list(self):
        pass
