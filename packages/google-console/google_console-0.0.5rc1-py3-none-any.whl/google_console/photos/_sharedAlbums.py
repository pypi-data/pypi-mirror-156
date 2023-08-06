from .._pipeline import Base
from pprint import pprint as _pprint


# SHARED ALBUMS
class SharedAlbums(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        scopes = ["full.access", "appendonly", "sharing"]
        super(SharedAlbums, self).__init__("photos", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    def get(self, share_token: str = None, share_album_name: str = None, pprint: bool = False):
        if share_token:
            response = self.service.sharedAlbums().get(shareToken=share_token).execute()
        elif share_album_name:
            print("This process can take a little while!")
            _albums = self.list()
            
            albums = {k: [f"Media Items: {x.get('mediaItemsCount', 0)}",
                                          x.get("title")] for k, x in enumerate(_albums) if x["title"] == share_album_name}
            if len(albums) == 1:
                response = _albums[next(iter(albums))]
            elif len(albums) > 1:
                input_key = int(input(f"There are two or more albums exist. "
                                      f"Choose one of them {list(enumerate(albums.values()))}: "))
                response = _albums[input_key]
            else:
                raise ValueError("Album does not exist!")
        else:
            raise ValueError("Required one of variable (share_token or share_album_name)")
        
        return response if not pprint else _pprint(response)
    
    def join(self, share_token: str = None, share_album_name: str = None, pprint: bool = False):
        album_info = self.get(share_token, share_album_name)
        response = self.service.sharedAlbums().join(body={"shareToken": album_info[""]["shareToken"]}).execute()
        return response if not pprint else _pprint(response)
    
    def leave(self, share_token: str = None):
        self.service.sharedAlbums().leave(body={"shareToken": share_token}).execute()
    
    def list(self, page_size: int = 50, exclude_non_app_created_data: bool = False, pprint: bool = False):
        response = self.service.sharedAlbums().list(pageSize=page_size,
                                                    excludeNonAppCreatedData=exclude_non_app_created_data).execute()
        albums = response.get("sharedAlbums")
        next_page_token = response.get("nextPageToken")
    
        while next_page_token:
            response = self.service.sharedAlbums().list(pageSize=page_size,
                                                        excludeNonAppCreatedData=exclude_non_app_created_data,
                                                        pageToken=next_page_token).execute()
        
            if response.get("sharedAlbums"):
                albums.extend(response.get("sharedAlbums"))
            next_page_token = response.get("nextPageToken")
    
        return albums if not pprint else _pprint(albums)
    