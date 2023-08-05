from .._pipeline import Base
from typing import List, Union


# SETTINGS
class Settings(Base):
    
    def __init__(self, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super(Settings, self).__init__("gmail", api_version, client_secret_file, scopes, prefix, suffix, token_dir)
    
    def getAutoForwarding(self):
        pass
    
    def getImap(self):
        pass
    
    def getLanguage(self):
        pass
    
    def getPop(self):
        pass
    
    def getVacation(self):
        pass
    
    def updateAutoForwarding(self):
        pass
    
    def updateImap(self):
        pass
    
    def updateLanguage(self):
        pass
    
    def updatePop(self):
        pass
    
    def updateVacation(self):
        pass
