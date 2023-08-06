from .._pipeline import Base
from typing import List, Union
from pprint import pprint as _pprint


# LABELS
class Labels(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        super(Labels, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
        
        self.__labels = self.__get_labels("me")
    
    def create(self, name: str, labelListVisibility: str = "labelShow", messageListVisibility: str = "show",
               user_id: str = "me", **kwargs):
        response = self.service.users().labels().create(userId=user_id,
                                                        body={"labelListVisibility": labelListVisibility,
                                                              "messageListVisibility": messageListVisibility,
                                                              "name": name, **kwargs}).execute()
        self.__labels = self.__get_labels(user_id)
        _pprint(response)
    
    def delete(self, user_id: str = "me", **kwargs):
        label_id = self.info(**kwargs).get("id")
        self.service.users().labels().delete(userId=user_id, id=label_id).execute()
    
    def get(self, user_id: str = "me", pprint: Union[bool, int] = False, **kwargs):
        label_id = self.info(**kwargs).get("id")
        response = self.service.users().labels().get(userId=user_id, id=label_id).execute()
        return response if not pprint else _pprint(response)
    
    def list(self, user_id: str = "me", pprint: Union[bool, int] = False):
        self.__labels = self.__get_labels(user_id)
        return self.__labels if not pprint else _pprint(self.__labels)
    
    def patch(self):
        pass
    
    def update(self, label_id: str, user_id: str = "me", **kwargs):
        _pprint({"id": label_id, **kwargs})
        response = self.service.users().labels().update(userId=user_id, body={"id": label_id, **kwargs}).execute()
        _pprint(response)
    
    def info(self, pprint: Union[bool, int] = False, **kwargs):
        if kwargs.get("label_id"):
            if kwargs.get("label_id") in [x.get("id") for x in self.__labels["labels"]]:
                response, = [x for x in self.__labels["labels"] if kwargs.get("label_id") == x.get("id")]
            else:
                raise TypeError(f"label_id: {kwargs.get('label_id')} not exists")
        elif kwargs.get("label_name"):
            if kwargs.get("label_name") in [x.get("name") for x in self.__labels["labels"]]:
                response, = [x for x in self.__labels["labels"] if kwargs.get("label_name") == x.get("name")]
            else:
                raise TypeError(f"label_name: {kwargs.get('label_name')} not exists")
        else:
            raise TabError("'label_id' or 'label_name' required")
        
        return response if not pprint else _pprint(response)
    
    # PRIVATE FUNCTION
    def __get_labels(self, user_id: str):
        return self.service.users().labels().list(userId=user_id).execute()
