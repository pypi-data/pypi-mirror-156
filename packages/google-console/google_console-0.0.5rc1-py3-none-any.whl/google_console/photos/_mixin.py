from .._pipeline import Base
from typing import List, Union
import builtins

from ._albums import Albums
from ._mediaItems import MediaItems
from ._sharedAlbums import SharedAlbums


class PhotosMixin(Base):
    
    def __init__(self, api_name: str, client_secret_file: str, api_version: str, scopes: Union[List[str], str],
                 prefix: str, suffix: str, token_dir: str):
        super().__init__(api_name, client_secret_file, api_version, scopes, prefix, suffix, token_dir)
        builtins.__MIXIN__ = self.service

        args = (client_secret_file, api_version, prefix, suffix, token_dir)
        self.albums = Albums(*args)
        self.mediaItems = MediaItems(*args)
        self.sharedAlbums = SharedAlbums(*args)

        del builtins.__MIXIN__  # type: ignore
        