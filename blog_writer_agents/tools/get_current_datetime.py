import datetime
import pytz
from google.adk.tools import ToolContext


async def get_current_datetime(_: str, tool_context: ToolContext):
    """Return the current date and time in JST."""
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
    return {"current_datetime": now}
