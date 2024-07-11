from LLMAgent import LLMAgent
from TableAgent import TableAgent

from modal import App, Image, web_endpoint, Secret
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
import traceback

app = App("sheetfreak")

image = (
    Image.debian_slim()
    .pip_install("pandas")
    .pip_install("numpy")
    .pip_install("openpyxl")
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
        table_agent = TableAgent()
        return await table_agent.upload_user_sheets(file)
    except:
        error_details = traceback.format_exc()
        print(f"Error: {error_details}")
        return "Error processing file"


@app.function(image=image, secrets=[Secret.from_name("sheetfreak_GOOGLE_CREDS_CRICK"), Secret.from_name("sheetfreak_GOOGLE_DRIVE_FOLDER_ID")])
@web_endpoint(method="POST")
def ingest(req: dict):
    """Copy the user given Google Sheets into local Google Drive and return local sheets ID"""
    user_sheets_share_link: str = req["google_sheets_link"]

    if not user_sheets_share_link:
        return "No input provided"
    
    try:
        user_sheets_id = user_sheets_share_link.split('/')[5]
        print("Found user sheets id:", user_sheets_id)

        table_agent = TableAgent()
        user_sheets_title = table_agent.get_sheets_title(user_sheets_id)

        share_link = table_agent.copy_user_sheets(user_sheets_id, user_sheets_title)
        return share_link
    except:
        error_details = traceback.format_exc()
        print(f"Error: {error_details}")
        return "Please provide a valid Google Sheets share link and select 'Anyone with the link can view'!"

@app.function(image=image, secrets=[Secret.from_name("sheetfreak_GOOGLE_CREDS_CRICK"), Secret.from_name("sheetfreak_OPENAI_PERSONAL_API_KEY"), Secret.from_name("sheetfreak_OPENAI_PERSONAL_ORG"), Secret.from_name("sheetfreak_AWS_ACCESS_KEY_ID"), Secret.from_name("sheetfreak_AWS_SECRET_ACCESS_KEY")])
@web_endpoint(method="POST")
def act(req: dict):
    """Given the task prompt and sheet ID, execute the instructions"""
    task_prompt: str = req["task_prompt"]
    sheet_id: str = req["sheet_id"]
    sheet_range = "Sheet1" #may change due to file upload and user input
    messages: list = req["messages"]

    if not task_prompt:
        return "Please provide a task!"
    
    if not sheet_id:
        return "No sheet ID provided"
    
    agent = LLMAgent(default_call="claude", tools_to_models={"write_table": "gpt-4o"})

    # TODO: Keep conversation history
    return StreamingResponse(
        agent.act_streamer(task_prompt, sheet_id, sheet_range, messages), media_type="text/event-stream"
    )
    
    