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
        # self.openai_client_initialized = False
        self.openai_client = OpenAI(organization=os.environ["OPENAI_ORG"])
        # self.openai_client_initialized = True
        # self.bedrock_client_initialized = False
        self.bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1',
                                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                )
        # self.bedrock_client_initialized = True

    # def initialize_openai_client(self):
    #     """Initializes LLM clients to use"""
    #     self.openai_client = OpenAI(organization=os.environ["OPENAI_ORG"])
    #     self.openai_client_initialized = True
    #     print("Initialized OpenAI client")
    
    # def initialize_bedrock_client(self):
    #     self.bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1',
    #                             aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    #                             aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    #                             )
    #     self.bedrock_client_initialized = True
    #     print("Initialized boto3 client")
    
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

    def get_model_ID(self, tool_name):
        """Returns model ID to use for the given tool_name"""
        if tool_name in self.tools_to_models:
            model_name = self.tools_to_models[tool_name]
            if model_name.startswith("gpt"):
                return gpt_model_to_model_IDs[model_name]
            elif model_name.startswith("claude"):
                return claude_model_to_model_IDs[model_name]
        else:
            if self.default_call == "gpt":
                model_name = self.default_gpt_model
                return gpt_model_to_model_IDs[model_name]
            elif self.default_call == "claude":
                model_name = self.default_claude_model
                return claude_model_to_model_IDs[model_name]
            else:
                print("Could not find LLM model to use")
        return ""
    
    def call_gpt(self, model_ID, user_msg_content, tool_name):
        """Call GPT on OpenAI"""
        # if not self.openai_client_initialized:
        #     self.initialize_openai_client()

        tool, sys_msg = gpt_tools["gpt_" + tool_name]
        user_msg = {
            "role": "user",
            "content": user_msg_content
        }
        messages = [sys_msg, user_msg]

        response = self.openai_client.chat.completions.create(
            model=model_ID,
            messages=messages,
            tools=[tool],
            tool_choice="required",
        )
        print(response.choices[0].message)
        return response.choices[0].message
    
    def call_claude(self, model_ID, user_msg_content, tool_name):
        """Call Claude on AWS Bedrock"""
        # if not self.bedrock_client_initialized:
        #     self.initialize_bedrock_client()

        tool, sys_msg = claude_tools["claude_" + tool_name]
        messages = [{"role": "user", "content": user_msg_content}]
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "system": sys_msg,
            "messages": messages,
            "max_tokens": 4000,
            "tools": [tool]
        })

        response = self.bedrock_client.invoke_model(body=body, modelId=model_ID)
        response_body = json.loads(response['body'].read())
        print(response_body['content'])
        return response_body['content']

    def get_instructions(self, task_prompt, sheet_content):
        """Attempts to get list of instructions to complete task"""
        tool_name = "get_instructions"
        get_instructions_user_msg = "Table:\n" + sheet_content.to_string() + f"\nEnd Table.\nTasks:\n{task_prompt}"
        model_ID = self.get_model_ID(tool_name)
        if model_ID.startswith("gpt"):
            gpt_response = self.call_gpt(model_ID, get_instructions_user_msg, tool_name)
            get_instructions_tool_calls = gpt_response.tool_calls
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
        elif model_ID.startswith("anthropic"):
            claude_response = self.call_claude(model_ID, get_instructions_user_msg, tool_name)
            # TODO: Claude get_instructions
        else:
            print("Sorry, there was an error finding an LLM to use")
            return "Sorry, there was an error finding an LLM to use"
    
    def read_instruction(self, sheet_content, instruction_command):
        """Performs a read instruction by reading from the table"""
        tool_name = "read_table"
        read_table_user_msg = "Table:\n" + sheet_content.to_string() + f"\nEnd Table.\nInstructions:\n{instruction_command}"
        model_ID = self.get_model_ID(tool_name)
        if model_ID.startswith("gpt"):
            gpt_response = self.call_gpt(model_ID, read_table_user_msg, tool_name)
            read_table_tool_calls = gpt_response.tool_calls
            
    
    def act_streamer(self, task_prompt: str, sheet_content: str):
        """Attempts to complete given task prompt and streams outputs"""
        # 1. Get instructions
        instructions = self.get_instructions(task_prompt, sheet_content)
        print("Instructions:", instructions)
        print_instructions = " ".join([f"{instr[1]}" for instr in instructions])
        yield print_instructions

        # 2. Execute instructions
        for instruction in instructions:
            print("Executing", instruction)
            yield instruction[1]

            instruction_type = instruction[0]
            instruction_command = instruction[1]
            if instruction_type == "READ":
                read_values = self.read_instruction(sheet_content, instruction_command)
                if read_values:
                    clean_read_values = [s for s in read_values if s]
                    print_read = ", ".join(clean_read_values)
                    yield print_read
                else:
                    yield "Sheet read failed."
                    return
            elif instruction_type == "WRITE":
                new_sheet_content, success, instructions_wrote = write_instruction(sheet_content, instruction_command)
                yield get_chunk_to_yield(f"Attempted writing...\n{instructions_wrote}")
                if not success:
                    print("Couldn't complete write instruction within allowed attempts")
                    yield get_chunk_to_yield("Sheet write failed.")
                    return
                sheet_content = new_sheet_content
                write_sheet(sheets, sheet_id, sheet_range, sheet_content)
                chat_response += "Sheet write successful. "

            elif instruction_type == "CHART":
                chart_instruction_response = chart_instruction(sheet_content, instruction_command, creds, sheet_id)
                if chart_instruction_response:
                    yield get_chunk_to_yield(f"Attempted making a chart with given schema...")
                    chat_response += "Chart creation successful. "
                else:
                    yield get_chunk_to_yield("Chart creation failed.")
                    return

            elif instruction_type == "OTHER":
                other_instruction_response = other_instruction(sheet_content, instruction_command, creds, sheet_id)
                if other_instruction_response:
                    yield get_chunk_to_yield(f"Attempted completing command\n{instruction_command}")
                    chat_response += "Instruction successful. "
                else:
                    yield get_chunk_to_yield("Instruction failed.")
                    return

            elif instruction_type == "QUESTION":
                question_res = question_instruction(sheet_content, instruction_command, creds, sheet_id)
                yield get_chunk_to_yield(question_res)

            elif instruction_type == "INAPPROPRIATE":
                chat_response += "This is irrelevant to Google Sheets. "
                yield get_chunk_to_yield(f"Sorry I can't help with: {instruction_command}")
            else:
                print("Unrecognizable instruction!")
                
        print("Finished all instructions")
        yield get_chunk_to_yield("Finished executing instructions. " + chat_response)
        return

    
    def hi(self):
        # self.set_tools_to_models("create_chart", "gpt-3.5")
        # self.call_gpt("create a blue line graph of columns 1 to 10", "create_chart")
        self.set_tools_to_models("create_chart", "claude-3.5")
        self.call_claude("create a blue line graph of columns 1 to 10", "create_chart")