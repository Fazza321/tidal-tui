from datetime import datetime, timezone


# return iso datetime
def now_iso():
    return datetime.now(timezone.utc).isoformat()
