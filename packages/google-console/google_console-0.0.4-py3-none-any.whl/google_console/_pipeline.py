from ._base import BaseEstimator
from typing import List, Union


class Base(BaseEstimator):
    
    def __init__(self, api_name: str, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str,  suffix: str, token_dir: str):
        try:
            self.service = __MIXIN__  # type: ignore
        except NameError:
            super(Base, self).__init__(api_name, api_version, client_secret_file, scopes, prefix, suffix, token_dir)
            
            self._get_cred()
            if self.cred:
                self.service = self._build_service()
            else:
                self._create_service()
                self.service = self._build_service()
    
    def rebuild_service(self):
        pass
    