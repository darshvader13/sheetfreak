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

    def get_sheet_content(self, sheet_range):
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
    
    def push_sheet_content(self, sheet_range):
        """Writes sheet content back to online Google Sheets file"""
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
    
    def expand_table(self, newRows, newCols):
        """Expand the table to size newRows x newCols"""
        currRows = len(self.sheet_content)
        currCols = len(self.sheet_content.columns)
        if newCols < currCols and newRows < currRows:
            return
        
        print(f"Expanding table to {newRows+1} x {newCols+1}")
        if newCols >= currCols:
            for i in range(currCols, newCols+1):
                self.sheet_content[i] = [pd.NA for _ in range(currRows)]
            currCols = newCols+1
        if newRows >= currRows:
            for i in range(currRows, newRows + 1):
                self.sheet_content.loc[i] = [pd.NA for _ in range(currCols)]
        return

    def write_table(self, args):
        """Write the table at the given rows and columns to the given values"""
        rows = args[0]
        columns = args[1]
        values = args[2]
        
        maxRows = max(rows)
        maxCols = max(columns)
        self.expand_table(maxRows, maxCols)

        n = len(rows)
        for i in range(n):
            print(f"Setting {rows[i]}, {columns[i]} to {values[i]}")
            self.sheet_content.iloc[rows[i], columns[i]] = values[i]
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
    
    def create_chart(self, args):
        """Creates a chart"""
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

        print("Creating chart with", create_chart_request)
        create_chart_response = self.sheets_service.spreadsheets().batchUpdate(spreadsheetId=self.sheet_id, body=create_chart_request).execute()
        print("Finished operation", create_chart_response)
    
    def other_instruction(self, args):
        """Performs other instruction via spreadsheets.batchUpdate()"""
        other_instruction_response = self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.sheet_id, body=args[0]
            ).execute()
        print("Executed other instruction with", args)
    
    def execute_instruction(self, instruction_type, args):
        print(f"Attempting {instruction_type} with {args}")
        try:
            if instruction_type == "WRITE":
                self.write_table(args)
                return True, "", "Finished writing to table"
            elif instruction_type == "READ":
                vals = self.read_table(args)
                return True, "", vals
            elif instruction_type == "CHART":
                self.create_chart(args)
                return True, "", "Created chart"
            elif instruction_type == "QUESTION":
                return True, "", args
            elif instruction_type == "OTHER":
                self.other_instruction(args)
                return True, "", "Completed instruction"
            
        except Exception as e:
            print("Exception", e)
            return False, e, ""
