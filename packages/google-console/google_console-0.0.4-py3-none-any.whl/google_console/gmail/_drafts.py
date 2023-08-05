from .._pipeline import Base
from ._base import PrivateMethods
from typing import List, Union
from pprint import pprint as _pprint


# DRAFT
class Drafts(Base, PrivateMethods):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        super(Drafts, self).__init__("gmail", api_version, client_secret_file, scopes, prefix, suffix, token_dir)

    def create(self, to: str, message: str, subject: str = None, file_attachment: Union[List[str], str] = None, cc: str = None,
               bcc: str = None, message_mode: str = "plain", user_id: str = "me", pprint: Union[bool, int] = False):
        raw_string = self._create_email(to, message, subject, file_attachment, cc, bcc, message_mode)
        response = self.service.users().drafts().create(userId=user_id, body={"message": {"raw": raw_string}}).execute()
        return response if not pprint else _pprint(response)
    
    def delete(self):
        pass
    
    def get(self):
        pass
    
    def list(self, includeSpamTrash: bool = False, user_id: str = "me", pprint: Union[bool, int] = False):
        response = self.service.users().drafts().list(userId=user_id, includeSpamTrash=includeSpamTrash, maxResults=500).execute()
        listDrafts=response.get("drafts")
        nextPageToken=response.get("nextPageToken")
        
        while nextPageToken:
            response = self.service.users().drafts().list(userId=user_id, includeSpamTrash=includeSpamTrash, maxResults=500, pageToken=nextPageToken).execute()
            if response.get("drafts"): listDrafts.append(response.get("drafts"))
            _pprint(response)
            nextPageToken = response.get("nextPageToken")
        listDrafts.append({"resultSizeEstimate": len(listDrafts)})
        return listDrafts if not pprint else _pprint(listDrafts)
    
    def send(self, user_id: str = "me"):
        response = self.service.users().drafts().send(userId=user_id, body={'id': 'r-7060467840493860627'}).execute()
        _pprint(response)
    
    def update(self):
        pass
