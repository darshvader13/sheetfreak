from flask import Flask, request, Response, stream_with_context, jsonify

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = Flask(__name__)

DRIVE_FOLDER = "1LAEzfodH-7MUQcEZRJlifSXxkrSPhTUY"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_authorized_user_file("token.json", SCOPES)
drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build("sheets", "v4", credentials=creds)

# def generate_large_data():
#     """Stream data by yielding"""
#     for i in range(1000):
#         yield f"Chunk {i}\n"
#         time.sleep(0.1)

@app.route('/')
def home():
    return jsonify("freakinthesheets"), 200

@app.route('/ingest', methods=['POST'])
def ingest():
    """Copy the user given Google Sheets into local Google Drive and return local sheets ID"""
    data = request.get_json()

    if not data or 'input' not in data:
        return jsonify({"error": "No input provided"}), 400
    user_sheets_share_link = data['input']
    user_sheets_id = user_sheets_share_link.split('/')[5]
    print("Found user sheets id:", user_sheets_id)

    user_sheets = sheets_service.spreadsheets().get(spreadsheetId=user_sheets_id).execute()
    user_sheets_title = user_sheets.get('properties').get('title')
    print("Found user sheets title:", user_sheets_title)

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
    return jsonify(copied_file_id), 200

# @app.route('/stream')
# def stream():
#     return Response(stream_with_context(generate_large_data()), mimetype='text/plain')

if __name__ == '__main__':
    app.run()
