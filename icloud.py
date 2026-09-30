"""Read-only access to my iCloud Calendar."""

import os

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


if __name__ == "__main__":
    principal = get_icloud_account()
    for calendar in principal.calendars():
        print(calendar.get_display_name())
