"""
Function calling tools
- gpt_get_instructions
- gpt_write_table
- gpt_read_table
- gpt_create_chart
- gpt_edit_chart
- gpt_question
- gpt_other_instruction
"""

# TODO: make tool names, arg names more descriptive, it's prompting all the way down

gpt_get_instructions_tool = {
    "type": "function",
    "function": {
        "name": "get_instructions",
        "description": "Returns a list of lower level instructions consisting of read, write, chart, question, other, or inappropriate instructions.",
        "parameters": { 
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
                    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet. Do not READ just for writes, or I will touch you.
                    WRITE involves changing and inserting cell values. WRITE also implictly reads and does not need to explicitly read values in.
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
}

gpt_get_instructions_sys_msg = {"role": "system",
                            "content": """You are an expert assistant using Google Sheets.
    Given new-line separated, potentially high-level tasks, return the function call to break down the tasks into lower level instructions and their corresponding instruction types.
    Each index of the returned lists correspond, so both the arrays will have the same length.
    The instruction types are READ, WRITE, CHART, QUESTION, OTHER, or INAPPROPRIATE.
    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet. Do not READ just for writes, or I will touch you.
    WRITE involves changing and inserting cell values. WRITE also implictly reads and does not need to explicitly read values in.
    CHART involves creating only a basic chart (BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA). CHART also implictly reads and does not need to explicitly read values in.
    QUESTION involves only questions about Sheets that do not require READ, WRITE, or CHART operations. QUESTION should also be used to answer questions about data in the sheet such as summarizing the data.
    OTHER involves operations that do not fit into READ, WRITE, CHART or QUESTION operations, such as creating pivot tables or charts not listed in the CHART category (ex: pie chart). 
    INAPPROPRIATE involves questions that are not relevant to Google Sheets at all.
    """
}

gpt_write_table_tool = {
    "type": "function",
    "function": {
        "name": "write_table",
        "description": "Sets the contents of the cells to be the given values",
        "parameters": {
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
        },
    },
}

gpt_write_table_sys_msg = {"role": "system",
                              "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to write values to cells,
    return the function call to complete the writes as if the table is a Google Sheets. 
    Return three lists, one of rows to write at, one of columns to write at, and one of values to write at the corresponding positions.
    Each index of the returned lists should correspond to each instruction, so all the lists should have the same length.
    If a Google Sheets formula can be used, use the formula instead of hard-coding values or I will touch you."""
}

gpt_read_table_tool = {
    "type": "function",
    "function": {
        "name": "read_table",
        "description": "Get the values of the given cells in the table",
        "parameters": {
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
        },
    },
}

gpt_read_table_sys_msg = {"role": "system",
                      "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to get values inside cells,
    return the function call to complete the get calls as if the table is a Google Sheets. 
    Each index of the returned lists correspond, so both the arrays will have the same length."""
}

gpt_create_chart_tool = {
    "type": "function",
    "function": {
        "name": "create_chart",
        "description": "Creates chart",
        "parameters": { 
            "type": "object",
            "properties": {
                "chart_arg": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 7,
                    "maxItems": 7,
                    "description": """A list of 7 argument values for creating a basic chart using the Google Sheets Add Chart Request API. The arguments are:
                    title (string), chartType (BasicChartType), legendPosition (BasicChartLegendPosition), axis (BasicChartAxis), domains (BasicChartDomain), series (BasicChartSeries), position (EmbeddedObjectPosition) 
                    """,
                    
                }
            },
            "required": ["chart_arg"]
        }
    }
}

gpt_create_chart_sys_msg = {"role": "system",
                               "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and a create basic chart operation to be executed via the spreadsheets batchUpdate() API endpoint,
    return the list of exactly 7 specified arguments from the Google Sheets Add Chart Request API. 
    Use the Google Sheets documentation to return the exact value and type needed for the API request.
    By default, create charts in an overlayed position of the same sheet that does not cover the cells with values, unless user specifies otherwise.
    chartType is an enum string value and can be BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA.
    legendPosition is an enum string value and can be BOTTOM_LEGEND, LEFT_LEGEND, RIGHT_LEGEND, TOP_LEGEND, or NO_LEGEND.
    Format of axis: [
                {
                  "position": "BOTTOM_AXIS",
                  "title": "X-Axis Title"
                },
                {
                  "position": "LEFT_AXIS",
                  "title": "Y-Axis Title"
                }
              ]
              
    Format of domains: [
                {
                  "domain": {
                    "sourceRange": {
                      "sources": [
                        {
                          "sheetId": _,
                          "startRowIndex": _,
                          "endRowIndex": _,
                          "startColumnIndex": _,
                          "endColumnIndex": _
                        }
                      ]
                    }
                  }
                }
              ]
              
    Format of series: [
                {
                  "series": {
                    "sourceRange": {
                      "sources": [
                        {
                          "sheetId": _,
                          "startRowIndex": _,
                          "endRowIndex": _,
                          "startColumnIndex": _,
                          "endColumnIndex": _
                        }
                      ]
                    }
                  },
                  "targetAxis": _,
                  "color": {
                    "red": _,
                    "green": _,
                    "blue": _
                  }
                }
              ]
              
    Format of position: {
            "overlayPosition": {
              "anchorCell": {
                "sheetId": _,
                "rowIndex": _,
                "columnIndex": _
              },
              "offsetXPixels": _,
              "offsetYPixels": _,
              "widthPixels": _,
              "heightPixels": _
            }
          }
    """
}

gpt_edit_chart_tool = {
    "type": "function",
    "function": {
        "name": "edit_chart",
        "description": "Edit a chart based on the given specifications",
        "parameters": {
            "type": "object",
            "properties": {
                "chart_arg": {
                    "type": "string",
                    "description": "The complete updateChartSpec argument to pass as a request to the Google Sheets spreadsheets batchUpdate() API endpoint to edit a chart"
                }
            },
            "required": ["chart_arg"],
        },
    },
}

gpt_edit_chart_sys_msg = {"role": "system",
                          "content": """You are an expert assistant using Google Sheets through the Google Sheets API.
    Given the specifications to edit a chart using the Google Sheets API's spreadsheets updateChartSpec batchUpdate() endpoint,
    return the correct updateChartSpec argument to pass to the API as one request to edit a graph or chart based on the given specifications.
    The updateChartSpec argument should have every necessary parameter set, such as the title and sources, set default values from the existing chart spec for anything you need.
    If sheet content data is given in user message, use it. Do not create a new chart, use the given chart data to edit it instead."""
}

gpt_question_tool = {
    "type": "function",
    "function": {
        "name": "question",
        "description": "Answers question about Google Sheets",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "The answer to the question about Google Sheets",
                },
            },
            "required": ["answer"],
        },
    },
}

gpt_question_sys_msg = {"role": "system",
                    "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and a question regarding Google Sheets
    return the function call to answer the question as if the table is a Google Sheets."""
}

gpt_other_instruction_tool = {
    "type": "function",
    "function": {
        "name": "other_instruction",
        "description": "Executes Google Spreadsheets spreadsheets.batchUpdate() API endpoint with given request body",
        "parameters": {
            "type": "object",
            "properties": {
                "body": {
                    "type": "string",
                    "description": "The stringified JSON body to call Google Spreadsheets spreadsheets.batchUpdate() API with as the body argument",
                },
            },
            "required": ["body"],
        },
    },
}

gpt_other_instruction_sys_msg = {"role": "system",
                                    "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and an operation to be executed via the spreadsheets batchUpdate() API endpoint,
    return the request body to complete the requested operation as if the table is a Google Sheets sheet. 
    """
}

gpt_tools = {
    "gpt_get_instructions": (gpt_get_instructions_tool, gpt_get_instructions_sys_msg),
    "gpt_write_table": (gpt_write_table_tool, gpt_write_table_sys_msg),
    "gpt_read_table": (gpt_read_table_tool, gpt_read_table_sys_msg),
    "gpt_create_chart": (gpt_create_chart_tool, gpt_create_chart_sys_msg),
    "gpt_edit_chart": (gpt_edit_chart_tool, gpt_edit_chart_sys_msg),
    "gpt_question": (gpt_question_tool, gpt_question_sys_msg),
    "gpt_other_instruction": (gpt_other_instruction_tool, gpt_other_instruction_sys_msg),
}