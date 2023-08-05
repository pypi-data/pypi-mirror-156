import os
import pickle
import datetime
from typing import List, Union
from collections import namedtuple
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from .scopes import scopes as _scopes


class BaseEstimator:
    
    def __init__(self, api_name: str, client_secret_file: str, api_version: str, scopes: Union[List[str], str], prefix: str, suffix: str, token_dir: str):

        self.API_NAME = api_name
        self.API_VERSION = api_version
        self.CLIENT_SECRET_FILE = client_secret_file
        self.SCOPES = _scopes(scopes, self.API_NAME)
        self.prefix = prefix
        self.suffix = suffix
        self.token_dir = token_dir
    
        self.working_dir = os.getcwd()
        self.pickle_file = f"{self.prefix}token_{self.API_NAME}_{self.API_VERSION}{self.suffix}.pickle"
    
    def _get_cred(self):
        if os.path.exists(os.path.join(self.working_dir, self.token_dir, self.pickle_file)):
            with open(os.path.join(self.working_dir, self.token_dir, self.pickle_file), "rb") as token:
                self.cred = pickle.load(token)
        else:
            self.cred = None
    
    def _build_service(self):
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
        
        try:
            service = build(self.API_NAME, self.API_VERSION, credentials=self.cred)
            print(self.API_NAME, self.API_VERSION, "service created successfully")
            return service
        except Exception as e:
            print(e)
            print(f"Failed to create service instance for {self.API_NAME}")
            os.remove(os.path.join(self.working_dir, self.token_dir, self.pickle_file))
            return None

    def _create_service(self):
        if not self.cred or not self.cred.valid:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(self.working_dir, self.token_dir,
                                                                          self.CLIENT_SECRET_FILE), self.SCOPES)
            self.cred = flow.run_local_server()

            if not os.path.exists(os.path.join(self.working_dir, self.token_dir)):
                os.mkdir(os.path.join(self.working_dir, self.token_dir))
        
            with open(os.path.join(self.working_dir, self.token_dir, self.pickle_file), "wb") as token:
                pickle.dump(self.cred, token)


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt


class GoogleSheetsHelper:
    # --> spreadsheets().batchUpdate()
    Paste_Type = namedtuple('_Paste_Type',
                            ('normal', 'value', 'format', 'without_borders',
                             'formula', 'date_validation', 'conditional_formatting')
                            )('PASTE_NORMAL', 'PASTE_VALUES', 'PASTE_FORMAT', 'PASTE_NO_BORDERS',
                              'PASTE_FORMULA', 'PASTE_DATA_VALIDATION', 'PASTE_CONDITIONAL_FORMATTING')
    
    Paste_Orientation = namedtuple('_Paste_Orientation', ('normal', 'transpose'))('NORMAL', 'TRANSPOSE')
    
    Merge_Type = namedtuple('_Merge_Type', ('merge_all', 'merge_columns', 'merge_rows')
                            )('MERGE_ALL', 'MERGE_COLUMNS', 'MERGE_ROWS')
    
    Delimiter_Type = namedtuple('_Delimiter_Type', ('comma', 'semicolon', 'period', 'space', 'custom', 'auto_detect')
                                )('COMMA', 'SEMICOLON', 'PERIOD', 'SPACE', 'CUSTOM', 'AUTODETECT')
    
    # --> Types
    Dimension = namedtuple('_Dimension', ('rows', 'columns'))('ROWS', 'COLUMNS')
    
    Value_Input_Option = namedtuple('_Value_Input_Option', ('raw', 'user_entered'))('RAW', 'USER_ENTERED')
    
    Value_Render_Option = namedtuple('_Value_Render_Option', ["formatted", "unformatted", "formula"]
                                     )("FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA")
    
    @staticmethod
    def define_cell_range(sheet_id, start_row_number=1, end_row_number=0,
                          start_column_number=None, end_column_number=0):
        """GridRange object"""
        json_body = {'sheetId': sheet_id,
                     'startRowIndex': start_row_number - 1,
                     'endRowIndex': end_row_number,
                     'startColumnIndex': start_column_number - 1,
                     'endColumnIndex': end_column_number}
        return json_body
    
    @staticmethod
    def define_dimension_range(sheet_id, dimension, start_index, end_index):
        json_body = {'sheetId': sheet_id,
                     'dimension': dimension,
                     'startIndex': start_index,
                     'endIndex': end_index}
        return json_body


class GoogleCalendarHelper:
    ...


class GoogleDriverHelper:
    ...


if __name__ == '__main__':
    g = GoogleSheetsHelper()
    print(g.Delimiter_Type)
    