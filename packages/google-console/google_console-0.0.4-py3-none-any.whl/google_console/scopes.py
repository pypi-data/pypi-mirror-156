from typing import List, Union


def __get_scope(scope: str, api_name: str):
    
    base_url = {"gmail": {"url": "https://www.googleapis.com/auth/gmail",
                          "scopes": ["labels", "send", "readonly", "compose", "insert", "modify", "metadata",
                                     "settings.basic", "settings.sharing", "full.access"]},
                "photos": {"url": "https://www.googleapis.com/auth/photoslibrary",
                           "scopes": ["readonly", "appendonly", "readonly.appcreateddata", "edit.appcreateddata",
                                      "sharing", "full.access"]}}

    # match [scope, api_name]:
    #     case ["full.access", "gmail"]:
    #         return "https://mail.google.com/"
    #     case ["full.access", "photos"]:
    #         return base_url[api_name].get("url")
    #
    #     case [_, ("gmail" | "photos")]:
    #         if scope not in base_url[api_name].get("scopes"):
    #             raise TypeError(f"'{scope}' Method is not allowed! Please use instead of {base_url[api_name].get('scopes')}")
    #         return ".".join([base_url[api_name].get("url"), scope])
    
    if scope == "full.access":
        if api_name == "gmail":
            return "https://mail.google.com/"
        elif api_name == "photos":
            return base_url[api_name].get("url")
    elif api_name in ("gmail", "photos"):
        if scope not in base_url[api_name].get("scopes"):
            raise TypeError(f"'{scope}' Method is not allowed! Please use instead of {base_url[api_name].get('scopes')}")
        return ".".join([base_url[api_name].get("url"), scope])


def scopes(types: Union[List[str], str], api_name: str):
    if type(types) != list: types = [types]
    api_name = api_name.lower()
    
    return [__get_scope(x.lower(), api_name) for x in types]
