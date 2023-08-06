from .._pipeline import Base
from typing import List, Union


# THREADS
class Threads(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super(Threads, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    def delete(self):
        pass
    
    def get(self):
        pass
    
    def list(self):
        pass
    
    def modify(self):
        pass
    
    def trash(self):
        pass
    
    def untrash(self):
        pass
