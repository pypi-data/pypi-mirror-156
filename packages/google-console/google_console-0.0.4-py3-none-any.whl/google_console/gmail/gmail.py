from ._mixin import GmailMixin
from typing import List, Union


class Gmail(GmailMixin):
    
    def __init__(self, client_secret_file: str, api_version: str, prefix: str = "", suffix: str = "", token_dir: str = ""):
        scopes = ["full.access", "labels", "send", "readonly", "compose", "insert", "modify", "metadata", "settings.basic", "settings.sharing"]
        super(Gmail, self).__init__("gmail", client_secret_file, api_version, scopes, prefix, suffix, token_dir)
    
    # USERS
    def users_getProfile(self, user_id: str = "me", pprint: Union[bool, int] = False):
        self.users.getProfile(user_id, pprint)
    
    def users_stop(self):
        self.users.stop()
    
    def users_watch(self):
        self.users.watch()
    
    # DRAFTS
    def drafts_create(self, to: str, message: str, subject: str = None, file_attachment: Union[List[str], str] = None, cc: str = None,
                      bcc: str = None, message_mode: str = "plain", user_id: str = "me", pprint: Union[bool, int] = False, **kwargs):
        return self.drafts.create(to, message, subject, file_attachment, cc, bcc, message_mode, user_id, pprint, **kwargs)
    
    def drafts_delete(self):
        self.drafts.delete()
    
    def drafts_get(self):
        self.drafts.get()
    
    def drafts_list(self, includeSpamTrash: bool = False, user_id: str = "me", pprint: Union[bool, int] = False):
        self.drafts.list(includeSpamTrash, user_id, pprint)
    
    def drafts_send(self):
        self.drafts.send()
    
    def drafts_update(self):
        self.drafts.update()
    
    # HISTORY
    def history_list(self):
        self.history.list()
    
    # LABELS
    def labels_create(self, name: str, labelListVisibility: str = "labelShow", messageListVisibility: str = "show",
                      user_id: str = "me", **kwargs):
        self.labels.create(name, labelListVisibility, messageListVisibility, user_id, **kwargs)
    
    def labels_delete(self, user_id: str = "me", **kwargs):
        self.labels.delete(user_id, **kwargs)
    
    def labels_get(self, user_id: str = "me", pprint: Union[bool, int] = False, **kwargs):
        return self.labels.get(user_id, pprint, **kwargs)
    
    def labels_list(self, user_id: str = "me", pprint: Union[bool, int] = False):
        return self.labels.list(user_id, pprint)
    
    def labels_patch(self):
        self.labels.patch()
    
    def labels_update(self, label_id: str, user_id: str = "me", **kwargs):
        self.labels.update(label_id, user_id, **kwargs)
    
    def labels_info(self, pprint: Union[bool, int] = False, **kwargs):
        return self.labels.info(pprint, **kwargs)
    
    # MESSAGES
    def messages_batchDelete(self):
        self.messages.batchDelete()
    
    def messages_batchModify(self):
        self.messages.batchModify()
    
    def messages_delete(self):
        self.messages.delete()
    
    def messages_get(self):
        self.messages.get()
    
    def messages_import(self):
        self.messages.import_()
    
    def messages_insert(self):
        self.messages.insert()
    
    def messages_list(self):
        self.messages.list()
    
    def messages_modify(self):
        self.messages.modify()
    
    def messages_send(self, to: str, message: str, subject: str = None, file_attachment: Union[List[str], str] = None, cc: str = None,
                      bcc: str = None, message_mode: str = "plain", user_id: str = "me", pprint: Union[bool, int] = False, **kwargs):
        return self.messages.send(to, message, subject, file_attachment, cc, bcc, message_mode, user_id, pprint, **kwargs)
    
    def messages_trash(self):
        self.messages.trash()
    
    def messages_untrash(self):
        self.messages.untrash()
    
    # MESSAGES ATTACHMENT
    def messages_attachment_get(self):
        self.messages.attachment.get()

    # SETTINGS
    def settings_getAutoForwarding(self):
        self.settings.getAutoForwarding()
    
    def settings_getImap(self):
        self.settings.getImap()
    
    def settings_getLanguage(self):
        self.settings.getLanguage()
    
    def settings_getPop(self):
        self.settings.getPop()
    
    def settings_getVacation(self):
        self.settings.getVacation()
    
    def settings_updateAutoForwarding(self):
        self.settings.updateAutoForwarding()
    
    def settings_updateImap(self):
        self.settings.updateImap()
    
    def settings_updateLanguage(self):
        self.settings.updateLanguage()
    
    def settings_updatePop(self):
        self.settings.updatePop()
    
    def settings_updateVacation(self):
        self.settings.updateVacation()
    
    # SETTINGS DELEGATES
    def settings_delegates_create(self):
        self.settings.delegates.create()
    
    def settings_delegates_get(self):
        self.settings.delegates.get()
    
    def settings_delegates_list(self):
        self.settings.delegates.list()

    # SETTINGS FILTERS
    def settings_filters_create(self):
        self.settings.filters.create()

    def settings_filters_delete(self):
        self.settings.filters.delete()

    def settings_filters_get(self):
        self.settings.filters.get()

    def settings_filters_list(self):
        self.settings.filters.list()

    # SETTINGS FORWARDING ADDRESS
    def settings_forwardingAddresses_create(self):
        self.settings.forwardingAddresses.create()

    def settings_forwardingAddresses_delete(self):
        self.settings.forwardingAddresses.delete()

    def settings_forwardingAddresses_get(self):
        self.settings.forwardingAddresses.get()

    def settings_forwardingAddresses_list(self):
        self.settings.forwardingAddresses.list()

    # SETTINGS SEND AS
    def settings_sendAs_create(self):
        self.settings.sendAs.create()

    def settings_sendAs_delete(self):
        self.settings.sendAs.delete()

    def settings_sendAs_get(self):
        self.settings.sendAs.get()

    def settings_sendAs_list(self):
        self.settings.sendAs.list()

    def settings_sendAs_patch(self):
        self.settings.sendAs.patch()

    def settings_sendAs_update(self):
        self.settings.sendAs.update()

    def settings_sendAs_verify(self):
        self.settings.sendAs.verify()

    # SETTINGS SEND AS SMIME INFO
    def settings_sendAs_smimeInfo_delete(self):
        self.settings.sendAs.smimeInfo.delete()

    def settings_sendAs_smimeInfo_get(self):
        self.settings.sendAs.smimeInfo.get()

    def settings_sendAs_smimeInfo_insert(self):
        self.settings.sendAs.smimeInfo.insert()

    def settings_sendAs_smimeInfo_list(self):
        self.settings.sendAs.smimeInfo.list()

    def settings_sendAs_smimeInfo_setDefault(self):
        self.settings.sendAs.smimeInfo.setDefault()

    # THREADS
    def threads_delete(self):
        self.threads.delete()

    def threads_get(self):
        self.threads.get()

    def threads_list(self):
        self.threads.list()

    def threads_modify(self):
        self.threads.modify()

    def threads_trash(self):
        self.threads.trash()

    def threads_untrash(self):
        self.threads.untrash()
    