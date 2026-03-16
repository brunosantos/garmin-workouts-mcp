# Garmin MCP Server

This Model Context Protocol (MCP) server connects to Garmin Connect and exposes your fitness and health data to AI agents that support the MCP standard. You can use this server to access your Garmin activities, workouts, and workout templates from AI agents like Claude, enabling you to ask questions about your fitness data and get insights.

This project is in early development (v0.1) and currently supports read-only access to activities, workouts, and workout templates. 

The source code is a simplified and refactored version of the original Garmin MCP server available at [garmin_mcp](https://github.com/Taxuspt/garmin_mcp). The original server is still available and maintained, but this new version is designed to reduce the data access surface area and focus on core features for creating workout training plans.

Garmin's API is accessed via the [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) library.

## Features

- List recent activities with pagination support
- Get detailed activity information
- Access workouts and training plans
- Browse workout templates

### Tool Coverage

This MCP server implements tools for the following domains:

- ✅ Activity Management (14 tools)
- ✅ Workouts (8 tools)
- ✅ Workout Templates (MCP resources)

### OAuth Scope Notes

This server uses the `garminconnect` / `garth` library for authentication, which relies on
Garmin's SSO OAuth tokens. The token grants access to the Garmin Connect API — scopes are
not user-configurable in the underlying library, but least-privilege access has been applied
by design:

- **Activity Management** — read-only operations (list and retrieve activities)
- **Workout Templates** — read-only access (browse built-in templates as MCP resources)
- **Workouts** — read and write operations required (listing, uploading, scheduling, deleting workouts)

## Setup

### Quick Start 
TODO

#### Prerequisites

- Python 3.12+
- Garmin Connect account
- MFA may be required if enabled on your account

### Security considerations
the secret management can be considered insecure specially the use of long lived OAuth access tokens. We are working on alternatives such as short lived tokens with automatic refresh, or integration with external secret managers. In the meantime, you must pre-authenticate to obtain the necessary tokens for the server to function. Use this tool at your own discretion and be aware of the security implications of storing credentials and tokens on your machine. However the scopes of the tokens are limited to read-only access for activities and workout templates, and read-write access for workouts, which minimizes potential risks.

#### Step 1: Pre-authenticate (One-time)
Before adding to GitHub Copilot on VSCode, authenticate once in your terminal:

```bash

# Install and run authentication tool
uvx --python 3.12 --from git+https://github.com/brunosantos/garmin_mcp garmin-mcp-auth

# You'll be prompted for:
# - Email (or set GARMIN_EMAIL env var)
# - Password (or set GARMIN_PASSWORD env var)
# - MFA code (if enabled on your account)

# OAuth tokens will be saved to ~/.garminconnect
```

You can verify your credentials at any time with
```bash
uv run garmin-mcp-auth --verify
```

**Note:** You can also set credentials via environment variables:
```bash
GARMIN_EMAIL=your@email.com GARMIN_PASSWORD=secret garmin-mcp-auth
```

If you don't have MFA enabled you can also skip `garmin-mcp-auth` and pass `GARMIN_EMAIL` and `GARMIN_PASSWORD` as env variables directly to Claude Desktop (or other MCP client, if supported), see below for an example.

#### Step 2: Configure Claude Desktop

Add to your Claude Desktop MCP settings **WITHOUT** credentials:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "garmin-workouts": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "git+https://github.com/brunosantos/garmin_workouts_mcp",
        "garmin-workouts-mcp"
      ]
    }
  }
}
```

**Important:** No `GARMIN_EMAIL` or `GARMIN_PASSWORD` needed in config! The server uses your saved tokens.

#### Step 3: Restart VSCode
#TODO replace refs to Claude to Copilot...
Your Garmin data is now available in VSCode Copilot!

---

### Development Setup

#### Directly from your local copy of the repository:

1. Add this server configuration:

```
{
  "mcpServers": {
    "garmin-workouts-local": {
      "command": "uv",
      "args": [
        "--directory",
        "<full path to your local repository>/garmin_workouts_mcp",
        "run",
        "garmin-workouts-mcp"
      ]
    }
  }
}
```

## Running the Server

### Testing the server locally with MCP Inspector

The Inspector runs directly through npx without requiring installation. Run from the project root:

```bash
npx @modelcontextprotocol/inspector uv run garmin--workouts-mcp
```

You'll be able to inspect and test the tools.


## Usage Examples

Once connected in Claude, you can ask questions like:

- "Show me the details of my latest run"
- "Create a workout plan for next week based on my recent activities"

### Login Issues

If you encounter login issues:

1. Verify your credentials are correct
2. Check if Garmin Connect requires additional verification
3. Ensure the garminconnect package is up to date

## Testing

This project includes comprehensive tests for all MCP tools. **All tests are currently passing (100%)**.

### Running Tests

```bash
# Run all integration tests (default - uses mocked Garmin API)
uv run pytest tests/integration/

# Run tests with verbose output
uv run pytest tests/integration/ -v

# Run a specific test module
uv run pytest tests/integration/test_activity_management_tools.py -v

# Run end-to-end tests (requires real Garmin credentials)
uv run pytest tests/e2e/ -m e2e -v
```

### Test Structure

- **Integration tests** (18 tests): Test all MCP tools using FastMCP integration with mocked Garmin API responses
- **End-to-end tests** (4 tests): Test with real MCP server and Garmin API (requires valid credentials)