import datetime
from zoneinfo import ZoneInfo

import pytest

# Import the function directly from its module, not from the main mcp file.
from tools.datetime import current_datetime

# By importing directly, we get the original async function, so the
# `getattr(..., "__wrapped__")` trick is no longer needed.


@pytest.mark.asyncio
async def test_current_datetime_utc():
    """UTC must yield a timezone-aware ISO-8601 string with zero offset."""
    ts = await current_datetime("UTC")
    dt = datetime.datetime.fromisoformat(ts)
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == datetime.timedelta(0)


@pytest.mark.asyncio
async def test_current_datetime_madrid():
    """Europe/Madrid offset should match ZoneInfo for the same instant."""
    ts = await current_datetime("Europe/Madrid")
    dt = datetime.datetime.fromisoformat(ts)
    expected_offset = ZoneInfo("Europe/Madrid").utcoffset(dt)
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == expected_offset


@pytest.mark.asyncio
async def test_current_datetime_invalid():
    """Invalid timezone must trigger the fallback message."""
    ts = await current_datetime("Invalid/Zone")
    assert "Invalid timezone" in ts