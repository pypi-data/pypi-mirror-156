from ._mixin import PhotosMixin


class Photos(PhotosMixin):
    
    def __init__(self, client_secret_file: str, api_version: str, prefix: str = "", suffix: str = "", token_dir: str = ""):
        scopes = ["full.access", "readonly", "appendonly", "readonly.appcreateddata", "edit.appcreateddata", "sharing"]
        super(Photos, self).__init__("photos", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    # ALBUMS
    def albums_addEnrichment(self, new_enrichment_item: dict, album_position: dict = {"position": "LAST_IN_ALBUM"},
                             album_id: str = None, album_name: str = None, pprint: bool = False):
        return self.albums.addEnrichment(new_enrichment_item, album_position, album_id, album_name, pprint)
    
    def albums_batchAddMediaItems(self):
        ...
    
    def albums_batchRemoveMediaItems(self):
        ...
    
    def albums_create(self, album_name: str, duplicate: bool = False, pprint: bool = False, **kwargs):
        return self.albums.create(album_name, duplicate, pprint, **kwargs)
    
    def albums_get(self, album_id: str = None, album_name: str = None, pprint: bool = False):
        return self.albums.get(album_id, album_name, pprint)
    
    def albums_list(self, page_size: int = 50, exclude_non_app_created_data: bool = False, pprint: bool = False):
        return self.albums.list(page_size, exclude_non_app_created_data, pprint)
    
    def albums_patch(self):
        ...
    
    def albums_share(self, album_id: str = None, album_name: str = None,
                     is_collaborative: bool = False, is_commentable: bool = False, pprint: bool = False):
        return self.albums.share(album_id, album_name, is_collaborative, is_commentable, pprint)
    
    def albums_unshare(self, album_id: str = None, album_name: str = None):
        self.albums.unshare(album_id, album_name)

    # MEDIA ITEMS
    def mediaItems_batchCreate(self, new_media_items: list, album_position: dict = None,
                               album_id: str = None, album_name: str = None, pprint: bool = False):
        ...
    
    def mediaItems_batchGet(self):
        ...
    
    def mediaItems_get(self, media_item_id: str = None, media_item_name: str = None, pprint: bool = False):
        return self.mediaItems.get(media_item_id, media_item_name, pprint)
    
    def mediaItems_list(self, page_size: int = 100, pprint: bool = False):
        return self.mediaItems.list(page_size, pprint)
    
    def mediaItems_patch(self):
        ...
    
    def mediaItems_search(self):
        ...
    
    # SHARED ALBUMS
    def sharedAlbums_get(self, share_token: str = None, share_album_name: str = None, pprint: bool = False):
        return self.sharedAlbums.get(share_token, share_album_name, pprint)
    
    def sharedAlbums_join(self, share_token: str = None, share_album_name: str = None, pprint: bool = False):
        return self.sharedAlbums.join(share_token, share_album_name, pprint)
    
    def sharedAlbums_leave(self, share_token: str = None):
        self.sharedAlbums.leave(share_token)
    
    def sharedAlbums_list(self, page_size: int = 50, exclude_non_app_created_data: bool = False, pprint: bool = False):
        return self.sharedAlbums.list(page_size, exclude_non_app_created_data, pprint)
    