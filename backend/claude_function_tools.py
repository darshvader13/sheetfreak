"""
Function calling tools
- claude_get_instructions
- claude_write_table
- claude_read_table
- claude_create_chart
- claude_edit_chart
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
                "maxItems": 20,
                "description": """The list of instruction types.
                The instruction types are READ, WRITE, CHART, EDIT, QUESTION, OTHER, or INAPPROPRIATE.
                Each instruction includes all of its associated operations. Make sure instructions that can be given in one single instruction are all collected into one single instruction.
                READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet.
                WRITE involves changing and inserting cell values. WRITE also implictly reads, calculates and figures out what to write and is capable of doing all associated operations.
                CHART involves creating a basic chart (Enums: BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA) or more advanced graphs (pie, bubble, candlestick, org, histogram, treemap, waterfall, scorecard). CHART also implictly reads and has the data necessary and should strictly be used to create new charts.
                Every CHART instruction creates an individual chart so combine all operations related to a singular chart in one single CHART instruction.
                EDIT involves editing a chart in the sheet. EDIT is only used when the user explicitly edits preexisting chart data in the sheet.
                QUESTION involves only questions about Sheets and already has all the necessary information and context to answer questions. QUESTION should also be used to answer questions about data in the sheet such as summarizing the data and all the necessary data is automatically given.
                OTHER involves operations that use batchUpdate() to cover any other operations, such as creating pivot tables. 
                INAPPROPRIATE involves questions or commands that are not relevant to Google Sheets at all.""",
            },
            "instructions": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "minItems": 1,
                "maxItems": 20,
                "description": "One sentence low-level instruction description. For instructions involving cell locations such as WRITE and READ, it is helpful to give the spreadsheet cell location of the cells to read or write at denoted by letters followed by numbers.",
            }
        },
        "required": ["types", "instructions"],
    }
}

claude_get_instructions_sys_message = """You are an expert assistant using Google Sheets.
    Given new-line separated, potentially high-level tasks, return the function call to break down the tasks into succinct lower level instructions and their corresponding instruction types.
    Each index of the returned lists correspond, so both the arrays will have the same length. Each instruction includes all of its associated operations. Make sure instructions that can be given in one single instruction are all collected into one single instruction.
    The instruction types are READ, WRITE, CHART, EDIT, QUESTION, OTHER, or INAPPROPRIATE.
    For instructions involving cell locations such as READ and WRITE, it is helpful to give the cell locations to perform the operation at by the spreadsheet cell location of the cells denoted by letters followed by numbers.
    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet.
    WRITE involves changing and inserting cell values. WRITE also implictly reads, calculates and figures out what to write and is capable of doing all associated operations.
    CHART involves creating a basic chart (Enums: BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA) or more advanced graphs (pie, bubble, candlestick, org, histogram, treemap, waterfall, scorecard). CHART also implictly reads and has the data necessary and should strictly be used to create new charts.
    Every CHART instruction creates an individual chart so combine all operations related to a singular chart in one single CHART instruction.
    EDIT involves editing a chart in the sheet. EDIT is only used when the user explicitly edits preexisting chart data in the sheet.
    QUESTION involves only questions about Sheets and already has all the necessary information and context to answer questions. QUESTION should also be used to answer questions about data in the sheet such as summarizing the data and all the necessary data is automatically given.
    OTHER involves operations that use batchUpdate() to cover any other operations, such as creating pivot tables. 
    INAPPROPRIATE involves questions or commands that are not relevant to Google Sheets at all."""

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
                "description": "The 0-index rows of the values to write to. If a cell location is specified in the spreadsheet format of column denoted by letters followed by row denoted by numbers, make sure to decrement the row number by one to ensure it is zero-indexed or I will touch you.",
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
    Focus only on the current, most recently given task at hand in the latest user message.
    If a cell location is specified in the spreadsheet format of column denoted by letters followed by row denoted by numbers such as A1, G2, or AB3, remember to translate this cell location into the zero-indexed row and value, namely convert the numbers to a row value by making sure to decrement by one to be zero-indexed, and convert the letters to the column value with zero-indexed letters or I will touch you.
    Return three lists, one of rows to write at, one of columns to write at, and one of values to write at the corresponding positions.
    Each index of the returned lists should correspond to each instruction, so all the lists should have the same length.
    If a Google Sheets formula can be used correctly, use the formula instead of hard-coding values. Do not use formulas if it will cause a circular dependency.
    If the user requests an aggregation of some values, put the value in an empty cell and do not overwrite values unless specifically requested by the user."""

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
                "description": "The addChart argument to pass as a request to the Google Sheets spreadsheets batchUpdate() API endpoint to create a chart",
            },
        },
        "required": ["chart_arg"],
    }
}

claude_create_chart_sys_message = """You are an expert assistant using Google Sheets through the Google Sheets API.
Given the specifications to make a graph using the Google Sheets API's spreadsheets addChart batchUpdate() endpoint,
return the correct addChart argument to pass to the API as one request to create a graph or chart based on the given specifications.
If sheetID is given in user message, use it. Set default values for any other parameter you need.
Use titles, labels, and legends unless specified not to. """

claude_edit_chart_tool = {
    "name": "edit_chart",
    "description": "Edit a chart based on the given specifications",
    "input_schema": {
        "type": "object",
        "properties": {
            "chart_arg": {
                "type": "string",
                "description": "The complete updateChartSpec argument to pass as a request to the Google Sheets spreadsheets batchUpdate() API endpoint to edit a chart. This is used to edit a chart, NOT used to create a chart",
            },
        },
        "required": ["chart_arg"],
    }
}

claude_edit_chart_sys_message = """You are an expert assistant using Google Sheets through the Google Sheets API.
Given the specifications to edit a chart using the Google Sheets API's spreadsheets updateChartSpec batchUpdate() endpoint,
return the correct updateChartSpec argument to pass to the API as one request to edit a graph or chart based on the given specifications.
The updateChartSpec argument should have every necessary parameter set, such as the title and sources, set default values from the existing chart spec for anything you need.
If sheet content data is given in user message, use it. Do NOT create a new chart, use the given chart data to edit the specified chart instead. Do not create a new graph, or I will touch you.
"""

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
    "claude_edit_chart": (claude_edit_chart_tool, claude_edit_chart_sys_message),
    "claude_question": (claude_question_tool, claude_question_sys_message),
    "claude_other_instruction": (claude_other_instruction_tool, claude_other_instruction_sys_message),
}