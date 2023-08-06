import sys
from ._base import BaseEstimator
from typing import List, Union


class Base(BaseEstimator):
    
    def __init__(self, api_name: str, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str,  suffix: str, token_dir: str):
        try:
            self.service = __MIXIN__  # type: ignore
        except NameError:
            super(Base, self).__init__(api_name, client_secret_file, api_version, scopes, prefix, suffix, token_dir)
            
            self._get_cred()
            if self.cred:
                self.service = self._build_service()
            else:
                self._create_service()
                self.service = self._build_service()
    
    def rebuild_service(self, pprint: bool = False):
        stdout = sys.stdout
        if not pprint:
            sys.stdout = None
        self.service = self._build_service()
        sys.stdout = stdout
    