"""Allow `python -m docsync` to start the MCP stdio server."""
from .server import run

if __name__ == "__main__":
    run()
