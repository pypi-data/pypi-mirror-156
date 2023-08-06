import os
import requests


def upload_media(cls, file_path: str, file_name=None, resumable: bool = False):
    upload_url = f'https://photoslibrary.googleapis.com/{cls.API_VERSION}/uploads'
    headers = {'Authorization': 'Bearer ' + cls.cred.token,
               'Content-type': 'application/octet-stream',
               'X-Goog-Upload-Protocol': 'raw',
               'X-Goog-Upload-File-Name': os.path.basename(file_path) if file_name is None else file_name}
    
    with open(file_path, 'rb') as myfile:
        response = requests.put(upload_url, data=myfile, headers=headers)
    if response.status_code == 401:
        print("Upload Failed! retrying one more time.")
        cls.rebuild_service()
        with open(file_path, 'rb') as file:
            response = requests.put(upload_url, data=file, headers=headers)
    return response.content.decode('utf-8')
    