"""
Function calling tools
- claude_get_instructions
- claude_write_table
- claude_read_table
- claude_create_chart
- claude_question
- claude_other_instruction
"""

# TODO: make tool names, arg names more descriptive, it's prompting all the way down

claude_get_instructions_tool = {
    "name": "get_instructions",
    "description": "Returns a list of lower level instructions consisting of read, write, chart, question, other, or inappropriate instructions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "types": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": """One word instruction summary. Must be one of the following: READ, WRITE, CHART, QUESTION, OTHER, or INAPPROPRIATE.
                Be concise, each instruction includes all of its related sub-instructions. For example, making a single write instruction includes the implicit read instructions needed. A single instruction to make a chart includes making all aspects of the chart to desired specifications.
                READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet.
                WRITE involves changing and inserting cell values. You already have the necessary information to manipulate values. You already have calculated everything you need to.
                CHART involves creating only a basic chart (BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA). CHART also implictly reads and does not need to explicitly read values in.
                QUESTION involves only questions about Google Sheets that do not require READ, WRITE, or CHART operations. QUESTION should also be used to answer questions about data in the sheet such as summarizing the data.
                OTHER involves Sheets operations that do not fit into READ, WRITE, CHART, or QUESTION operations, such as creating pivot tables or charts not listed in the CHART category (ex: pie chart). 
                INAPPROPRIATE involves questions that are not relevant to Google Sheets at all. """,
            },
            "instructions": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": "One sentence low-level instruction description",
            }
        },
        "required": ["types", "instructions"],
    }
}

claude_get_instructions_sys_message = """You are an expert assistant using Google Sheets.
    Given new-line separated, potentially high-level tasks, return the function call to break down the tasks into lower level instructions and their corresponding instruction types.
    Each index of the returned lists correspond, so both the arrays will have the same length.
    The instruction types are READ, WRITE, CHART, QUESTION, OTHER, or INAPPROPRIATE.
    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet. Do not READ just for writes, or I will touch you.
    WRITE involves changing and inserting cell values. WRITE also implictly reads and does not need to explicitly read values in.
    CHART involves creating only a basic chart (BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA). CHART also implictly reads and does not need to explicitly read values in.
    QUESTION involves only questions about Sheets that do not require READ, WRITE, or CHART operations. QUESTION should also be used to answer questions about data in the sheet such as summarizing the data.
    OTHER involves operations that do not fit into READ, WRITE, CHART or QUESTION operations, such as creating pivot tables or charts not listed in the CHART category (ex: pie chart). 
    INAPPROPRIATE involves questions that are not relevant to Google Sheets at all."""

claude_write_table_tool = {
    "name": "write_table",
    "description": "Sets the contents of the cells to be the given values",
    "input_schema": {
        "type": "object",
        "properties": {
            "list_of_rows": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": "The 0-index rows of the values to write to",
            },
            "list_of_columns": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": "The 0-index columns of the values to write to",
            },
            "list_of_values": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": "The values to write at the rows and columns",
            },
        },
        "required": ["list_of_rows", "list_of_columns", "list_of_values"],
    }
}

claude_write_table_sys_message = """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to write values to cells,
    return the function call to complete the writes as if the table is a Google Sheets. 
    Return three lists, one of rows to write at, one of columns to write at, and one of values to write at the corresponding positions.
    Each index of the returned lists should correspond to each instruction, so all the lists should have the same length.
    If a Google Sheets formula can be used, use the formula instead of hard-coding values or I will touch you."""

claude_read_table_tool = {
    "name": "read_table",
    "description": "Get the values of the given cells in the table",
    "input_schema": {
        "type": "object",
        "properties": {
            "rows": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": "The 0-index rows of the values to get",
            },
            "columns": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "minItems": 1,
                "maxItems": 1000,
                "description": "The 0-index columns of the values to get",
            },
        },
        "required": ["rows", "columns"],
    }
}

claude_read_table_sys_message = """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to get values inside cells,
    return the function call to complete the get calls as if the table is a Google Sheets. 
    Each index of the returned lists correspond, so both the arrays will have the same length."""

claude_create_chart_tool = {
    "name": "create_chart",
    "description": "Create a chart based on the given specifications",
    "input_schema": {
        "type": "object",
        "properties": {
            "chart_arg": {
                "type": "string",
                "description": "The argument to pass to the Google Sheets spreadsheets batchUpdate() API endpoint to create a chart",
            },
        },
        "required": ["chart_arg"],
    }
}

claude_create_chart_sys_message = """You are an expert assistant using Google Sheets through the Google Sheets API.
Given the specifications to make a graph using the Google Sheets API's spreadsheets batchUpdate() endpoint,
return the correct argument to pass to the API to create a graph or chart based on the given specifications.
Set default values for any other parameter you need. If sheetID is given in user message, use it."""

claude_question_tool = {
    "name": "question",
    "description": "Answers question about Google Sheets",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "The answer to the question about Google Sheets",
            },
        },
        "required": ["answer"],
    }
}

claude_question_sys_message = """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and a question regarding Google Sheets
    return the function call to answer the question as if the table is a Google Sheets."""

claude_other_instruction_tool = {
    "name": "other_instruction",
    "description": "Executes Google Spreadsheets spreadsheets.batchUpdate() API endpoint with given request body",
    "input_schema": {
        "type": "object",
        "properties": {
            "body": {
                "type": "string",
                "description": "The stringified JSON body to call Google Spreadsheets spreadsheets.batchUpdate() API with as the body argument",
            },
        },
        "required": ["body"],
    }
}

claude_other_instruction_sys_message = """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and an operation to be executed via the spreadsheets batchUpdate() API endpoint,
    return the request body to complete the requested operation as if the table is a Google Sheets sheet."""

claude_tools = {
    "claude_get_instructions": (claude_get_instructions_tool, claude_get_instructions_sys_message),
    "claude_write_table": (claude_write_table_tool, claude_write_table_sys_message),
    "claude_read_table": (claude_read_table_tool, claude_read_table_sys_message),
    "claude_create_chart": (claude_create_chart_tool, claude_create_chart_sys_message),
    "claude_question": (claude_question_tool, claude_question_sys_message),
    "claude_other_instruction": (claude_other_instruction_tool, claude_other_instruction_sys_message),
}