from .._pipeline import Base
from typing import List, Union
import builtins

from ._users import Users
from ._drafts import Drafts
from ._history import History
from ._labels import Labels
from ._messages import Messages
from ._messages_attachment import MessagesAttachment
from ._settings import Settings
from ._settings_delegates import SettingsDelegates
from ._settings_filters import SettingsFilters
from ._settings_forwardingAddresses import SettingsForwardingAddresses
from ._settings_sendAs import SettingsSendAs
from ._settings_sendAs_smimeInfo import SettingsSendAsSmimeInfo
from ._threads import Threads


class MessagesMixin(Messages):
    
    def __init__(self, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super().__init__(api_version, client_secret_file, scopes, prefix, suffix, token_dir)

        args = (api_version, client_secret_file, scopes, prefix, suffix, token_dir)
        self.attachment = MessagesAttachment(*args)


class SettingsSendAsMixin(SettingsSendAs):
    
    def __init__(self, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super().__init__(api_version, client_secret_file, scopes, prefix, suffix, token_dir)
        
        args = (api_version, client_secret_file, scopes, prefix, suffix, token_dir)
        self.smimeInfo = SettingsSendAsSmimeInfo(*args)


class SettingsMixin(Settings):
    
    def __init__(self, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):
        super().__init__(api_version, client_secret_file, scopes, prefix, suffix, token_dir)

        args = (api_version, client_secret_file, scopes, prefix, suffix, token_dir)
        self.delegates = SettingsDelegates(*args)
        self.filters = SettingsFilters(*args)
        self.forwardingAddresses = SettingsForwardingAddresses(*args)
        self.sendAs = SettingsSendAsMixin(*args)
    

class GmailMixin(Base):
    
    def __init__(self, api_name: str, api_version: str, client_secret_file: str, scopes: Union[List[str], str], prefix: str,
                 suffix: str, token_dir: str):
        super().__init__(api_name, api_version, client_secret_file, scopes, prefix, suffix, token_dir)
        builtins.__MIXIN__ = self.service
        
        args = (api_version, client_secret_file, scopes, prefix, suffix, token_dir)
        self.users = Users(*args)
        self.drafts = Drafts(*args)
        self.history = History(*args)
        self.labels = Labels(*args)
        self.messages = MessagesMixin(*args)
        self.settings = SettingsMixin(*args)
        self.threads = Threads(*args)
        
        del builtins.__MIXIN__  # type: ignore
    