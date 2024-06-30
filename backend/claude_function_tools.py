"""
Function calling tools
- claude_create_chart
"""

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
        "required": ["chart_arg",],
    }
}

claude_create_chart_sys_message = """You are an expert assistant using Google Sheets through the Google Sheets API.
Given the specifications to make a graph using the Google Sheets API's spreadsheets batchUpdate() endpoint,
return the correct argument to pass to the API to create a graph or chart based on the given specifications."""

claude_tools = {
    "claude_create_chart": (claude_create_chart_tool, claude_create_chart_sys_message)
}