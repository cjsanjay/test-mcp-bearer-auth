"""MCP server with API key authentication using FastMCP."""

import argparse
import json
import os
from datetime import datetime
import uuid as uuid_module
from typing import Any

import uvicorn
from dotenv import load_dotenv

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier


load_dotenv()


DEFAULT_API_KEY = "mcp_sk_7a8f9e2d4c1b6h5g3j0k9m8n7p6q5r4s3t2u1v0w"


verifier = StaticTokenVerifier(
    tokens={
        "dev-alice-token": {
            "client_id": "alice@company.com",
            "scopes": ["read:data", "write:data", "admin:users"]
        },
        "dev-guest-token": {
            "client_id": "guest-user",
            "scopes": ["read:data"]
        }
    },
    required_scopes=["read:data"]
)


# Initialize FastMCP server with API key authentication
mcp = FastMCP(
    name="test_mcp_server",
    json_response=False,
    stateless_http=False,
    auth=verifier
)

@mcp.tool()
async def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time.
{{ ... }}
    Args:
        timezone: Timezone (optional, defaults to UTC)
    """
    current_time = datetime.now()
    result = {
        "tool": "get_current_time",
        "timestamp": current_time.isoformat(),
        "timezone": timezone,
        "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "unix_timestamp": int(current_time.timestamp())
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def calculate(operation: str, a: float, b: float) -> str:
    """Perform basic arithmetic calculations.
    
    Args:
        operation: The arithmetic operation (add, subtract, multiply, divide)
        a: First operand
        b: Second operand
    """
    if operation == "add":
        result_value = a + b
    elif operation == "subtract":
        result_value = a - b
    elif operation == "multiply":
        result_value = a * b
    elif operation == "divide":
        if b == 0:
            return json.dumps({
                "error": "Division by zero",
                "message": "Cannot divide by zero"
            }, indent=2)
        result_value = a / b
    else:
        return json.dumps({
            "error": "Invalid operation",
            "message": f"Unknown operation: {operation}"
        }, indent=2)
    
    result = {
        "tool": "calculate",
        "operation": operation,
        "operands": {"a": a, "b": b},
        "result": result_value
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def reverse_string(text: str) -> str:
    """Reverse a given string.
    
    Args:
        text: The text to reverse
    """
    reversed_text = text[::-1]
    result = {
        "tool": "reverse_string",
        "original": text,
        "reversed": reversed_text,
        "length": len(text)
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def word_count(text: str) -> str:
    """Count words, characters, and lines in a text.
    
    Args:
        text: The text to analyze
    """
    words = text.split()
    lines = text.split("\n")
    result = {
        "tool": "word_count",
        "characters": len(text),
        "words": len(words),
        "lines": len(lines),
        "non_whitespace_chars": len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def generate_uuid(count: int = 1) -> str:
    """Generate random UUIDs (v4).
    
    Args:
        count: Number of UUIDs to generate (default: 1, max: 10)
    """
    count = min(count, 10)
    uuids = [str(uuid_module.uuid4()) for _ in range(count)]
    result = {
        "tool": "generate_uuid",
        "count": count,
        "uuids": uuids
    }
    return json.dumps(result, indent=2)



def main():
    parser = argparse.ArgumentParser(description="Run MCP Streamable HTTP based server")
    parser.add_argument("--port", type=int, default=8123, help="Localhost port to listen on")
    args = parser.parse_args()

    # Start the server with Streamable HTTP transport
    uvicorn.run(mcp.streamable_http_app, host="localhost", port=args.port)


if __name__ == "__main__":
    main()