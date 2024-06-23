from modal import App, Image, web_endpoint, Secret

import json
import os

app = App("freakinthesheets")

image = (
    Image.debian_slim()
    .pip_install("openai")
    .pip_install("google-api-python-client")
    .pip_install("google-auth-httplib2")
    .pip_install("google-auth-oauthlib")
    .pip_install("pandas")
)

get_tasks_tool = {
    "type": "function",
    "function": {
        "name": "get_tasks",
        "description": "Returns a list of lower level tasks",
        "parameters": { 
            "type": "object",
            "properties": {
                "types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "One word task summary. Must be one of the following: READ, WRITE, GRAPH, QUESTION, or OTHER",
                },
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "One sentence low-level task description",
                }
            },
            "required": ["types", "tasks"],
        }
    }
}

get_tasks_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given new-line separated, potentially high-level instructions, 
    return the function call to break down the instructions into low level instructions.
    Each index of the returned lists should correspond, so both the arrays should have the same length."""
}

update_table_tool = {
    "type": "function",
    "function": {
        "name": "update_table",
        "description": "Set the value in the cell to be the given value",
        "parameters": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index rows of the values to update",
                },
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index columns of the values to update",
                },
                "values": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The values to update at the rows and columns",
                },
            },
            "required": ["rows", "columns", "values"],
        },
    },
}

update_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to update values inside cells,
    return the function call to complete the updates as if the table is a Google Sheets. 
    Each index of the returned lists should correspond to each instruction, so all the arrays should have the same length.
    If a Google Sheets formula can be used, use it instead of hard-coding values."""
}

get_table_tool = {
    "type": "function",
    "function": {
        "name": "get_table",
        "description": "Get the value of a given cell in the table",
        "parameters": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index rows of the values to get",
                },
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index columns of the values to get",
                },
            },
            "required": ["rows", "columns"],
        },
    },
}

get_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to get values inside cells,
    return the function call to complete the get calls as if the table is a Google Sheets. 
    Each index of the returned lists should correspond, so both the arrays should have the same length."""
}

@app.function(image=image)
@web_endpoint(method="GET")
def home():
    return "freakinthesheets"

@app.function(image=image, secrets=[Secret.from_name("GOOGLE_CREDENTIALS_CRICK")])
@web_endpoint(method="POST")
def ingest(req: dict):
    """Copy the user given Google Sheets into local Google Drive and return local sheets ID"""
    user_sheets_share_link: str = req["google_sheets_link"]

    if not user_sheets_share_link:
        return "No input provided"
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        GOOGLE_CREDENTIALS_JSON = json.loads(os.environ["GOOGLE_CREDENTIALS_CRICK"])
        creds = Credentials(GOOGLE_CREDENTIALS_JSON['token'],
            refresh_token=GOOGLE_CREDENTIALS_JSON['refresh_token'],
            token_uri=GOOGLE_CREDENTIALS_JSON['token_uri'],
            client_id=GOOGLE_CREDENTIALS_JSON['client_id'],
            client_secret=GOOGLE_CREDENTIALS_JSON['client_secret'],
            scopes=GOOGLE_CREDENTIALS_JSON['scopes']
        )
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build("sheets", "v4", credentials=creds)

        user_sheets_id = user_sheets_share_link.split('/')[5]
        print("Found user sheets id:", user_sheets_id)

        user_sheets = sheets_service.spreadsheets().get(spreadsheetId=user_sheets_id).execute()
        user_sheets_title = user_sheets.get('properties').get('title')
        print("Found user sheets title:", user_sheets_title)

        DRIVE_FOLDER = "1LAEzfodH-7MUQcEZRJlifSXxkrSPhTUY"
        request_body = {
            'name': user_sheets_title + ' w freakinthesheets',
            'parents': [DRIVE_FOLDER]
        }

        copied_file = drive_service.files().copy(
            fileId=user_sheets_id,
            body=request_body
        ).execute()
        copied_file_id = copied_file.get("id")
        print("Copied file ID:", copied_file_id)
        return copied_file_id
    except:
        return "Please provide a valid Google Sheets share link and select 'Anyone with the link can view'!"
    
def update_table(table, rows, columns, values):
    """Update the table"""
    import pandas as pd

    if len(rows) != len(columns) or len(columns) != len(values):
        print("Invalid update table arguments")
        return
    
    #First expand dataframe if necessary
    maxRows = max(rows)
    currRows = len(table)
    maxCols = max(columns)
    currCols = len(table.columns)
    if maxRows >= currRows:
        table.reindex(range(maxRows+1))
        currRows = maxRows
    if maxCols >= currCols:
        for i in range(currCols, maxCols+1):
            table[i] = [pd.NA for j in range(currRows)]
    n = len(rows)
    for i in range(n):
        print(f"Setting {rows[i]}, {columns[i]} to {values[i]}")
        table.iloc[rows[i], columns[i]] = values[i]
    print(table)
    return table

def get_table_values(table, rows, columns):
    if len(rows) != len(columns):
        print("Invalid update table arguments")
        return
    
    returned_values = []
    n = len(rows)
    for i in range(n):
        returned_values.append(table.iloc[rows[i], columns[i]])
    return table
    
@app.function(image=image, secrets=[Secret.from_name("GOOGLE_CREDENTIALS_CRICK"), Secret.from_name("freakinthesheets_OPENAI_API_KEY"), Secret.from_name("freakinthesheets_OPENAI_ORG")])
@web_endpoint(method="POST")
def act(req: dict):
    """Given the task prompt and sheet ID, execute the instructions"""
    task_prompt: str = req["task_prompt"]
    sheet_id: str = req["sheet_id"]
    sheet_range = "Sheet1"

    if not task_prompt:
        return "Please provide a task!"
    
    if not sheet_id:
        return "No sheet ID provided"
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        import pandas as pd
        from openai import OpenAI
        GOOGLE_CREDENTIALS_JSON = json.loads(os.environ["GOOGLE_CREDENTIALS_CRICK"])
        creds = Credentials(GOOGLE_CREDENTIALS_JSON['token'],
            refresh_token=GOOGLE_CREDENTIALS_JSON['refresh_token'],
            token_uri=GOOGLE_CREDENTIALS_JSON['token_uri'],
            client_id=GOOGLE_CREDENTIALS_JSON['client_id'],
            client_secret=GOOGLE_CREDENTIALS_JSON['client_secret'],
            scopes=GOOGLE_CREDENTIALS_JSON['scopes']
        )
        sheets_service = build("sheets", "v4", credentials=creds)
        sheets = sheets_service.spreadsheets()
        read_sheet_result = (
            sheets.values()
            .get(spreadsheetId=sheet_id, range=sheet_range)
            .execute()
        )
        sheet_content = read_sheet_result.get("values", [])
        sheet_content = pd.DataFrame(sheet_content)
        print("Read values:", sheet_content)
        
    except:
        print("Couldn't read values")
        return "Error"
    
    # Read sheet contents into pandas DataFrame
    # try:
    update_table_user_msg = {
        "role": "user",
        "content": "Table: " + sheet_content.to_string() + f"\nEnd Table. Instructions:\n{task_prompt}"
    }
    messages = [update_table_sys_msg, update_table_user_msg]
    tools = [update_table_tool]

    client = OpenAI(organization=os.environ["freakinthesheets_OPENAI_ORG"])

    update_table_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    update_table_tool_calls = update_table_response.choices[0].message.tool_calls
    if len(update_table_tool_calls) > 1:
        print("More than one tool call")
        print(update_table_tool_calls)
    update_table_args = update_table_tool_calls[0].function.arguments
    print("Update table function args:", update_table_args)
    args = json.loads(update_table_args)
    rows = args["rows"]
    columns = args["columns"]
    values = args["values"]
    sheet_content = update_table(sheet_content, rows, columns, values)
    print("Finished updating table")

    write_sheet_body = {
        "values": sheet_content.values.tolist()
    }
    write_sheet_result = (
        sheets.values()
        .update(
            spreadsheetId=sheet_id,
            range=sheet_range,
            valueInputOption="USER_ENTERED",
            body=write_sheet_body,
        )
        .execute()
    )
    print(write_sheet_result)

    return "Updated table!"
    # except:
    #     print("Error executing instruction")
    #     return "Error"

