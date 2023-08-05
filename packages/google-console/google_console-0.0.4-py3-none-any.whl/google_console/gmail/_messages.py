from .._pipeline import Base
from ._base import PrivateMethods
from typing import List, Union
from pprint import pprint as _pprint


# MESSAGES
class Messages(Base, PrivateMethods):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        super(Messages, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)

    def batchDelete(self):
        pass
    
    def batchModify(self):
        pass
    
    def delete(self):
        pass
    
    def get(self):
        pass
    
    def import_(self):
        pass
    
    def insert(self):
        pass
    
    def list(self):
        pass
    
    def modify(self):
        pass
    
    def send(self, to: str, message: str, subject: str = None, file_attachment: Union[List[str], str] = None, cc: str = None,
             bcc: str = None, message_mode: str = "plain", user_id: str = "me", pprint: Union[bool, int] = False, **kwargs):
        raw_string = self._create_email(to, message, subject, file_attachment, cc, bcc, message_mode)
        response = self.service.users().messages().send(userId=user_id, body={"raw": raw_string}).execute()
        return response if not pprint else _pprint(response)
    
    def trash(self):
        pass
    
    def untrash(self):
        pass
    