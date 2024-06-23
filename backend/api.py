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

get_instructions_tool = {
    "type": "function",
    "function": {
        "name": "get_instructions",
        "description": "Returns a list of lower level instructions consisting of read, write, question, or other instructions.",
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
                    "description": """One word instruction summary. Must be one of the following: READ, WRITE, QUESTION, or OTHER.
                    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet. Do not READ just for writes, or I will touch you.
                    WRITE involves changing and inserting cell values. WRITE also implictly reads and does not need to explicitly read values in. 
                    QUESTION involves only questions about Sheets that do not require READ or WRITE operations.
                    OTHER involves operations that do not fit into READ, WRITE, or QUESTION operations, such as creating tables or charts. """,
                    
                },
                "instructions": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "One sentence low-level instruction description",
                }
            },
            "required": ["types", "instructions"],
        }
    }
}

get_instructions_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given new-line separated, potentially high-level tasks, 
    return the function call to break down the tasks into lower level instructions and their corresponding instruction types.
    Each index of the returned lists correspond, so both the arrays will have the same length.
    The instruction types are READ, WRITE, QUESTION, and OTHER.
    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet. Do not READ just for writes, or I will touch you.
    WRITE involves changing and inserting cell values. WRITE also implictly reads. 
    QUESTION involves only questions about Sheets that do not require READ or WRITE operations.
    OTHER involves operations that do not fit into READ, WRITE, or QUESTION operations, such as creating tables or charts.
    """
}

#test_user_msg = {"role": "user", "content": "Create a third column that is the sum of the first and second column and change the color of the cells to blue"}

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

other_instruction_table_tool = {
    "type": "function",
    "function": {
        "name": "other_operation",
        "description": "Returns value based on the Google Spreadsheets batchUpdate API",
        "parameters": {
            "type": "object",
            "properties": {
                "body": {
                    "type": "string",
                    "description": "The stringified JSON body that will be used in the Google Spreadsheets batchUpdate API as an argument",
                },
            },
            "required": ["body"],
        },
    },
}

other_instruction_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions,
    return the function call to complete the requested operation as if the table is a Google Sheets. 
    Return only the stringified JSON value that will be used as the body argument in the Google Spreadsheets batchUpdate API.
    By default create charts in an overlayed position of the sheet that does not cover the cells with values. 
    """
}

#test_other_msg = {'role': 'user', 'content': 'Create a green line graph with column 1 on the X axis labeled Bettors and column 2 on the Y labeled Dollars Made'}

read_table_tool = {
    "type": "function",
    "function": {
        "name": "other_operation",
        "description": "Get the values of given cells in the table",
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

read_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to get values inside cells,
    return the function call to complete the get calls as if the table is a Google Sheets. 
    Each index of the returned lists should correspond, so both the arrays should have the same length."""
}



@app.function(image=image)
@web_endpoint(method="GET")
def home():
    return "freakinthesheets"

def get_google_credentials(google_creds):
    """Return Google Credentials"""
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    creds = Credentials(google_creds['token'],
                        refresh_token=google_creds['refresh_token'],
                        token_uri=google_creds['token_uri'],
                        client_id=google_creds['client_id'],
                        client_secret=google_creds['client_secret'],
                        scopes=google_creds['scopes']
                        )
    return creds

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
        creds = get_google_credentials(GOOGLE_CREDENTIALS_JSON)
        
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
    
def write_sheet(sheet_id, sheet_range, table):
    """Writes the sheet back to the online Google Sheets file"""
    write_sheet_body = {
        "values": table.values.tolist()
    }
    write_sheet_result = (
        table.values()
        .update(
            spreadsheetId=sheet_id,
            range=sheet_range,
            valueInputOption="USER_ENTERED",
            body=write_sheet_body,
        )
        .execute()
    )
    print(write_sheet_result)

def expand_table(table, newRows, newCols):
    """Expand the table to size newRows x newCols"""
    import pandas as pd

    print(f"Expanding table to {newRows+1} x {newCols+1}")
    currRows = len(table)
    currCols = len(table.columns)
    if newRows >= currRows:
        table.reindex(range(newRows+1))
        currRows = newRows
    if newCols >= currCols:
        for i in range(currCols, newCols+1):
            table[i] = [pd.NA for j in range(currRows)]
    return table

def update_table(table, rows, columns, values):
    """Update the table at the given rows and columns to the given values"""
    import pandas as pd

    if len(rows) != len(columns) or len(columns) != len(values):
        print("Invalid update table arguments")
        return
    
    #First expand dataframe if necessary
    maxRows = max(rows)
    maxCols = max(columns)
    table = expand_table(table, maxRows, maxCols)

    #Make updates
    n = len(rows)
    for i in range(n):
        print(f"Setting {rows[i]}, {columns[i]} to {values[i]}")
        table.iloc[rows[i], columns[i]] = values[i]
    print(table)
    return table

def get_table_values(table, rows, columns):
    import pandas as pd

    if len(rows) != len(columns):
        print("Invalid get table values arguments")
        return
    
    maxRows = max(rows)
    maxCols = max(columns)
    expand_table(table, maxRows, maxCols)
    
    returned_values = []
    n = len(rows)
    for i in range(n):
        returned_values.append(table.iloc[rows[i], columns[i]])
    print("Read in", returned_values)
    return returned_values

def read_instruction(table, instruction):
    """Performs a read instruction by reading from the table"""
    import os
    import pandas as pd
    from openai import OpenAI

    read_table_user_msg = {
        "role": "user",
        "content": "Table:\n" + table.to_string() + f"\nEnd Table.\nInstructions:\n{instruction}"
    }
    messages = [read_table_sys_msg, read_table_user_msg]

    client = OpenAI(organization=os.environ["freakinthestreets_OPENAI_ORG"])

    read_table_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[read_table_tool],
        tool_choice="auto",
    )

    read_table_tool_calls = read_table_response.choices[0].message.tool_calls
    read_values = []
    for i in range(len(read_table_tool_calls)):
        read_table_args = read_table_tool_calls[i].function.arguments
        print("Read table function args:", read_table_args)
        args = json.loads(read_table_args)
        rows = args["rows"]
        columns = args["columns"]
        read_values += get_table_values(table, rows, columns)
    print("Finished reading")
    return read_values

def write_instruction(table, instruction):
    """Performs a write instruction by updating the table"""    
    import os
    import pandas as pd
    from openai import OpenAI

    update_table_user_msg = {
        "role": "user",
        "content": "Table:\n" + table.to_string() + f"\nEnd Table.\nInstructions:\n{instruction}"
    }
    messages = [update_table_sys_msg, update_table_user_msg]

    client = OpenAI(organization=os.environ["freakinthesheets_OPENAI_ORG"])

    update_table_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[update_table_tool],
        tool_choice="auto",
    )

    update_table_tool_calls = update_table_response.choices[0].message.tool_calls
    for i in range(len(update_table_tool_calls)):
        update_table_args = update_table_tool_calls[i].function.arguments
        print("Update table function args:", update_table_args)
        args = json.loads(update_table_args)
        rows = args["rows"]
        columns = args["columns"]
        values = args["values"]
        table = update_table(table, rows, columns, values)
    print("Finished updating table")
    return table

def other_instruction(table, instruction):

    other_instruction_table_user_msg = {
        "role": "user",
        "content": "Table: " + table.to_string() + f"\nEnd Table. Instructions:\n{instruction}"
    }
    messages = [other_instruction_table_sys_msg, other_instruction_table_user_msg]
    tools = [other_instruction_table_tool]

    client = OpenAI(organization=os.environ["freakinthesheets_OPENAI_ORG"])

    other_instruction_table_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

def get_instructions(table, task):
    """Get a list of low-level instructions to complete the given task with the given table state."""
    import os
    import pandas as pd
    from openai import OpenAI

    get_instructions_user_msg = {
        "role": "user",
        "content": "Table:\n" + table.to_string() + f"\nEnd Table.\Tasks:\n{task}"
    }
    messages = [get_instructions_sys_msg, get_instructions_user_msg]

    client = OpenAI(organization=os.environ["freakinthesheets_OPENAI_ORG"])

    get_instructions_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[get_instructions_tool],
        tool_choice="auto",
    )

    get_instructions_tool_calls = get_instructions_response.choices[0].message.tool_calls
    instruction_types = []
    instruction_commands = []
    for i in range(len(get_instructions_tool_calls)):
        get_instructions_args = get_instructions_tool_calls[i].function.arguments
        print("Get instructions args:", get_instructions_args)
        args = json.loads(get_instructions_args)
        instruction_types += args["types"]
        instruction_commands += args["instructions"]
    if len(instruction_types) != len(instruction_commands):
        print("Invalid instructions!")
        return []
    instructions = []
    for i in range(len(instruction_types)):
        instructions.append((instruction_types[i], instruction_commands[i]))
    return instructions

def execute_instruction(table, instruction):
    """Executes the given instruction based on the state of the table and returns the updated table and read values if any"""
    instruction_type = instruction[0]
    instruction_command = instruction[1]
    if instruction_type == "READ":
        return table, read_instruction(instruction_command)
    elif instruction_type == "WRITE":
        return write_instruction(table, instruction_command), ""
    elif instruction_type == "OTHER":
        return other_instruction(table, instruction_command), ""
    else:
        print("Unrecognizable instruction!")
    return "Unrecognizable instruction"

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
        creds = get_google_credentials(GOOGLE_CREDENTIALS_JSON)

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
    
    instructions = get_instructions(sheet_content, task_prompt)
    print("Got instructions", instructions)

    user_reads = []
    for instruction in instructions:
        print("Executing", instruction)
        sheet_content, read_values = execute_instruction(sheet_content, instruction)
        if read_values:
            user_reads += read_values
    
    write_sheet(sheet_id, sheet_range, sheet_content)
    print("Wrote sheet to Google Sheets")
    return "Success"