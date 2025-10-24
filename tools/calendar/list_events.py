"""List calendar events tool - View scheduled events."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="calendar",
    description="List upcoming calendar events",
    tags=["calendar", "event", "list", "schedule", "agenda"],
    mock=True,
)
def list_events(
    days_ahead: Annotated[int, "Number of days to look ahead"] = 7,
    calendar_name: Annotated[str, "Calendar name to filter by"] = "all",
) -> str:
    """List upcoming calendar events.

    This is a mock implementation with sample event data.
    In production, this would fetch real calendar data from APIs.

    Args:
        days_ahead: Number of days to look ahead (default: 7)
        calendar_name: Filter by calendar name, or "all" for all calendars

    Returns:
        Formatted string with upcoming events

    Example:
        >>> list_events(days_ahead=3)
        "📅 **Your Upcoming Events (Next 3 Days)**

        Tomorrow, October 25, 2025:
        1. 🕐 09:00 - 09:30 | Team Standup
           👥 5 attendees
        ..."
    """
    # Mock event data
    sample_events = [
        {
            "title": "Team Standup",
            "date": datetime.now() + timedelta(days=1),
            "time": "09:00",
            "duration": 30,
            "attendees": 5,
            "calendar": "Work",
            "type": "meeting"
        },
        {
            "title": "Project Review with Stakeholders",
            "date": datetime.now() + timedelta(days=1),
            "time": "14:00",
            "duration": 60,
            "attendees": 8,
            "calendar": "Work",
            "type": "meeting"
        },
        {
            "title": "Dentist Appointment",
            "date": datetime.now() + timedelta(days=2),
            "time": "10:30",
            "duration": 60,
            "attendees": 1,
            "calendar": "Personal",
            "type": "appointment"
        },
        {
            "title": "Coffee with Sarah",
            "date": datetime.now() + timedelta(days=3),
            "time": "15:00",
            "duration": 45,
            "attendees": 2,
            "calendar": "Personal",
            "type": "social"
        },
        {
            "title": "Quarterly Planning Meeting",
            "date": datetime.now() + timedelta(days=5),
            "time": "10:00",
            "duration": 120,
            "attendees": 12,
            "calendar": "Work",
            "type": "meeting"
        },
    ]

    # Filter by days ahead
    cutoff_date = datetime.now() + timedelta(days=days_ahead)
    filtered_events = [e for e in sample_events if e["date"] <= cutoff_date]

    # Filter by calendar
    if calendar_name.lower() != "all":
        filtered_events = [e for e in filtered_events if e["calendar"].lower() == calendar_name.lower()]

    if not filtered_events:
        return f"📭 **No events found** in the next {days_ahead} days{f' for {calendar_name} calendar' if calendar_name != 'all' else ''}."

    # Build response
    header = f"📅 **Your Upcoming Events (Next {days_ahead} Days)**"
    if calendar_name != "all":
        header += f" - {calendar_name} Calendar"

    result = [header + "\n"]

    # Group events by date
    events_by_date = {}
    for event in filtered_events:
        date_key = event["date"].strftime("%Y-%m-%d")
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    # Format events
    for date_key in sorted(events_by_date.keys()):
        events = events_by_date[date_key]
        event_date = events[0]["date"]

        # Date header
        if event_date.date() == datetime.now().date():
            day_label = "Today"
        elif event_date.date() == (datetime.now() + timedelta(days=1)).date():
            day_label = "Tomorrow"
        else:
            day_label = event_date.strftime("%A")

        result.append(f"**{day_label}, {event_date.strftime('%B %d, %Y')}:**")

        # Events for this date
        for i, event in enumerate(events, 1):
            end_time = datetime.strptime(event["time"], "%H:%M") + timedelta(minutes=event["duration"])

            # Event type icon
            icon = "🤝" if event["type"] == "meeting" else "📍" if event["type"] == "appointment" else "☕"

            result.append(f"{i}. {icon} **{event['time']} - {end_time.strftime('%H:%M')}** | {event['title']}")
            result.append(f"   👥 {event['attendees']} {'attendee' if event['attendees'] == 1 else 'attendees'} • 📁 {event['calendar']}")

        result.append("")

    # Add summary
    total_events = len(filtered_events)
    total_hours = sum(e["duration"] for e in filtered_events) / 60
    result.append(f"📊 **Summary:** {total_events} events • {total_hours:.1f} hours scheduled")

    return "\n".join(result)
