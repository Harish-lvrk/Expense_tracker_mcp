import os
from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.server import create_proxy
from fastmcp.client.auth import BearerAuth

# Load token from .env file
load_dotenv()
TOKEN = os.environ.get("FASTMCP_TOKEN", "")

# Create a proxy to your remote FastMCP Cloud server with auth
mcp = create_proxy(
    Client(
        "https://scientific-gold-iguana.fastmcp.app/mcp",
        auth=BearerAuth(TOKEN)
    )
)

if __name__ == "__main__":
    # This runs via STDIO, which Claude Desktop can connect to
    mcp.run()