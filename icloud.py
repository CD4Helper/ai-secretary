"""Read-only access to my iCloud Calendar."""

import os
from datetime import datetime, timedelta, timezone

import caldav
from dotenv import load_dotenv

load_dotenv()

icloud_password = os.getenv("ICLOUD_APP_PASSWORD")
icloud_username = os.getenv("ICLOUD_USERNAME")
print("Username loaded:", icloud_username is not None)
print("Password loaded:", icloud_password is not None)


def get_icloud_account():
    """Return iCloud account."""
    client = caldav.DAVClient(
        url="https://caldav.icloud.com/",
        username=icloud_username,
        password=icloud_password,
    )
    return client.principal()


def get_icloud_events():
    """Return the next 24 hours of iCloud events as text, one per line."""
    principal = get_icloud_account()
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=1)

    lines = []
    for calendar in principal.calendars():
        events = calendar.search(start=now, end=end, event=True, expand=True)
        for event in events:
            start = event.component.start
            title = event.component.get("summary")

            if isinstance(start, datetime):
                label = start.astimezone().strftime("%a %b %-d, %-I:%M %p")
            else:
                label = start.strftime("%a %b %-d, All day:")
            lines.append(f"{label} {title}")

    if not lines:
        return "Nothing on the calendar in the next 24 hours."
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_icloud_events())
