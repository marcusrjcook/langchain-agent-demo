import math
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Supports standard math operations and functions like sqrt, pow, sin, cos, log."""
    try:
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed["abs"] = abs
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


@tool
def get_current_datetime(timezone: str = "UTC") -> str:
    """Get the current date and time. Optionally specify a timezone (e.g. 'America/New_York', 'US/Eastern', 'UTC')."""
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime(f"%Y-%m-%d %H:%M:%S %Z ({timezone})")
    except Exception:
        now = datetime.utcnow()
        return now.strftime("%Y-%m-%d %H:%M:%S UTC")
