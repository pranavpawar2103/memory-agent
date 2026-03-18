import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def list_events(max_results: int = 5) -> str:
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        return "No upcoming events found."
    output = ""
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        output += f"- {e['summary']} at {start}\n"
    return output

def create_event(title: str, date: str, time: str = "10:00", duration_hours: int = 1) -> str:
    service = get_calendar_service()
    start_dt = f"{date}T{time}:00"
    end_dt = f"{date}T{str(int(time[:2]) + duration_hours).zfill(2)}{time[2:]}:00"
    event = {
        "summary": title,
        "start": {"dateTime": start_dt, "timeZone": "America/Toronto"},
        "end": {"dateTime": end_dt, "timeZone": "America/Toronto"},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"Event created: {created.get('summary')} — {created.get('htmlLink')}"