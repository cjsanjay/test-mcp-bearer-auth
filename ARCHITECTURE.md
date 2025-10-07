# MCP API Auth Server - Architecture

## Overview

This is a Model Context Protocol (MCP) server implementation using the **Streamable HTTP transport**. It demonstrates API key authentication and provides 5 test tools.

## Transport Protocol: Streamable HTTP

The Streamable HTTP transport is one of the official MCP transport protocols. It allows the server to:

1. **Operate as an independent process** that can handle multiple client connections
2. **Use HTTP POST requests** for client-to-server communication (JSON-RPC 2.0)
3. **Optionally use Server-Sent Events (SSE)** for server-to-client notifications and streaming

This is different from:
- **stdio transport**: Single client, process-based communication via stdin/stdout
- **Pure SSE transport**: Only SSE-based communication

## Architecture Components

### 1. HTTP Server (Starlette + Uvicorn)

The server runs as an ASGI application using:
- **Starlette**: Lightweight ASGI framework for routing
- **Uvicorn**: ASGI server for production-ready HTTP serving

### 2. Endpoints

#### `POST /message` (Primary Endpoint)
Handles all MCP protocol messages using JSON-RPC 2.0:

**Supported Methods:**
- `initialize` - Session initialization
- `tools/list` - List available tools
- `tools/call` - Execute a tool
- `ping` - Keepalive

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "calculate",
    "arguments": {...}
  }
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {...}
}
```

#### `GET /sse` (Optional)
Server-Sent Events endpoint for:
- Server-to-client notifications
- Server-initiated requests
- Real-time updates
- Connection keepalive

#### `GET /health`
Health check endpoint (no authentication required)

### 3. Authentication

API key authentication is implemented at two levels:

1. **HTTP Level**: Validates `X-API-Key` header or `api_key` query parameter
2. **Tool Level**: Each tool requires `api_key` in its arguments (demonstration)

### 4. Session Management

- Sessions are tracked in memory using UUIDs
- Each client can maintain its own session
- Multiple concurrent clients are supported

### 5. Tools

Five demonstration tools are implemented:

1. **get_current_time**: Returns current timestamp
2. **calculate**: Basic arithmetic operations
3. **reverse_string**: String reversal
4. **word_count**: Text analysis
5. **generate_uuid**: UUID generation

## Request Flow

```
Client                    Server
  |                         |
  |-- POST /message ------->|
  |   (initialize)          |
  |<----- 200 OK -----------|
  |   (session created)     |
  |                         |
  |-- POST /message ------->|
  |   (tools/list)          |
  |<----- 200 OK -----------|
  |   (tools array)         |
  |                         |
  |-- POST /message ------->|
  |   (tools/call)          |
  |<----- 200 OK -----------|
  |   (tool result)         |
  |                         |
  |-- GET /sse ------------>|
  |<----- SSE stream -------|
  |   (notifications)       |
```

## Key Features

### Multiple Client Support
Unlike stdio transport, this server can handle multiple concurrent clients, each with their own session.

### Stateless HTTP
Each request is independent and authenticated. No persistent connection required for basic operations.

### Optional Streaming
SSE endpoint is optional - clients can use pure HTTP POST if they don't need server notifications.

### JSON-RPC 2.0 Compliance
All messages follow JSON-RPC 2.0 specification with proper error codes:
- `-32601`: Method not found
- `-32603`: Internal error

## Security Considerations

1. **API Key Authentication**: Required for all MCP operations
2. **HTTPS Ready**: Can be deployed behind reverse proxy with TLS
3. **CORS**: Can be configured for web clients
4. **Rate Limiting**: Can be added via middleware
5. **Session Isolation**: Each client has isolated session state

## Deployment Options

### Development
```bash
python -m mcp_api_auth.server
```

### Production
- Deploy behind Nginx/Caddy with HTTPS
- Use environment variables for configuration
- Enable proper logging and monitoring
- Consider rate limiting and DDoS protection

### Docker
Can be containerized with:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["mcp-api-auth-server"]
```

## Comparison with Other Transports

| Feature | Streamable HTTP | stdio | Pure SSE |
|---------|----------------|-------|----------|
| Multiple clients | ✅ Yes | ❌ No | ✅ Yes |
| Network accessible | ✅ Yes | ❌ No | ✅ Yes |
| Bidirectional | ✅ Yes | ✅ Yes | ⚠️ Limited |
| Streaming | ✅ Optional | ✅ Yes | ✅ Yes |
| Stateless | ✅ Yes | ❌ No | ❌ No |
| Load balancing | ✅ Easy | ❌ N/A | ⚠️ Complex |

## Client SDK Support

### Current State

The MCP Python SDK is evolving, and as of now:

- ✅ **stdio transport**: Fully supported
- ✅ **SSE transport**: Supported via `mcp.client.sse.sse_client`
- ⚠️ **Streamable HTTP transport**: May not have dedicated client yet

### Expected Client Usage (When Available)

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async with streamable_http_client(
    url="http://localhost:8000/message",
    headers={"X-API-Key": "your-api-key"}
) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("tool_name", arguments={...})
```

### Current Workaround

For now, clients can:
1. Use raw HTTP POST with `httpx` or `requests` (see `test_client.py`)
2. Use SSE client if server supports it (see `mcp_test_client.py`)
3. Implement custom transport adapter for the MCP SDK

## Future Enhancements

1. **WebSocket Support**: Add WebSocket as alternative to SSE
2. **Authentication**: OAuth2, JWT tokens
3. **Rate Limiting**: Per-client rate limits
4. **Metrics**: Prometheus metrics endpoint
5. **Database**: Persistent session storage
6. **Clustering**: Redis-based session sharing for horizontal scaling
7. **SDK Integration**: Full MCP SDK client support when available
