import os
import json
import traceback
from TableAgent import *
from gpt_function_tools import *
from claude_function_tools import *

from openai import OpenAI
import boto3

model_to_model_IDs = {
    "gpt-4o": "gpt-4o",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-4": "gpt-4",
    "gpt-3.5": "gpt-3.5-turbo",
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

instruction_type_to_tool_name = {
    "WRITE": "write_table",
    "READ": "read_table",
    "CHART": "create_chart",
    "QUESTION": "question",
    "OTHER": "other_instruction",
}

# TODO: timeit measure latency of class methods
class LLMAgent:
    """LLMAgent is the orchestrated agent responsible for making LLM calls to plan and produce instructions"""

    def __init__(self, default_call="gpt", default_gpt_model="gpt-4o", default_claude_model="claude-3.5", tools_to_models={}):
        self.max_attempts = 5
        self.default_call = default_call # Either 'gpt' or 'claude'
        self.default_gpt_model = default_gpt_model
        self.default_claude_model = default_claude_model
        self.tools_to_models = tools_to_models # Maps tool's function name to model to use for that tool
        self.openai_client = OpenAI(organization=os.environ["OPENAI_PERSONAL_ORG"])
        self.bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1',
                                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                )
    
    def set_default_call(self, call):
        """Sets the default call (either gpt or claude)"""
        self.default_call = call
        print("default_call:", self.default_call)

    def set_tools_to_models(self, key, value):
        """Sets the model to use for the given tool"""
        if key not in tools:
            print("Invalid tool!")
            return
        if value not in model_to_model_IDs:
            print("Invalid model!")
            return
        self.tools_to_models[key] = value
        print("tools_to_models:", self.tools_to_models)

    def get_model_ID(self, tool_name):
        """Returns model ID to use for the given tool_name"""
        if tool_name in self.tools_to_models:
            model_name = self.tools_to_models[tool_name]
            return model_to_model_IDs[model_name]
        else:
            if self.default_call == "gpt":
                model_name = self.default_gpt_model
                return model_to_model_IDs[model_name]
            elif self.default_call == "claude":
                model_name = self.default_claude_model
                return model_to_model_IDs[model_name]
            else:
                print("Could not find LLM model to use")
        return ""
    
    def clean_messages(self, messages):
        """Cleans messages received from user"""
        if not messages:
            return []
        cleaned = []
        fluff_messages = {"Starting...", "Finished reading in data..."}
        for message in messages:
            sender = message["sender"]
            if sender == "user":
                role = "user"
            elif sender == "bot":
                role = "assistant"
            else:
                print("Unrecognized message sender")
                return
            content = message["text"]
            if role == "assistant":
                if content in fluff_messages:
                    continue
            cleaned.append({"role": role, "content": content})

        # Merge assistant messages (Claude does not allow multiple assistant messages in a row)
        final = [cleaned[0]]
        for message in cleaned[1:]:
            if message["role"] == "assistant" and final[-1]["role"] == "assistant":
                    final[-1]["content"] += "\n" + message["content"]
            else:
                final.append(message)
        return final
    
    def add_assistant_message(self, messages: list, new_message: str):
        """Add message to message history and merges assistant messages"""
        if messages and messages[-1]["role"] == "assistant":
            messages[-1]["content"] += "\n" + new_message
        else:
            messages.append({"role": "assistant", "content": new_message})
        return messages
    
    def call_gpt(self, model_ID, user_msg_content, tool_name, messages):
        """Call GPT on OpenAI"""
        tool, sys_msg = gpt_tools["gpt_" + tool_name]
        user_msg = {
            "role": "user",
            "content": user_msg_content
        }
        messages = [sys_msg] + messages + [user_msg]
        print(messages)
        response = self.openai_client.chat.completions.create(
            model=model_ID,
            messages=messages,
            tools=[tool],
            tool_choice="required",
        )
        print(response.choices[0].message)
        return response.choices[0].message
    
    def call_claude(self, model_ID, user_msg_content, tool_name, messages):
        """Call Claude on AWS Bedrock"""
        tool, sys_msg = claude_tools["claude_" + tool_name]
        messages = messages + [{"role": "user", "content": user_msg_content}]
        print(messages)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "system": sys_msg,
            "messages": messages,
            "max_tokens": 4000,
            "tools": [tool],
            "tool_choice": {"type": "any"},
        })

        response = self.bedrock_client.invoke_model(body=body, modelId=model_ID)
        response_body = json.loads(response['body'].read())
        print(response_body['content'])
        return response_body['content']

    def get_instruction_args(self, tool_name, task, sheet_content, sheet_id, args_names, messages, prev_response, prev_response_error):
        """Gets instructions arguments.
        Returns success bool, error message, and args.
        """
        user_msg = "Table:\n" + sheet_content + f"\nEnd Table.\nInstructions:\n{task}"
        if "chart" in tool_name:
            user_msg += " The sheet id is: " + str(sheet_id)
        if prev_response:
            user_msg += f"\nYour previous response was {prev_response} which resulted in an error."
        if prev_response_error:
            user_msg += f"\nThe error was: {prev_response_error}"
        print("User message:", user_msg)
        model_ID = self.get_model_ID(tool_name)
        print("Using model:", model_ID)
        if model_ID.startswith("gpt"):
            gpt_response = self.call_gpt(model_ID, user_msg, tool_name, messages)
            tool_calls = gpt_response.tool_calls
            args_collection = [None for _ in range(len(args_names))]
            for i in range(len(tool_calls)):
                instruction_args = tool_calls[i].function.arguments
                print(f"{tool_name} function args:", instruction_args)
                args = json.loads(instruction_args)
                for j in range(len(args_names)):
                    if not args_collection[j]:
                        args_collection[j] = args[args_names[j]]
                    else:
                        if type(args_collection[j]) == str:
                            args_collection[j] += " " + args[args_names[j]]
                        else:
                            args_collection[j] += args[args_names[j]]
                    if j > 0 and type(args_collection[j]) == list and type(args_collection[j-1]) == list:
                        if len(args_collection[j]) != len(args_collection[j-1]):
                            print("Invalid instructions")
                            return False, "Invalid instructions length", instruction_args
            print("Args collection:", args_collection)
            if tool_name != "get_instructions" and tool_name != "write_table" and tool_name != "read_table":
                return True, "", args_collection
            assert(type(args_collection[0] == list))
            instruction_args = []
            for i in range(len(args_collection[0])):
                curr_instruction = [args_collection[j][i] for j in range(len(args_names))]
                instruction_args.append(curr_instruction)
            print("Args zipped:", instruction_args)
            return True, "", instruction_args
        elif model_ID.startswith("anthropic"):
            claude_response = self.call_claude(model_ID, user_msg, tool_name, messages)
            args_collection = {}
            for item in claude_response:
                if item['type'] == "tool_use":
                    args = item['input']
                    for arg_name in args_names:
                        if arg_name in args_collection:
                            print("Redundant argument")
                            return False, "redundant argument", str(args)
                        args_collection[arg_name] = args[arg_name]

            args_collection_list = []
            for i, arg_name in enumerate(args_names):
                args_collection_list.append(args_collection[arg_name])
                if i > 0 and type(args_collection_list[i]) == list and type(args_collection_list[i-1]) == list:
                    if len(args_collection_list[i]) != len(args_collection_list[i-1]):
                        print("Invalid instructions")
                        return False, "Invalid instructions length", str(args_collection)
            print(f"{tool_name} function args collected: {args_collection_list}")
            if tool_name != "get_instructions" and tool_name != "write_table" and tool_name != "read_table":
                return True, "", args_collection_list
            assert(type(args_collection_list[0] == list))
            instruction_args = []
            for i in range(len(args_collection_list[0])):
                curr_instruction = [args_collection_list[j][i] for j in range(len(args_names))]
                instruction_args.append(curr_instruction)
            print("Args zipped:", instruction_args)
            return True, "", instruction_args
            
        else:
            print("Invalid LLM")
            return False, "Invalid LLM", ""

    def get_arg_names(self, instruction_type):
        if instruction_type == "get_instructions":
            return ["types", "instructions"]
        elif instruction_type == "WRITE":
            return ["list_of_rows", "list_of_columns", "list_of_values"]
        elif instruction_type == "READ":
            return ["rows", "columns"]
        elif instruction_type == "CHART":
            return ["chart_arg"]
        elif instruction_type == "QUESTION":
            return ["answer"]
        elif instruction_type == "OTHER":
            return ["body"]
    
    def act_streamer(self, task_prompt: str, spreadsheet_id: str, messages: list):
        """Attempts to complete given task prompt and streams outputs"""
        try:
            table_agent = TableAgent(spreadsheet_id)
            sheet_range = table_agent.get_sheets_names()[0]
            sheet_id = table_agent.get_sheets_ids()[0]
            sheet_content = table_agent.get_sheet_content(sheet_range)

            yield get_chunk_to_yield("Finished reading in data...")
        except:
            error_details = traceback.format_exc()
            print(f"Error: {error_details}")
            yield get_chunk_to_yield("Error reading data")
            return
        
        messages = self.clean_messages(messages)
        
        # 1. Get instructions
        prev_response = None
        prev_response_error = None
        instructions = None
        for attempt_num in range(1, self.max_attempts+1):
            try:
                print(f"Attempt {attempt_num} of get_instructions")
                success, error_msg, args = self.get_instruction_args("get_instructions", task_prompt, sheet_content, sheet_id, self.get_arg_names("get_instructions"), messages, prev_response, prev_response_error)
                if not success:
                    assert(type(error_msg) == type(args) == str)
                    prev_response = args
                    prev_response_error = error_msg
                    print("Error in get_instructions", error_msg)
                    continue
                else:
                    instructions = args
                    break
            except Exception as e:
                print("Error in get_instructions")
                print(e)
                if str(e).startswith("Error code: 429"):
                    # Rate limited
                    yield get_chunk_to_yield("Sorry, please try again in a few minutes!")
                    return
                continue
        print("Instructions:", instructions)
        if instructions == None:
            yield get_chunk_to_yield("Error getting instructions")
            return
        print_instructions = "Plan:\n" + "\n".join([instr[1] for instr in instructions])
        yield get_chunk_to_yield(print_instructions)

        if "INAPPROPRIATE" in [instr[0] for instr in instructions]:
            yield get_chunk_to_yield(f"Sorry I can't help with: {task_prompt}")
            return
        
        if not messages:
            messages = [{"role": "user", "content": task_prompt}]
        messages = self.add_assistant_message(messages, print_instructions)

        # 2. Execute instructions
        need_to_push_sheet_content = False
        for instruction in instructions:
            print("Executing", instruction)
            yield get_chunk_to_yield(f"Executing...\n{instruction[1]}")
            messages = self.add_assistant_message(messages, f"Executing...\n{instruction[1]}")

            prev_response = None
            prev_response_error = None
            failed_all_attempts = True
            for attempt_num in range(1, self.max_attempts+1):
                try:
                    instruction_type = instruction[0]
                    instruction_command = instruction[1]
                    print(f"Attempt {attempt_num} of {instruction_type}: {instruction_command}")
                    if instruction_type not in instruction_type_to_tool_name:
                        print("Unrecognized instruction type")
                        break
                    
                    success, error_msg, args = self.get_instruction_args(instruction_type_to_tool_name[instruction_type], instruction_command, sheet_content, sheet_id, self.get_arg_names(instruction_type), messages, prev_response, prev_response_error)
                    if not success:
                        assert(type(error_msg) == type(args) == str)
                        prev_response = args
                        prev_response_error = error_msg
                        print("Error:", error_msg)
                        continue
                    info_instruction_type = instruction_type
                    if instruction_type == "CHART":
                        if "create_chart" in self.tools_to_models:
                            if self.tools_to_models["create_chart"].startswith("claude"):
                                info_instruction_type += "-claude"
                            else:
                                info_instruction_type += "-gpt"
                        else:
                            info_instruction_type += "-" + self.default_call
                    success, error_msg, result = table_agent.execute_instruction(info_instruction_type, args)
                    if not success:
                        assert(type(error_msg) == type(result) == str)
                        prev_response = result
                        prev_response_error = error_msg
                        print("Error:", error_msg)
                        continue
                    if instruction_type == "WRITE":
                        need_to_push_sheet_content = True
                        sheet_content = table_agent.get_sheet_content_current()
                    yield get_chunk_to_yield(result)
                    messages = self.add_assistant_message(messages, result)
                    failed_all_attempts = False
                    break
                except:
                    error_details = traceback.format_exc()
                    print(f"Error: {error_details}")
                    prev_response = None
                    prev_response_error = None
                    continue
            if failed_all_attempts:
                yield get_chunk_to_yield("Failed instruction after all attempts")
                messages = self.add_assistant_message(messages, "Failed instruction after all attempts")
        yield get_chunk_to_yield("Finished executing all instructions.")
        if need_to_push_sheet_content:
            push_result = table_agent.push_sheet_content(sheet_range)
            yield get_chunk_to_yield(push_result)
        return

def get_chunk_to_yield(chunk):
    return chunk + " --END_CHUNK-- "