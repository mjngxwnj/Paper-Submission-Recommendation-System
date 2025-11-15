from datetime import datetime, timedelta, timezone

# Vietnam timezone
VN_TZ = timezone(timedelta(hours=7))


def now() -> datetime:
    """
    Get the current datetime in Vietnam timezone (UTC+7).

    Returns:
        datetime: Current datetime in Vietnam timezone
    """
    return datetime.now(VN_TZ)
