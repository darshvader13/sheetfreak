import os
import json
from gpt_function_tools import *
from claude_function_tools import *

from openai import OpenAI
import boto3

gpt_model_to_model_IDs = {
    # Must start with 'gpt'
    "gpt-4o": "gpt-4o",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-4": "gpt-4",
    "gpt-3.5": "gpt-3.5-turbo",
}

claude_model_to_model_IDs = {
    # Must start with 'claude'
    "claude-3.5": "anthropic.claude-3-5-sonnet-20240620-v1:0",
}

tools = {
    "get_instructions",
    "write_table",
    "read_table",
    "create_chart",
    "question",
    "other_instruction"
}

# TODO: timeit measure latency of class methods
class LLMAgent:
    """LLMAgent is the orchestrated agent responsible for making LLM calls to plan and produce instructions"""

    def __init__(self, default_call="gpt", default_gpt_model="gpt-4o", default_claude_model="claude-3.5"):
        # Maps tool's function name to model to use for that tool
        self.tools_to_models = {}
        self.default_call = default_call
        self.default_gpt_model = default_gpt_model
        self.default_claude_model = default_claude_model
        self.openai_client = None
        self.bedrock_client = None
        self.openai_client_initialized = False
        self.openai_client = OpenAI(organization=os.environ["OPENAI_ORG"])
        self.openai_client_initialized = True
        self.bedrock_client_initialized = False
        self.bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1',
                                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                )
        self.bedrock_client_initialized = True

    def initialize_openai_client(self):
        """Initializes LLM clients to use"""
        self.openai_client = OpenAI(organization=os.environ["OPENAI_ORG"])
        self.openai_client_initialized = True
        print("Initialized OpenAI client")
    
    def initialize_bedrock_client(self):
        self.bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1',
                                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                )
        self.bedrock_client_initialized = True
        print("Initialized boto3 client")
    
    def set_tools_to_models(self, key, value):
        """Sets the model to use for the given tool"""
        if key not in tools:
            print("Invalid tool!")
            return
        if value not in gpt_model_to_model_IDs and value not in claude_model_to_model_IDs:
            print("Invalid model!")
            return
        self.tools_to_models[key] = value
        print("tools_to_models:", self.tools_to_models)

    def call_gpt(self, user_msg_content, tool_name):
        """Call GPT on OpenAI"""
        if not self.openai_client_initialized:
            self.initialize_openai_client()

        tool, sys_msg = gpt_tools["gpt_" + tool_name]
        user_msg = {
            "role": "user",
            "content": user_msg_content
        }
        messages = [sys_msg, user_msg]
        modelName = self.tools_to_models[tool_name] if tool_name in self.tools_to_models else self.default_gpt_model
        modelID = gpt_model_to_model_IDs[modelName]

        response = self.openai_client.chat.completions.create(
            model=modelID,
            messages=messages,
            tools=[tool],
            tool_choice="required",
        )
        print(response.choices[0].message)
    
    def call_claude(self, user_msg_content, tool_name):
        """Call Claude on AWS Bedrock"""
        if not self.bedrock_client_initialized:
            self.initialize_bedrock_client()

        tool, sys_msg = claude_tools["claude_" + tool_name]
        messages = [{"role": "user", "content": user_msg_content}]
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "system": sys_msg,
            "messages": messages,
            "max_tokens": 4000,
            "tools": [tool]
        })
        modelName = self.tools_to_models[tool_name] if tool_name in self.tools_to_models else self.default_claude_model
        modelID = claude_model_to_model_IDs[modelName]

        response = self.bedrock_client.invoke_model(body=body, modelId=modelID)
        response_body = json.loads(response['body'].read())
        print(response_body['content'])

    def act_streamer(self, task_prompt: str, sheet_content: str):
        """Attempts to complete given task prompt and streams outputs"""

    
    def hi(self):
        # self.set_tools_to_models("create_chart", "gpt-3.5")
        # self.call_gpt("create a blue line graph of columns 1 to 10", "create_chart")
        self.set_tools_to_models("create_chart", "claude-3.5")
        self.call_claude("create a blue line graph of columns 1 to 10", "create_chart")