"""
UserFriendlyTime by Rapptz
Source:
https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/time.py
"""
# yeah :pensivewobble: but the method down is used and i cba to change it

from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta


def human_timedelta(dt, *, source=None):
    now = source or datetime.now(timezone.utc)
    if dt > now:
        delta = relativedelta(dt, now)
        suffix = ""
    else:
        delta = relativedelta(now, dt)
        suffix = " ago"

    if delta.microseconds and delta.seconds:
        delta = delta + relativedelta(seconds=+1)

    attrs = ["years", "months", "days", "hours", "minutes", "seconds"]

    output = []
    for attr in attrs:
        elem = getattr(delta, attr)
        if not elem:
            continue

        if elem > 1:
            output.append(f"{elem} {attr}")
        else:
            output.append(f"{elem} {attr[:-1]}")

    if not output:
        return "now"
    if len(output) == 1:
        return output[0] + suffix
    if len(output) == 2:
        return f"{output[0]} and {output[1]}{suffix}"
    return f"{output[0]}, {output[1]} and {output[2]}{suffix}"
