from .._pipeline import Base
from ._albums import Albums as _Albums
from pprint import pprint as _pprint
import builtins


# MEDIA ITEMS
class MediaItems(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        scopes = ["full.access", "appendonly", "sharing"]
        super(MediaItems, self).__init__("photos", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
        
        try:
            __MIXIN__  # type: ignore
            remove = False
        except:
            builtins.__MIXIN__ = self.service
            remove = True

        args = (client_secret_file, api_version, prefix, suffix, token_dir)
        self.__albums = _Albums(*args)
        
        if remove:
            del builtins.__MIXIN__  # type: ignore
    
    def batchCreate(self, new_media_items: list, album_position: dict = None,
                    album_id: str = None, album_name: str = None, pprint: bool = False):
        album_info = self.__albums.get(album_id, album_name)
        request_body = {"albumId": album_info["id"], "newMediaItems": new_media_items,
                        **({"albumPosition": album_position} if album_position else {})}
        
        response = self.service.mediaItems().batchCreate(body=request_body).execute()
        return response if not pprint else _pprint(response)
    
    def batchGet(self):
        pass

    # compleat  # TODO: MAY FACE PROBLEM
    def get(self, media_item_id: str = None, media_item_name: str = None, pprint: bool = False):
        if media_item_id:
            response = self.service.mediaItems().get(mediaItemId=media_item_id).execute()
        elif media_item_name:
            print("This process can take a little while!")
            _medias = self.list()
            
            medias = {k: [f"Media Info-> H: {x['mediaMetadata'].get('height')}, W: {x['mediaMetadata'].get('width')}",
                                             x.get("filename")] for k, x in enumerate(_medias) if x["filename"] == media_item_name}
            if len(medias) == 1:
                response = _medias[next(iter(medias))]
            elif len(medias) > 1:
                input_key = int(input(f"There are two or more albums exist. "
                                      f"Choose one of them {list(enumerate(medias.values()))}: "))
                response = _medias[input_key]
            else:
                raise ValueError("Album does not exist!")
        else:
            raise ValueError("Required one of variable (album_id or album_name)")
            
        return response if not pprint else _pprint(response)
    
    # compleat
    def list(self, page_size: int = 100, pprint: bool = False):
        response = self.service.mediaItems().list(pageSize=page_size).execute()
        medias = response.get('mediaItems')
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = self.service.mediaItems().list(pageSize=page_size, pageToken=nextPageToken).execute()
    
            if response.get('mediaItems'):
                medias.extend(response.get('mediaItems'))
            nextPageToken = response.get('nextPageToken')

        return medias if not pprint else _pprint(medias)
    
    def patch(self):
        pass
    
    def search(self):
        pass
    