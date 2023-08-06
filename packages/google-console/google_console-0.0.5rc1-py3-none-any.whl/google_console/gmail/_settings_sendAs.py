from .._pipeline import Base
from typing import List, Union


# SETTINGS SEND AS
class SettingsSendAs(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super(SettingsSendAs, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    def create(self):
        pass
    
    def delete(self):
        pass
    
    def get(self):
        pass
    
    def list(self):
        pass
    
    def patch(self):
        pass
    
    def update(self):
        pass
    
    def verify(self):
        pass
