from modal import App, Image, web_endpoint, Secret
from LLMAgent import LLMAgent

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

@app.function(image=image, secrets=[Secret.from_name("sheetfreak_OPENAI_API_KEY"), Secret.from_name("sheetfreak_OPENAI_ORG"), Secret.from_name("sheetfreak_AWS_ACCESS_KEY_ID"), Secret.from_name("sheetfreak_AWS_SECRET_ACCESS_KEY")])
@web_endpoint(method="GET")
def home():
    agent = LLMAgent()
    agent.hi()
    return "sheetfreak"