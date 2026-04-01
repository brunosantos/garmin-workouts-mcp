# Garmin Workouts MCP Server

The Garmin Workouts Model Context Protocol (MCP) server connects to Garmin Connect APIs and exposes your fitness and health data to AI agents that support the MCP standard. Users can use this server to access your Garmin activities, workouts, and workout templates from AI clients like Claude Desktop or VS Code Copilot, enabling users to query about their activity data, get insights and get AI generated workout plans.

This project is in early development (v0.1) and currently supports read-only access to activities, workouts, and workout templates. 

The source code is a simplified and refactored version of the original Garmin MCP server available at [garmin_mcp](https://github.com/Taxuspt/garmin_mcp). The original mcp solution is still available and maintained, but this forked version is designed to reduce the data access surface area to the AI agent and focus on the core features for creating workout training plans rather than exposing all the data and features of the Garmin Connect API.

Garmin's API is accessed via the [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) library and also the garth 

## Features

- List recent activities with pagination support
- Get detailed activity information
- Access workouts and training plans
- Browse workout templates

## Usage Examples

Once connected in Claude Desktop/VS Code Copilot, you can ask questions like:

### Basic queries:
- "Show me the details of my latest run"
- "Create a workout plan for next week based on my recent activities"
- "When is my next scheduled workout?"
- "Create a workout plan with 30min easy run at conversational pace"
- "Create a workout plan with 5km tempo run at 5:15 min/km pace"
- "Create a workout plan with intervals: 6×400 m @ 4:10–4:20/km, 90s recovery (include 15 min warm-up/cool-down)"

### AI Coach assisted queries:
- "What are some workout templates I can use to improve my 5k time?"
- "Based on my recent activities, what workouts should I do this week to prepare for a half marathon?"
- "Create a workout plan for the next Hackney Half Marathon based on my recent activities, with a goal to run it in under 1h45."
- "Upload a structured 45-minute threshold run workout and schedule it for next Tuesday"
- "Look at my last 4 weeks of running and tell me if I'm overtraining or ready to increase mileage"
- "How much time did I spend in each heart rate zone during my run last Sunday?"
- "Compare my pace and HR across my last 5 runs — am I getting fitter?"
- "I have a race in 6 weeks — build me a progressive weekly workout schedule and add each session to my calendar"

### Tool Coverage

This MCP server implements tools for the following domains:

- ✅ **Activity Management** — 13 read-only tools 🏃
  - 📋 `get_activities` — list activities with pagination support (newest first)
  - 📅 `get_activities_by_date` — list activities between two dates, optionally filtered by type
  - 📅 `get_activities_fordate` — list activities recorded on a specific date
  - 🔍 `get_activity` — get detailed information for a single activity
  - 📊 `get_activity_splits` — get lap/split data for an activity
  - 📊 `get_activity_typed_splits` — get typed splits (run/walk/etc.) for an activity
  - 📊 `get_activity_split_summaries` — get split summary statistics for an activity
  - 🌤️ `get_activity_weather` — get weather conditions recorded during an activity
  - ❤️ `get_activity_hr_in_timezones` — get heart rate distribution across HR zones for an activity
  - 👟 `get_activity_gear` — get gear (shoes, bike, etc.) used for an activity
  - 🏋️ `get_activity_exercise_sets` — get exercise sets for strength training activities
  - 🏷️ `get_activity_types` — list all activity types supported by Garmin Connect
  - 🔢 `count_activities` — get the total number of activities in the account

- ✅ **Workouts** — 11 read/write tools 💪
  - 📋 `get_workouts` — list all workouts in the Garmin Connect workout library
  - 🔍 `get_workout_by_id` — get full details for a workout by numeric ID or UUID
  - ⬆️ `upload_workout` — create a new workout from structured JSON data
  - ⬆️ `upload_workouts` — create multiple workouts from structured JSON data in a single call
  - 🗑️ `delete_workout` — permanently delete a workout from the library
  - 🗑️ `delete_workouts` — permanently delete multiple workouts from the library in a single call
  - 📅 `schedule_workout` — schedule a workout to a specific calendar date
  - 📅 `schedule_workouts` — schedule multiple workouts (or upload-and-schedule inline) in a single call
  - 📅 `get_scheduled_workouts` — list workouts scheduled on the calendar between two dates
  - 🗓️ `get_training_plan_workouts` — get Garmin Coach / training plan workouts for a given week
  - ⬇️ `download_workout` — download a workout in FIT file format

- ✅ **Workout Templates** — 5 MCP resources 📂
  - 🏃 `workout://templates/simple-run` — basic warmup / run / cooldown structure
  - ⚡ `workout://templates/interval-running` — interval training with repeat groups (6×400 m)
  - 🎯 `workout://templates/tempo-run` — tempo run targeting a heart rate zone
  - 🏋️ `workout://templates/strength-circuit` — strength training circuit with repeat groups
  - 📖 `workout://reference/structure` — complete JSON structure reference for building workouts

### OAuth Scope Notes

This server uses the [garminconnect](https://github.com/cyberjunky/python-garminconnect) and [garth](https://github.com/matin/garth) libraries for authentication, which relies on Garmin's SSO OAuth tokens. The access token grants access to the Garmin Connect API with read and write permissions. The token scopes are not user-configurable in the auth library (`garth`). For that reason least-privilege access has been applied by design at the MCP Tool level as follows:

- **Activity Management** — read-only operations to list and retrieve activities. No write operations are implemented for activities (e.g. creating, updating, or deleting activities). No access to user profile or other sensitive data like GPS coordinates.
- **Workouts** — read and write operations required (listing, uploading, scheduling, deleting workouts)

## Setup

### Security considerations
> [!NOTE] 
> [Garmin’s official API program](https://developer.garmin.com/gc-developer-program/program-faq/) is available for Enterprise use only and not for individual developers to access. I tried to get access to the official API but was denied because I'm doing this as a Open Source individual project. For that reason I turner to other existing open source libraries. The `garminconnect` library uses reverse-engineered API endpoints and relies on OAuth tokens obtained through the Garmin Connect web/mobile login flow. The `garmin-mcp-auth` tool is a workaround to obtain these tokens for use with the MCP server, but it is not an official or long-term solution.

The Garmin Workouts MCP depends on the [Garmin connect library](https://github.com/cyberjunky/python-garminconnect) and that uses the [Garth library](https://github.com/matin/garth) for authentication, which relies on long lived OAuth tokens.
The Garth library uses Garmin Connect’s mobile-app SSO flow to obtain and persist long-lived (one year) session tokens, which python-garminconnect (API Wrapper) then uses to call Garmin Connect API endpoints.
The `garmin-mcp-auth` tool is a one-time setup utility that prompts you for your Garmin Connect credentials and MFA code (if enabled) to obtain these tokens. The tokens are then saved locally and used by the MCP server for authentication when making API requests to Garmin Connect.

The secret management in this solution can be considered insecure specially the use of long lived OAuth access tokens. We are working on alternatives such as short lived tokens with automatic refresh or integration with external secret managers or keyvaults. In the meantime, you must pre-authenticate to obtain the necessary tokens for the server to function. Use this tool at your own discretion and be aware of the security implications of storing credentials and tokens on your machine. However the scopes of the MCP tools are limited to read-only access for activities and read-write access for workouts, which minimizes potential risks.

#### Prerequisites

- Python 3.12+
- Garmin Connect account
- MFA may be required if enabled on your account

#### Step 1: Pre-authenticate (One-time)
Before adding to Claude Desktop or VS Code Copilot, authenticate once in your terminal:

```bash

# Install and run authentication tool
uvx --python 3.12 --from git+https://github.com/brunosantos/garmin-workouts-mcp garmin-mcp-auth

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

**Note:** This will create a local file at `~/.garminconnect` with your Garmin Connect long lived tokens (one year). The MCP server will read from this file to authenticate API requests. These tokens will have a one year lifespan. 


> [!WARNING]  
> Here be dragons 🐉. 
> Long Lived Tokens are a security risk and against OAuth's best practices, but is a limitation of the underlying `garminconnect` library. Use with caution and be aware of the security implications.
> For this reason I've restricted the scope of the MCP server to only the necessary API endpoints (read-only for activities and workout templates, read-write for workouts) to minimize potential risks.
> I'm working on an alternative using short lived tokens with automatic refresh.

### Usage with Claude Desktop
#### Step 2: Configure Claude Desktop

> **Prerequisite:** Complete [Step 1: Pre-authenticate](#step-1-pre-authenticate-one-time) before configuring Claude Desktop.

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
        "git+https://github.com/brunosantos/garmin-workouts-mcp",
        "garmin-workouts-mcp"
      ]
    }
  }
}
```

**Important:** No `GARMIN_EMAIL` or `GARMIN_PASSWORD` needed in config! The server uses your saved tokens.

#### Step 3: Restart Claude Desktop
Your Garmin data is now available in Claude Desktop !

---

### Usage with VS Code

> **Prerequisite:** Complete [Step 1: Pre-authenticate](#step-1-pre-authenticate-one-time) before configuring VS Code.

For quick installation, use one of the one-click install buttons below:

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=garmin-workouts&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--python%22%2C%223.12%22%2C%22--from%22%2C%22git%2Bhttps%3A//github.com/brunosantos/garmin-workouts-mcp%22%2C%22garmin-workouts-mcp%22%5D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=garmin-workouts&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--python%22%2C%223.12%22%2C%22--from%22%2C%22git%2Bhttps%3A//github.com/brunosantos/garmin_workouts_mcp%22%2C%22garmin-workouts-mcp%22%5D%7D&quality=insiders)

For manual installation, you can configure the MCP server using one of these methods:

**Method 1: User Configuration (Recommended)** Add the configuration to your user-level MCP configuration file. Open the Command Palette (`Ctrl + Shift + P`) and run `MCP: Open User Configuration`. This will open your user `mcp.json` file where you can add the server configuration.

**Method 2: Workspace Configuration** Alternatively, you can add the configuration to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> For more details about MCP configuration in VS Code, see the [official VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).

```json
{
  "servers": {
    "garmin-workouts": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "git+https://github.com/brunosantos/garmin-workouts-mcp",
        "garmin-workouts-mcp"
      ]
    }
  }
}
```

**Important:** No `GARMIN_EMAIL` or `GARMIN_PASSWORD` needed in config! The server uses your saved tokens from the pre-authentication step.

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
        "<full path to your local repository>/garmin-workouts-mcp",
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

- **Integration tests** (49 tests): Test all MCP tools using FastMCP integration with mocked Garmin API responses
- **End-to-end tests** (4 tests): Test with real MCP server and Garmin API (requires valid credentials)