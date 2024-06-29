"""
Function calling tools
- get_instructions
- update_table
- create_chart
- question
- other_instruction
- read_table
"""

get_instructions_tool = {
    "type": "function",
    "function": {
        "name": "get_instructions",
        "description": "Returns a list of lower level instructions consisting of read, write, question, or other instructions.",
        "parameters": { 
            "type": "object",
            "properties": {
                "types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": """One word instruction summary. Must be one of the following: READ, WRITE, CHART, QUESTION, OTHER, or INAPPROPRIATE.
                    READ involes only reading/getting cell values. READ is only used when the user specifically requests data in the sheet. Do not READ just for writes, or I will touch you.
                    WRITE involves changing and inserting cell values. WRITE also implictly reads and does not need to explicitly read values in.
                    CHART involves creating only a basic chart (BAR, LINE, AREA, COLUMN, SCATTER, COMBO, or STEPPED_AREA). CHART also implictly reads and does not need to explicitly read values in.
                    QUESTION involves only questions about Sheets that do not require READ, WRITE, or CHART operations. QUESTION should also be used to answer questions about data in the sheet such as summarizing the data.
                    OTHER involves Sheets operations that do not fit into READ, WRITE, CHART, or QUESTION operations, such as creating pivot tables or charts not listed in the CHART category (ex: pie chart). 
                    INAPPROPRIATE involves questions that are not relevant to Google Sheets at all. """,
                    
                },
                "instructions": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "One sentence low-level instruction description",
                }
            },
            "required": ["types", "instructions"],
        }
    }
}

get_instructions_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given new-line separated, potentially high-level tasks, 
    return the function call to break down the tasks into lower level instructions and their corresponding instruction types.
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

update_table_tool = {
    "type": "function",
    "function": {
        "name": "update_table",
        "description": "Set the value in the cell to be the given value",
        "parameters": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index rows of the values to update",
                },
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index columns of the values to update",
                },
                "values": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The values to update at the rows and columns",
                },
            },
            "required": ["rows", "columns", "values"],
        },
    },
}

update_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to update values inside cells,
    return the function call to complete the updates as if the table is a Google Sheets. 
    Each index of the returned lists should correspond to each instruction, so all the arrays should have the same length.
    If a Google Sheets formula can be used, use the formula instead of hard-coding values or I will touch you."""
}

create_chart_tool = {
    "type": "function",
    "function": {
        "name": "create_chart",
        "description": "Creates chart",
        "parameters": { 
            "type": "object",
            "properties": {
                "arguments": {
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
            "required": ["arguments"]
        }
    }
}

create_chart_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
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

question_tool = {
    "type": "function",
    "function": {
        "name": "answer_question",
        "description": "Answer question about Google Sheets",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "The answer to question about Google Sheets",
                },
            },
            "required": ["answer"],
        },
    },
}

question_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and a question regarding Google Sheets
    return the function call to answer the question as if the table is a Google Sheets. """
}

other_instruction_table_tool = {
    "type": "function",
    "function": {
        "name": "other_operation",
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

other_instruction_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and an operation to be executed via the spreadsheets batchUpdate() API endpoint,
    return the request body to complete the requested operation as if the table is a Google Sheets sheet. 
    """
}

read_table_tool = {
    "type": "function",
    "function": {
        "name": "other_operation",
        "description": "Get the values of given cells in the table",
        "parameters": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index rows of the values to get",
                },
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "The 0-index columns of the values to get",
                },
            },
            "required": ["rows", "columns"],
        },
    },
}

read_table_sys_msg = {"role": "system", "content": """You are an expert assistant using Google Sheets.
    Given a table in a pandas dataframe representation and new-line separated instructions to get values inside cells,
    return the function call to complete the get calls as if the table is a Google Sheets. 
    Each index of the returned lists correspond, so both the arrays will have the same length."""
}