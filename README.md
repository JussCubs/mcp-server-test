# Vector GraphQL MCP Server

This MCP server provides tools for querying the Vector GraphQL API:

- `fetch_leaderboard`: Get Vector leaderboard data
- `fetch_profile`: Get detailed trader profile data
- `fetch_token_data`: Get trending Solana tokens
- `fetch_token_broadcasts`: Get broadcasts for a specific token

## Setup

```bash
# Clone the repository
git clone https://github.com/JussCubs/mcp-server-test.git
cd mcp-server-test

# Install dependencies with uv
uv add "mcp[cli]" httpx
```

If you don't have uv installed, you can install it following the instructions at [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv).

Alternatively, you can use pip:
```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run in development mode with the MCP Inspector
uv run mcp dev vector_server.py

# OR if you're using pip
mcp dev vector_server.py

# Install in Claude Desktop
uv run mcp install vector_server.py

# OR if you're using pip
mcp install vector_server.py
```

## Troubleshooting

If you see a warning like `The package 'mcp==X.X.X' does not have an extra named 'cli'`, you may need to install the CLI tools separately:

```bash
pip install mcp httpx "click>=8.0" "rich>=10.0" "typer>=0.9.0"
```

## Tool Documentation

### fetch_leaderboard

Fetches Vector leaderboard data:
- `leaderboard_type`: The type of leaderboard (default: 'PNL_WIN')

### fetch_profile

Fetches detailed profile data for a Vector trader:
- `username`: Vector username to fetch

### fetch_token_data

Fetches trending Solana tokens from Vector.
This tool has no parameters and returns trending tokens with 5-minute broadcast activity.

### fetch_token_broadcasts

Fetches broadcasts for a specific token:
- `token_id`: Vector token ID 