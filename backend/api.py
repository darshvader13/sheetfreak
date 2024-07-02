from LLMAgent import LLMAgent
from TableAgent import TableAgent

from modal import App, Image, web_endpoint, Secret
from fastapi import File, UploadFile, FastAPI
from fastapi.responses import StreamingResponse

app = App("sheetfreak")

image = (
    Image.debian_slim()
    .pip_install("pandas")
    .pip_install("google-api-python-client")
    .pip_install("google-auth-httplib2")
    .pip_install("google-auth-oauthlib")
    .pip_install("openai")
    .pip_install("boto3")
)

@app.function(image=image)
@web_endpoint(method="GET")
def home():
    return "sheetfreak"

@app.function(image=image, secrets=[Secret.from_name("sheetfreak_GOOGLE_CREDS_CRICK"), Secret.from_name("sheetfreak_GOOGLE_DRIVE_FOLDER_ID")])
@web_endpoint(method="POST")
async def upload(file: UploadFile = File(...)):
    """Upload a file (.xlsx or .csv), convert to DataFrame, and save as Google Sheet"""
    try:
        import pandas as pd
        from io import BytesIO
        
        contents = await file.read()
        
        # Determine file type and read into DataFrame
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(contents))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        else:
            return "Error with unsupported file type. Please upload .xlsx or .csv files."

        # Get Google credentials
        GOOGLE_CREDENTIALS_JSON = json.loads(os.environ["GOOGLE_CREDS_CRICK"])
        creds = get_google_credentials(GOOGLE_CREDENTIALS_JSON)
        
        # Create a new Google Sheet
        from googleapiclient.discovery import build
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)

        DRIVE_FOLDER = "1LAEzfodH-7MUQcEZRJlifSXxkrSPhTUY"
        sheet_metadata = {
            'properties': {
                'title': file.filename + " w/ freakinthesheets"
            },
        }

        sheet = sheets_service.spreadsheets().create(body=sheet_metadata).execute()
        sheet_id = sheet['spreadsheetId']

        file = drive_service.files().update(
            fileId=sheet_id,
            addParents=DRIVE_FOLDER,
            fields='id, parents'
        ).execute()

        # Write DataFrame to Google Sheet
        values = [df.columns.tolist()] + df.values.tolist()

        request_body = {
            'values': values
        }

        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range='Sheet1',
            valueInputOption='RAW', body=request_body).execute()

        # Make file editable to anyone with the link
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }

        drive_service.permissions().create(fileId=sheet_id, body=permission).execute()
        file = drive_service.files().get(fileId=sheet_id, fields='webViewLink').execute()
        share_link = file.get('webViewLink')
        return share_link
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error details: {error_details}")
        return "Error processing file: " + str(e)


@app.function(image=image, secrets=[Secret.from_name("sheetfreak_GOOGLE_CREDS_CRICK")])
@web_endpoint(method="POST")
def ingest(req: dict):
    """Copy the user given Google Sheets into local Google Drive and return local sheets ID"""
    user_sheets_share_link: str = req["google_sheets_link"]

    if not user_sheets_share_link:
        return "No input provided"
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        GOOGLE_CREDENTIALS_JSON = json.loads(os.environ["sheetfreak_GOOGLE_CREDS_CRICK"])
        creds = get_google_credentials(GOOGLE_CREDENTIALS_JSON)
        
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build("sheets", "v4", credentials=creds)

        user_sheets_id = user_sheets_share_link.split('/')[5]
        print("Found user sheets id:", user_sheets_id)

        table_agent = TableAgent()
        user_sheets_title = table_agent.get_sheets_title(user_sheets_id)

        DRIVE_FOLDER = "1LAEzfodH-7MUQcEZRJlifSXxkrSPhTUY"
        request_body = {
            'name': user_sheets_title + ' w/ sheetfreak',
            'parents': [DRIVE_FOLDER]
        }

        copied_file = drive_service.files().copy(
            fileId=user_sheets_id,
            body=request_body
        ).execute()
        copied_file_id = copied_file.get("id")
        print("Copied file ID:", copied_file_id)

        #Make file editable to anyone with the link
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        drive_service.permissions().create(fileId=copied_file_id, body=permission).execute()
        file = drive_service.files().get(fileId=copied_file_id, fields='webViewLink').execute()
        share_link = file.get('webViewLink')
        return share_link
    except:
        return "Please provide a valid Google Sheets share link and select 'Anyone with the link can view'!"

@app.function(image=image, secrets=[Secret.from_name("sheetfreak_GOOGLE_CREDS_CRICK"), Secret.from_name("sheetfreak_OPENAI_PERSONAL_API_KEY"), Secret.from_name("sheetfreak_OPENAI_PERSONAL_ORG"), Secret.from_name("sheetfreak_AWS_ACCESS_KEY_ID"), Secret.from_name("sheetfreak_AWS_SECRET_ACCESS_KEY")])
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
    
    agent = LLMAgent()
    return StreamingResponse(
        agent.act_streamer(task_prompt, sheet_id, sheet_range), media_type="text/event-stream"
    )
    
    