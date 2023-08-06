from .._pipeline import Base
from typing import List, Union


# MESSAGES ATTACHMENT
class MessagesAttachment(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super(MessagesAttachment, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)

    def get(self):
        pass
