# MCP API Auth Server

A test Model Context Protocol (MCP) server with API key authentication and 5 demonstration tools. Uses **Streamable HTTP transport** with JSON-RPC over HTTP POST/GET.

## Features

- **Streamable HTTP Transport**: JSON-RPC over HTTP POST requests with optional SSE for server notifications
- **API Key Authentication**: All requests require a valid API key
- **Multiple Client Support**: Can handle multiple concurrent client connections
- **5 Test Tools**:
  1. `get_current_time` - Get current date and time with timezone support
  2. `calculate` - Perform basic arithmetic operations (add, subtract, multiply, divide)
  3. `reverse_string` - Reverse any text string
  4. `word_count` - Count words, characters, and lines in text
  5. `generate_uuid` - Generate random UUIDs (v4)

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /Users/sanjay23/experiments/mcp-servers/mcp-api-auth
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

## Configuration

1. **Set up your API key**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** and configure:
   ```
   MCP_API_KEY=your-secret-api-key-here
   MCP_SERVER_HOST=0.0.0.0
   MCP_SERVER_PORT=8000
   ```

   > **Note**: The default API key is `test-api-key-12345` for testing purposes.

## Running the Server

The server will start an HTTP server with SSE streaming on the configured port (default: 8000).

### Method 1: Using the installed script
```bash
mcp-api-auth-server
```

### Method 2: Using Python module
```bash
python -m mcp_api_auth.server
```

### Method 3: Direct execution
```bash
python mcp_api_auth/server.py
```

Once started, you'll see:
```
============================================================
Starting MCP API Auth Server (Streamable HTTP)
============================================================
API Key configured: test-api...
Server URL: http://0.0.0.0:8000

Endpoints:
  POST /message - Main MCP endpoint (JSON-RPC over HTTP)
  GET  /sse     - SSE stream for server notifications (optional)
  GET  /health  - Health check endpoint

Authentication: X-API-Key header or api_key query parameter
============================================================
```

## Server Endpoints

### `POST /message` (Main MCP Endpoint)
The primary endpoint for all MCP communication using JSON-RPC 2.0 protocol.

**Supported Methods:**
- `initialize` - Initialize a new session
- `tools/list` - List all available tools
- `tools/call` - Execute a tool
- `ping` - Keepalive ping

### `GET /sse` (Optional)
SSE streaming endpoint for server-to-client notifications and requests. Allows the server to push messages to connected clients.

### `GET /health`
Health check endpoint (no authentication required)

## Using the Tools

All tools require an `api_key` parameter for authentication. Here are examples of each tool:

### 1. Get Current Time
```json
{
  "name": "get_current_time",
  "arguments": {
    "api_key": "test-api-key-12345",
    "timezone": "UTC"
  }
}
```

**Response**:
```json
{
  "tool": "get_current_time",
  "timestamp": "2025-10-07T13:29:38.123456",
  "timezone": "UTC",
  "formatted": "2025-10-07 13:29:38",
  "unix_timestamp": 1728298778
}
```

### 2. Calculate
```json
{
  "name": "calculate",
  "arguments": {
    "api_key": "test-api-key-12345",
    "operation": "multiply",
    "a": 15,
    "b": 7
  }
}
```

**Response**:
```json
{
  "tool": "calculate",
  "operation": "multiply",
  "operands": {"a": 15, "b": 7},
  "result": 105
}
```

### 3. Reverse String
```json
{
  "name": "reverse_string",
  "arguments": {
    "api_key": "test-api-key-12345",
    "text": "Hello, World!"
  }
}
```

**Response**:
```json
{
  "tool": "reverse_string",
  "original": "Hello, World!",
  "reversed": "!dlroW ,olleH",
  "length": 13
}
```

### 4. Word Count
```json
{
  "name": "word_count",
  "arguments": {
    "api_key": "test-api-key-12345",
    "text": "The quick brown fox\njumps over the lazy dog"
  }
}
```

**Response**:
```json
{
  "tool": "word_count",
  "characters": 44,
  "words": 9,
  "lines": 2,
  "non_whitespace_chars": 35
}
```

### 5. Generate UUID
```json
{
  "name": "generate_uuid",
  "arguments": {
    "api_key": "test-api-key-12345",
    "count": 3
  }
}
```

**Response**:
```json
{
  "tool": "generate_uuid",
  "count": 3,
  "uuids": [
    "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "f6e5d4c3-b2a1-4098-7654-321fedcba098",
    "12345678-90ab-4cde-f012-3456789abcde"
  ]
}
```

## Authentication Errors

If you provide an invalid or missing API key, you'll receive an error response:

```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

## Testing the Server

### Quick Test with Test Clients

Two test client scripts are included:

#### 1. Raw HTTP Client (Recommended for testing)
```bash
# Make sure the server is running first
python test_client.py
```

This uses `httpx` to make raw HTTP POST requests, demonstrating the JSON-RPC protocol directly.

#### 2. MCP SDK Client (When available)
```bash
python mcp_test_client.py
```

This demonstrates how to use the official MCP Python SDK's HTTP transport client. **Note:** As of now, the MCP SDK's `streamable_http_client` may not be fully available. The script shows the expected usage pattern and falls back to explaining the limitation.

### Manual Testing with cURL

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "server": "mcp-api-auth-server",
  "version": "0.1.0",
  "transport": "Streamable HTTP",
  "endpoints": {
    "message": "/message (POST)",
    "sse": "/sse (GET, optional)",
    "health": "/health (GET)"
  }
}
```

### 2. Initialize Session
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

### 3. List Available Tools
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

### 4. Call a Tool
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "calculate",
      "arguments": {
        "api_key": "test-api-key-12345",
        "operation": "multiply",
        "a": 15,
        "b": 7
      }
    }
  }'
```

### 5. Connect to SSE Stream (Optional)
```bash
curl -H "X-API-Key: test-api-key-12345" http://localhost:8000/sse
```

Or with query parameter:
```bash
curl http://localhost:8000/sse?api_key=test-api-key-12345
```

## MCP Client Configuration

### Using HTTP Transport

Configure your MCP client to use the Streamable HTTP transport:

```
Base URL: http://localhost:8000
Message Endpoint: POST /message
SSE Endpoint: GET /sse (optional)
Authentication: X-API-Key header with value "test-api-key-12345"
```

### Programmatic Access (Python)

```python
import httpx
import json

# Base configuration
base_url = "http://localhost:8000"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "test-api-key-12345"
}

async with httpx.AsyncClient() as client:
    # Initialize
    response = await client.post(
        f"{base_url}/message",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "my-client", "version": "1.0.0"}
            }
        }
    )
    print(response.json())
    
    # List tools
    response = await client.post(
        f"{base_url}/message",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
    )
    print(response.json())
    
    # Call a tool
    response = await client.post(
        f"{base_url}/message",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_current_time",
                "arguments": {
                    "api_key": "test-api-key-12345",
                    "timezone": "UTC"
                }
            }
        }
    )
    print(response.json())
```

## Development

### Project Structure
```
mcp-api-auth/
├── mcp_api_auth/
│   ├── __init__.py
│   └── server.py          # Main server implementation
├── test_client.py         # Test client for demonstration
├── pyproject.toml         # Project metadata and dependencies
├── requirements.txt       # Alternative dependency file
├── .env.example           # Example environment configuration
├── .gitignore
└── README.md
```

### Dependencies
- `mcp>=0.1.0` - Model Context Protocol SDK
- `python-dotenv>=1.0.1` - Environment variable management
- `pydantic>=2.7.0` - Data validation
- `starlette>=0.37.0` - ASGI framework
- `sse-starlette>=2.0.0` - Server-Sent Events support
- `httpx>=0.27.0` - HTTP client
- `uvicorn>=0.30.0` - ASGI server

## Security Notes

- **Never commit your `.env` file** with real API keys to version control
- Use strong, randomly generated API keys in production
- The API key is validated via `X-API-Key` header or query parameter
- Consider using HTTPS in production with proper TLS certificates
- For production, consider OAuth2 or JWT-based authentication

## License

MIT License - Feel free to use and modify as needed.
