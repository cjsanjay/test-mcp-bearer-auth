from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl
import os
import sys
from datetime import datetime

# Read from environment
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-tenant.us.auth0.com")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "https://your-api-identifier")
RESOURCE_SERVER_URL = os.getenv("RESOURCE_SERVER_URL", "https://your-domain.example.com/mcp") # your mcp server deployment url

# JWT verification setup
token_verifier = JWTVerifier(
    jwks_uri=f"https://{AUTH0_DOMAIN}/.well-known/jwks.json",
    issuer=f"https://{AUTH0_DOMAIN}/", # note the trailing slash
    audience=AUTH0_AUDIENCE            # must match your API identifier exactly
)

# Remote OAuth provider for MCP
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl(f"https://{AUTH0_DOMAIN}/")],
    base_url=RESOURCE_SERVER_URL      # usually your /mcp endpoint
)
mcp = FastMCP(name="Protected MCP Server", auth=auth)


@mcp.tool  
def test_str(name: str) -> str:    
    return f"Hello, {name}!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    # Start an HTTP server on port 8000
    mcp.run(transport="http", host="0.0.0.0", port=8000)