import datetime
from google.adk.tools import ToolContext


async def get_current_datetime(_: str, tool_context: ToolContext):
    """Return the current date and time."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_datetime": now}
