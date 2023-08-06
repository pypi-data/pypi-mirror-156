from .._pipeline import Base
from typing import List, Union
from pprint import pprint as _pprint


# USERS
class Users(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        super(Users, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    def getProfile(self, user_id: str = "me", pprint: Union[bool, int] = False):
        profile_info = self.service.users().getProfile(userId=user_id).execute()
        return profile_info if not pprint else _pprint(profile_info)
    
    def stop(self):
        pass
    
    def watch(self):
        pass
