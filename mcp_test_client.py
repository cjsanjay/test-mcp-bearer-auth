"""MCP Streamable HTTP Client"""
import os
import argparse
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    """MCP Client for interacting with an MCP Streamable HTTP server"""

    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_streamable_http_server(
        self,
        server_url: str,
        headers: Optional[dict[str, str]] = None,
        bearer_token: Optional[str] = None,
    ):
        """Connect to an MCP server running with HTTP Streamable transport."""

        combined_headers: dict[str, str] = dict(headers or {})
        if bearer_token:
            combined_headers.setdefault("Authorization", f"Bearer {bearer_token}")

        self._streams_context = streamablehttp_client(  # pylint: disable=W0201
            url=server_url,
            headers=combined_headers,
        )
        read_stream, write_stream, _ = await self._streams_context.__aenter__()  # pylint: disable=E1101

        self._session_context = ClientSession(read_stream, write_stream)  # pylint: disable=W0201
        self.session: ClientSession = await self._session_context.__aenter__()  # pylint: disable=C2801

        await self.session.initialize()

    async def test_server(self):
        """Test all available tools on the server"""
        
        print("\n" + "=" * 60)
        print("Testing MCP Server Tools")
        print("=" * 60)
        
        # List all available tools
        print("\n1. Listing available tools...")
        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        print(f"✓ Found {len(available_tools)} tools:")
        for tool in available_tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Test 1: get_current_time
        print("\n2. Testing get_current_time...")
        try:
            result = await self.session.call_tool(
                "get_current_time",
                arguments={"timezone": "UTC"}
            )
            print(f"✓ Result: {result.content[0].text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 2: calculate
        print("\n3. Testing calculate (multiply)...")
        try:
            result = await self.session.call_tool(
                "calculate",
                arguments={
                    "operation": "multiply",
                    "a": 15,
                    "b": 7
                }
            )
            print(f"✓ Result: {result.content[0].text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 3: calculate (divide)
        print("\n4. Testing calculate (divide)...")
        try:
            result = await self.session.call_tool(
                "calculate",
                arguments={
                    "operation": "divide",
                    "a": 100,
                    "b": 4
                }
            )
            print(f"✓ Result: {result.content[0].text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: reverse_string
        print("\n5. Testing reverse_string...")
        try:
            result = await self.session.call_tool(
                "reverse_string",
                arguments={"text": "Hello, MCP Server!"}
            )
            print(f"✓ Result: {result.content[0].text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: word_count
        print("\n6. Testing word_count...")
        try:
            result = await self.session.call_tool(
                "word_count",
                arguments={"text": "The quick brown fox jumps over the lazy dog"}
            )
            print(f"✓ Result: {result.content[0].text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: generate_uuid
        print("\n7. Testing generate_uuid...")
        try:
            result = await self.session.call_tool(
                "generate_uuid",
                arguments={"count": 3}
            )
            print(f"✓ Result: {result.content[0].text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:  # pylint: disable=W0125
            await self._streams_context.__aexit__(None, None, None)  # pylint: disable=E1101


async def main():
    """Main function to run the MCP client"""
    parser = argparse.ArgumentParser(description="Run MCP Streamable http based Client")
    parser.add_argument(
        "--mcp-localhost-port", type=int, default=8123, help="Localhost port to bind to"
    )
    parser.add_argument(
        "--bearer-token",
        type=str,
        help="Bearer token used for Authorization header",
    )
    args = parser.parse_args()

    client = MCPClient()

    try:
        await client.connect_to_streamable_http_server(
            f"http://localhost:{args.mcp_localhost_port}/mcp",
            bearer_token="dev-alice-token",
        )
        await client.test_server()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())