from LLMAgent import LLMAgent

from modal import App, Image, web_endpoint, Secret
from fastapi.responses import StreamingResponse

app = App("sheetfreak_dev")

image = (
    Image.debian_slim()
    .pip_install("google-api-python-client")
    .pip_install("google-auth-httplib2")
    .pip_install("google-auth-oauthlib")
    .pip_install("pandas")
    .pip_install("openai")
    .pip_install("boto3")
)

@app.function(image=image, secrets=[Secret.from_name("sheetfreak_GOOGLE_CREDS_CRICK"), Secret.from_name("sheetfreak_OPENAI_API_KEY"), Secret.from_name("sheetfreak_OPENAI_ORG"), Secret.from_name("sheetfreak_AWS_ACCESS_KEY_ID"), Secret.from_name("sheetfreak_AWS_SECRET_ACCESS_KEY")])
@web_endpoint(method="GET")
def home():
    agent = LLMAgent()
    agent.set_tools_to_models("question", "gpt-3.5")
    task_prompt = "What is in this sheets"
    sheet_id = "1gVcLhpeszKixK9H5cg2SygUWnaJnePnifEGvj36TFMI"
    sheet_range = "Sheet1"
    return StreamingResponse(
        agent.act_streamer(task_prompt, sheet_id, sheet_range), media_type="text/event-stream"
    )
