from .._pipeline import Base
from pprint import pprint as _pprint


# ALBUMS
class Albums(Base):
    
    def __init__(self, client_secret_file: str, api_version: str, prefix: str = "", suffix: str = "", token_dir: str = "", **kwargs):
        scopes = ["full.access", "appendonly", "sharing"]  # , "edit.appcreateddata"
        super(Albums, self).__init__("photos", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    # complete
    def addEnrichment(self, new_enrichment_item: dict, album_position: dict = {"position": "LAST_IN_ALBUM"},
                      album_id: str = None, album_name: str = None, pprint: bool = False):
        album_info = self.get(album_id, album_name)
        request_body = {"newEnrichmentItem": new_enrichment_item, "albumPosition": album_position}
        
        response = self.service.albums().addEnrichment(albumId=album_info["id"], body=request_body).execute()
        return response if not pprint else _pprint(response)
    
    # need to check
    def batchAddMediaItems(self, media_item_ids: list, album_id: str = None, album_name: str = None, pprint: bool = False):
        album_info = self.get(album_id, album_name)
        request_body = {"mediaItemIds": media_item_ids}
        response = self.service.albums().batchAddMediaItems(albumId=album_info["id"], body=request_body).execute()
        return response if not pprint else _pprint(response)
    
    # need to check
    def batchRemoveMediaItems(self, media_item_ids: list, album_id: str = None, album_name: str = None, pprint: bool = False):
        album_info = self.get(album_id, album_name)
        request_body = {"mediaItemIds": media_item_ids}
        response = self.service.albums().batchRemoveMediaItems(albumId=album_info["id"], body=request_body).execute()
        return response if not pprint else _pprint(response)
    
    # complete
    def create(self, album_name: str, duplicate: bool = False, pprint: bool = False, **kwargs):
        if not duplicate:
            print("This process can take a little while!")
            albums = [x["title"] for x in self.list() if x["title"] == album_name]
            if albums:
                raise NameError(f"Album name '{album_name}' already existed!")
        
        request_body = {"album": {"title": album_name, **kwargs}}
        response = self.service.albums().create(body=request_body).execute()
        return response if not pprint else _pprint(response)
    
    # complete
    def get(self, album_id: str = None, album_name: str = None, pprint: bool = False):
        if album_id:
            response = self.service.albums().get(albumId=album_id).execute()
        elif album_name:
            print("This process can take a little while!")
            _albums = self.list()
            
            albums = {k: [f"Media Items: {x.get('mediaItemsCount', 0)}",
                                          x.get("title")] for k, x in enumerate(_albums) if x["title"] == album_name}
            if len(albums) == 1:
                response = _albums[next(iter(albums))]
            elif len(albums) > 1:
                input_key = int(input(f"There are two or more albums exist. "
                                      f"Choose one of them {list(enumerate(albums.values()))}: "))
                response = _albums[input_key]
            else:
                raise ValueError("Album does not exist!")
        else:
            raise ValueError("Required one of variable (album_id or album_name)")
        
        return response if not pprint else _pprint(response)
    
    # complete
    def list(self, page_size: int = 50, exclude_non_app_created_data: bool = False, pprint: bool = False):
        response = self.service.albums().list(pageSize=page_size,
                                              excludeNonAppCreatedData=exclude_non_app_created_data).execute()
        
        albums = response.get("albums")
        next_page_token = response.get("nextPageToken")
        
        while next_page_token:
            response = self.service.albums().list(pageSize=page_size,
                                                  excludeNonAppCreatedData=exclude_non_app_created_data,
                                                  pageToken=next_page_token).execute()
            
            if response.get("albums"):
                albums.extend(response.get("albums"))
            next_page_token = response.get("nextPageToken")
        
        return albums if not pprint else _pprint(albums)
    
    # need to check
    def patch(self, album_id: str = None, album_name: str = None, pprint: bool = False, **kwargs):  # TODO: FIX
        album_info = self.get(album_id, album_name)
        response = self.service.albums().patch(id=album_info["id"], body={**kwargs}).execute()
        return response if not pprint else _pprint(response)
    
    # complete
    def share(self, album_id: str = None, album_name: str = None,
              is_collaborative: bool = False, is_commentable: bool = False, pprint: bool = False):
        album_info = self.get(album_id, album_name)
        request_body = {"sharedAlbumOptions": {"isCollaborative": is_collaborative,
                                               "isCommentable": is_commentable}}
        response = self.service.albums().share(albumId=album_info["id"], body=request_body).execute()
        return response if not pprint else _pprint(response)
    
    # complete
    def unshare(self, album_id: str = None, album_name: str = None):
        album_info = self.get(album_id, album_name)
        self.service.albums().unshare(albumId=album_info["id"]).execute()
    