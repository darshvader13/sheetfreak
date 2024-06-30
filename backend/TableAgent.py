import os
import pandas as pd
import json

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class TableAgent:
    """TableAgent is the agent responsible for manipulating the underlying table"""
    def __init__(self, sheet_id = -1):
        self.sheet_id = sheet_id
        self.sheet_content = None
        creds_json = json.loads(os.environ["GOOGLE_CREDS_CRICK"])
        creds = Credentials(creds_json['token'],
                        refresh_token=creds_json['refresh_token'],
                        token_uri=creds_json['token_uri'],
                        client_id=creds_json['client_id'],
                        client_secret=creds_json['client_secret'],
                        scopes=creds_json['scopes']
                        )        
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.sheets_service = build("sheets", "v4", credentials=creds)
    
    def get_sheets_title(self, user_sheets_id):
        """Returns the title of the user's sheets"""
        user_sheets = self.sheets_service.spreadsheets().get(spreadsheetId=user_sheets_id).execute()
        user_sheets_title = user_sheets.get('properties').get('title')
        print("Found user sheets title:", user_sheets_title)
        return user_sheets_title
    
    def copy_user_sheets(self, user_sheets_id, user_sheets_title):
        request_body = {
            'name': user_sheets_title + ' w sheetfreak',
            'parents': [os.environ["GOOGLE_DRIVE_FOLDER_ID"]]
        }

        copied_file = self.drive_service.files().copy(
            fileId=user_sheets_id,
            body=request_body
        ).execute()
        copied_file_id = copied_file.get("id")
        self.sheet_id = copied_file_id
        print("Copied file ID:", copied_file_id)
        
        #Make file editable to anyone with the link
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        self.drive_service.permissions().create(fileId=copied_file_id, body=permission).execute()
        file = self.drive_service.files().get(fileId=copied_file_id, fields='webViewLink').execute()
        share_link = file.get('webViewLink')
        return share_link

    def get_sheets_content(self, sheet_range):
        """Gets content of sheet ID"""
        read_sheet_result = (
            self.sheets_service.spreadsheets().values()
            .get(spreadsheetId=self.sheet_id, range=sheet_range)
            .execute()
        )
        sheet_content = read_sheet_result.get("values", [])
        sheet_content = pd.DataFrame(sheet_content)
        print("Read values:", sheet_content)
        self.sheet_content = sheet_content
        return sheet_content.to_string()