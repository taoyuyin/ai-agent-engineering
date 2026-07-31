from .models import ToolDefinition


def to_openai(tool: ToolDefinition):
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.input_schema,
        "strict": True,
    }


def to_anthropic(tool: ToolDefinition):
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.input_schema,
        "strict": True,
    }


def to_google(tool: ToolDefinition):
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.input_schema,
    }
