from datetime import datetime, timedelta, timezone

# Vietnam timezone
VN_TZ = timezone(timedelta(hours=7))

def today() -> datetime:
    """
    Get the current date in Vietnam timezone (UTC+7).

    Returns:
        date: Current date in Vietnam timezone
    """
    return datetime.now(VN_TZ)
