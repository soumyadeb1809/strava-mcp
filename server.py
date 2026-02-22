import logging
from mcp.server.fastmcp import FastMCP
from strava_client import StravaClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strava-mcp")

# Initialize MCP Server
mcp = FastMCP("Strava MCP Server")

# Initialize Strava Client
try:
    strava_client = StravaClient()
except Exception as e:
    logger.error(f"Failed to initialize Strava Client: {e}")
    # Continue initialization, as tools might handle errors gracefully

@mcp.tool()
def get_authenticated_athlete() -> str:
    """
    Returns the currently authenticated athlete's profile information.
    Use this to get details about the user's Strava account.
    """
    try:
        profile = strava_client.get_athlete_profile()
        return profile

    except Exception as e:
        return f"Error retrieving athlete profile: {str(e)}"

@mcp.tool()
def get_athlete_stats(athlete_id: int) -> dict | str:
    """
    Returns the activity stats of an athlete.
    Requires the athlete's ID, which can be obtained from get_authenticated_athlete().
    Only includes data from activities set to Everyone visibility.
    """
    try:
        return strava_client.get_athlete_stats(athlete_id)
    except Exception as e:
        return f"Error retrieving athlete stats: {str(e)}"

@mcp.tool()
def get_logged_in_athlete_zones() -> dict | str:
    """
    Returns the authenticated athlete's heart rate and power zones.
    """
    try:
        return strava_client.get_logged_in_athlete_zones()
    except Exception as e:
        return f"Error retrieving athlete zones: {str(e)}"

@mcp.tool()
def list_athlete_activities(before: int = None, after: int = None, page: int = 1) -> list | str:
    """
    Returns the activities of the authenticated athlete.
    'before' and 'after' are epoch timestamps to filter activities.
    'page' (default 1) control pagination.
    """
    try:
        return strava_client.list_athlete_activities(before, after, page)
    except Exception as e:
        return f"Error retrieving activities: {str(e)}"

@mcp.tool()
def get_activity(activity_id: int, include_all_efforts: bool = True) -> dict | str:
    """
    Returns a detailed representation of an activity owned by the authenticated athlete.
    Requires the 'activity_id'. Set 'include_all_efforts' to False to omit segment efforts.
    """
    try:
        return strava_client.get_activity(activity_id, include_all_efforts)
    except Exception as e:
        return f"Error retrieving activity: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting Strava MCP Server...")
    # FastMCP automatically runs on stdio by default through run()
    mcp.run()
