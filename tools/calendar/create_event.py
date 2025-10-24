"""Create calendar event tool - Schedule new events."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="calendar",
    description="Create a new calendar event",
    tags=["calendar", "event", "create", "schedule", "meeting"],
    mock=True,
)
def create_event(
    title: Annotated[str, "The event title"],
    date: Annotated[str, "Event date (YYYY-MM-DD format)"],
    time: Annotated[str, "Event time (HH:MM format)"],
    duration_minutes: Annotated[int, "Duration in minutes"] = 60,
    attendees: Annotated[str, "Comma-separated list of attendee emails"] = "",
) -> str:
    """Create a new calendar event.

    This is a mock implementation that simulates creating calendar events.
    In production, this would integrate with Google Calendar, Outlook, etc.

    Args:
        title: Event title/subject
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        duration_minutes: Duration of the event in minutes (default: 60)
        attendees: Comma-separated email addresses of attendees

    Returns:
        Formatted string confirming event creation

    Example:
        >>> create_event("Team Standup", "2025-10-25", "09:00", 30)
        "✅ Event Created Successfully!
        📅 Team Standup
        📆 Date: 2025-10-25 at 09:00
        ⏱️  Duration: 30 minutes
        🔗 Event ID: EVT-12345"
    """
    # Parse and format the datetime
    try:
        event_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = event_date + timedelta(minutes=duration_minutes)
    except ValueError:
        return "❌ Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."

    event_id = f"EVT-{hash(f'{title}{date}{time}') % 100000}"

    result = f"""
✅ **Event Created Successfully!**

📅 **Title:** {title}
📆 **Date:** {event_date.strftime('%A, %B %d, %Y')}
🕐 **Time:** {event_date.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
⏱️  **Duration:** {duration_minutes} minutes
🔗 **Event ID:** {event_id}
    """.strip()

    if attendees:
        attendee_list = attendees.split(",")
        result += f"\n👥 **Attendees ({len(attendee_list)}):**"
        for attendee in attendee_list:
            result += f"\n   • {attendee.strip()}"

    result += f"\n\n📍 **Calendar:** Default"
    result += f"\n🔔 **Reminder:** 15 minutes before"

    return result
