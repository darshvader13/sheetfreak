import os
import pandas as pd
import numpy as np
import json
import traceback
from io import BytesIO

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload

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

        copied_sheet = self.drive_service.files().copy(
            fileId=user_sheets_id,
            body=request_body
        ).execute()
        copied_sheet_id = copied_sheet.get("id")
        self.sheet_id = copied_sheet_id
        print("Copied sheet ID:", copied_sheet_id)
        
        #Make file editable to anyone with the link
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        self.drive_service.permissions().create(fileId=copied_sheet_id, body=permission).execute()
        file = self.drive_service.files().get(fileId=copied_sheet_id, fields='webViewLink').execute()
        share_link = file.get('webViewLink')
        return share_link
    
    async def upload_user_sheets(self, file):
        """Uploads user .xlsx or .csv to a Google Sheets file"""
        if file.filename.endswith('.xlsx'):
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file.filename.endswith('.csv'):
            mime_type = 'text/csv'
        else:
            return "Error: unsupported file type. Please upload .xlsx or .csv file."
   
        file_content = await file.read()
        file_bytes = BytesIO(file_content)
        
        media = MediaIoBaseUpload(file_bytes, mimetype=mime_type, resumable=True)

        file_metadata = {
            'name': file.filename + " w sheetfreak",
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }

        sheet = self.drive_service.files().create(body=file_metadata, media_body=media).execute()
        sheet_id = sheet["id"]
        self.sheet_id = sheet_id

        #Make file editable to anyone with the link
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        self.drive_service.permissions().create(fileId=sheet_id, body=permission).execute()
        file = self.drive_service.files().get(fileId=sheet_id, fields='webViewLink').execute()
        share_link = file.get('webViewLink')
        return share_link

    def get_sheet_content(self, sheet_range):
        """Gets content of sheet ID"""
        read_sheet_result = (
            self.sheets_service.spreadsheets().values()
            .get(spreadsheetId=self.sheet_id, range=sheet_range, valueRenderOption="FORMULA")
            .execute()
        )
        sheet_content = read_sheet_result.get("values", [])
        sheet_content = pd.DataFrame(sheet_content)
        sheet_content = sheet_content.replace({np.NaN: None})
        self.sheet_content = sheet_content
        print("Read values:\n", sheet_content.to_string())
        return sheet_content.to_string()
    
    def get_sheet_content_current(self):
        """Gets sheet content without reading sheet"""
        return self.sheet_content.to_string()
    
    def push_sheet_content(self, sheet_range):
        """Writes sheet content back to online Google Sheets file"""
        try:
            write_sheet_body = {
                "values": self.sheet_content.values.tolist()
            }
            write_sheet_result = (
                self.sheets_service.spreadsheets().values()
                .update(
                    spreadsheetId=self.sheet_id,
                    range=sheet_range,
                    valueInputOption="USER_ENTERED",
                    body=write_sheet_body,
                )
                .execute()
            )
            print(write_sheet_result)
            return "Wrote to Google Sheets"
        except:
            return "Error writing to Google Sheets"
    
    def expand_table(self, newRows, newCols):
        """Expand the table to size newRows x newCols"""
        currRows = len(self.sheet_content)
        currCols = len(self.sheet_content.columns)
        if newCols < currCols and newRows < currRows:
            return
        
        print(f"Expanding table to {newRows+1} x {newCols+1}")
        if newCols >= currCols:
            for i in range(currCols, newCols+1):
                self.sheet_content[i] = [None for _ in range(currRows)]
            currCols = newCols+1
        if newRows >= currRows:
            for i in range(currRows, newRows + 1):
                self.sheet_content.loc[i] = [None for _ in range(currCols)]
        return

    def write_table(self, args):
        """Write the table at the given rows and columns to the given values"""
        for write_args in args:
            row = write_args[0]
            col = write_args[1]
            value = write_args[2]

            self.expand_table(row, col)

            print(f"Setting {row}, {col} to {value}")
            self.sheet_content.iloc[row, col] = value
        print("Final sheet:", self.sheet_content)

    def read_table(self, args):
        """Gets the table values at the specified rows and columns"""
        rows = args[0]
        columns = args[1]
        
        maxRows = max(rows)
        maxCols = max(columns)
        self.expand_table(maxRows, maxCols)
        
        returned_values = []
        n = len(rows)
        for i in range(n):
            returned_values.append(self.sheet_content.iloc[rows[i], columns[i]])
        print("Read in", returned_values)
        return returned_values
    
    def get_chart_req(self, args):
        """Creates chart request from GPT response"""
        format_arguments = lambda x: json.loads(x) if type(x)==str else x
        create_chart_request = {
            "requests": [
                {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": args[0],
                                
                                "basicChart": {
                                    "chartType": args[1],
                                    "legendPosition": args[2],
                                    "axis": format_arguments(args[3]),
                                    "domains": format_arguments(args[4]),
                                    "series": format_arguments(args[5]),
                                }
                            },
                            "position": format_arguments(args[6]),
                        }
                    }
                }
            ]
        }
        return create_chart_request
    
    def create_chart(self, req):
        """Creates a chart"""
        print("Creating chart with", req)
        create_chart_response = self.sheets_service.spreadsheets().batchUpdate(spreadsheetId=self.sheet_id, body=req).execute()
        print("Finished operation", create_chart_response)
    
    def other_instruction(self, args):
        """Performs other instruction via spreadsheets.batchUpdate()"""
        print("Executing other instruction with", args)
        other_instruction_response = self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.sheet_id, body=args[0]
            ).execute()
        print("Finished operation", other_instruction_response)
    
    def execute_instruction(self, instruction_type, args):
        print(f"Attempting {instruction_type} with {args}")
        try:
            if instruction_type == "WRITE":
                self.write_table(args)
                return True, "", "Finished writing to table"
            elif instruction_type == "READ":
                vals = self.read_table(args)
                return True, "", str(vals)
            elif instruction_type == "CHART-gpt":
                chart_req = self.get_chart_req(args[0])
                self.create_chart(chart_req)
                return True, "", "Created chart"
            elif instruction_type == "CHART-claude":
                chart_req = {"requests": [json.loads(args[0])]}
                self.create_chart(chart_req)
                return True, "", "Created chart"
            elif instruction_type == "QUESTION":
                return True, "", args[0]
            elif instruction_type == "OTHER":
                self.other_instruction(args[0])
                return True, "", "Completed instruction"
            else:
                print("Unrecognized instruction type")
                return False, "Unrecognized instruction type", ""
            
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error: {error_details}")
            print("Exception when attempting instruction:", e)
            return False, str(e), str(args)
