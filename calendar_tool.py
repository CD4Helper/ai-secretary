"""Read-only access to my Google Calendar."""

import os
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar():
    """Return a ready-to-use Google Calendar connection."""
    creds = None
    # token.json holds the saved login; it's created on first authorization
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def get_today_events():
    """Return today's calendar events as text, one per line."""
    service = get_calendar()
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=1)
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = result.get("items", [])
    lines = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        start_time = datetime.fromisoformat(start)

        # Check whether it's an all-day event
        if "dateTime" in event["start"]:
            # Timed event: show the time
            label = start_time.strftime("%a %b %-d, %-I:%M %p")
        else:
            # All-day event: there is no time to show
            label = start_time.strftime("%a %b %-d, All day:")
        lines.append(f"{label} {event['summary']}")

    if not lines:
        return "Nothing on the calendar in the next 24 hours."
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_today_events())
