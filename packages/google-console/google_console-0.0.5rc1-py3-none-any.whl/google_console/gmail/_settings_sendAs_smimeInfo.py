from .._pipeline import Base
from typing import List, Union


# SETTINGS SEND AS SMIME INFO
class SettingsSendAsSmimeInfo(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super(SettingsSendAsSmimeInfo, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    def delete(self):
        pass
    
    def get(self):
        pass
    
    def insert(self):
        pass
    
    def list(self):
        pass
    
    def setDefault(self):
        pass
