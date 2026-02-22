# Strava MCP Server

A Model Context Protocol (MCP) server that provides an interface to interact with your Strava account. This server allows AI assistants (like Claude, Gemini, etc.) to fetch your profile information, statistics, power/heart rate zones, and activity data.

## Features

- **OAuth 2.0 Authentication Flow**: Seamlessly connects to your Strava account to authorize the API and generate access and refresh tokens.
- **Token Management**: Automatically refreshes expired tokens so you only have to authorize once.
- **Secure Configuration**: Uses `.env` to keep your client secrets and tokens safe.
- **Five Ready-to-use Tools**: 
    - `get_authenticated_athlete`: Retrieves your profile details.
    - `get_athlete_stats`: Gets aggregated stats (like YTD running/cycling totals).
    - `get_logged_in_athlete_zones`: Fetches your personalized heart rate and power zones.
    - `list_athlete_activities`: Retrieves a paginated list of your recent activities.
    - `get_activity`: Fetches complete details (including segment efforts) for a specific activity.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- A Strava Developer Account. 
    1. Go to [https://www.strava.com/settings/api](https://www.strava.com/settings/api).
    2. Create an Application.
    3. Set the "Authorization Callback Domain" to `localhost`.
    4. Note down your `Client ID` and `Client Secret`.

### 2. Installation
Clone the repository, set up a virtual environment, and install the dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Credentials
Create a `.env` file in the root directory and add your `Client ID` and `Client Secret` from the prerequisite step:
```env
STRAVA_CLIENT_ID=<your_client_id>
STRAVA_CLIENT_SECRET=<your_client_secret>
```

### 4. Authorize the App
Before the MCP Server can function, you must authorize it to read your Strava data. Run the setup script:
```bash
python auth.py
```
This will open your browser to a Strava authorization page. Once you approve access, the script will automatically capture the tokens and save them to your `.env` file (`STRAVA_ACCESS_TOKEN` and `STRAVA_REFRESH_TOKEN`).

### 5. Running the MCP Server
Typically, the context provider (Claude Desktop) will run the server, but you can verify it starts correctly with:
```bash
python server.py
```

## Tool Integration

This server can be used by any MCP-compatible client. Below are instructions for popular clients:

### Claude Desktop

To use this server with Claude Desktop, you must add it to your configuration file located at `~/Library/Application Support/Claude/claude_desktop_config.json`. Add the entry inside the `mcpServers` object, pointing to the absolute paths of this project on your machine:

```json
{
  "mcpServers": {
    "strava": {
      "command": "/absolute/path/to/strava-mcp/venv/bin/python",
      "args": [
        "/absolute/path/to/strava-mcp/server.py"
      ]
    }
  }
}
```
*Note: Replace `/absolute/path/to/strava-mcp/` with the actual path to wherever you cloned this repository.* 

Restart Claude Desktop for the tools to appear.

### Gemini CLI

To use this server with `gemini-cli`, you can add it to your configuration file typically located at `~/.config/gemini/config.yaml` or wherever your CLI environment stores MCP server settings.

For example, your configuration might look like this:

```yaml
mcp:
  servers:
    strava:
      command: "/absolute/path/to/strava-mcp/venv/bin/python"
      args:
        - "/absolute/path/to/strava-mcp/server.py"
```
*Note: Replace `/absolute/path/to/strava-mcp/` with the actual path to wherever you cloned this repository.*

Restart or reload your Gemini CLI for the tools to become active.

---

## Connecting to a Deployed Cloud Server

If you have deployed this MCP Server to a cloud provider (such as Render) that supports SSE transport, you can connect your AI assistant directly to the remote URL instead of running the Python script locally.

This requires having the `fastmcp` CLI installed locally in your Python environment.

### Cloud Configuration Example (Claude Desktop)

```json
{
  "mcpServers": {
    "strava": {
      "command": "/absolute/path/to/strava-mcp/venv/bin/fastmcp",
      "args": [
        "run",
        "--no-banner",
        "--log-level",
        "CRITICAL",
        "https://strava-mcp-r7v4.onrender.com/sse"
      ]
    }
  }
}
```
*Note: Replace `/absolute/path/to/strava-mcp/` with the actual path to wherever you cloned this repository.*

## Project Structure
- `server.py`: The FastMCP server initialization and defined tools.
- `strava_client.py`: A helper class that handles HTTP requests to the Strava API and automatically refreshes tokens.
- `auth.py`: A local HTTP server script that handles the initial OAuth 2.0 authorization code flow.
- `.env`: (Ignored by Git) Stores your credentials and active tokens.

## Tools Overview
- **`get_authenticated_athlete()`**: Returns the authenticated athlete's profile.
- **`get_athlete_stats(athlete_id: int)`**: Returns the activity stats for an athlete. *Requires the athlete ID from the previous tool.*
- **`get_logged_in_athlete_zones()`**: Returns heart rate and power zones.
- **`list_athlete_activities(before: int=None, after: int=None, page: int=1)`**: Returns a list of activities. Allows filtering by epoch timestamps.
- **`get_activity(activity_id: int, include_all_efforts: bool=True)`**: Returns a detailed view of a specific activity.
