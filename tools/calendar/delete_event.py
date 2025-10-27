"""Delete calendar event tool - Remove scheduled events."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool


@tool(
    domain="calendar",
    description="Delete a calendar event by ID or title",
    tags=["calendar", "event", "delete", "remove", "cancel"],
    mock=True,
)
def delete_event(
    event_id: Annotated[str, "The event ID to delete (e.g., EVT-12345)"] = "",
    title: Annotated[str, "Event title to search and delete"] = "",
) -> str:
    """Delete a calendar event by ID or title.

    This is a mock implementation that simulates deleting calendar events.
    In production, this would integrate with Google Calendar, Outlook, etc.

    Args:
        event_id: Unique event identifier (e.g., EVT-12345)
        title: Event title to search for (if event_id not provided)

    Returns:
        Formatted string confirming event deletion

    Example:
        >>> delete_event(event_id="EVT-12345")
        "✅ Event Deleted Successfully!
        🗑️  Event ID: EVT-12345
        📅 Team Standup
        📆 Was scheduled for: Monday, October 25, 2025 at 09:00 AM"
    """
    if not event_id and not title:
        return "❌ **Error:** Please provide either an event_id or title to delete."

    # Mock event data for demonstration
    mock_events = {
        "EVT-12345": {
            "title": "Team Standup",
            "date": "Monday, October 25, 2025",
            "time": "09:00 AM",
            "attendees": ["john@example.com", "sarah@example.com"],
        },
        "EVT-67890": {
            "title": "Project Review",
            "date": "Tuesday, October 26, 2025",
            "time": "02:00 PM",
            "attendees": ["manager@example.com", "team@example.com"],
        },
    }

    # Try to find event by ID
    if event_id:
        event = mock_events.get(event_id)
        if not event:
            # Generate a generic successful deletion for any event ID
            return f"""
✅ **Event Deleted Successfully!**

🗑️  **Event ID:** {event_id}
📅 **Title:** Unknown Event
⏰ **Status:** Removed from calendar

💡 **Note:** Event and all notifications have been cancelled.
            """.strip()

        result = f"""
✅ **Event Deleted Successfully!**

🗑️  **Event ID:** {event_id}
📅 **Title:** {event["title"]}
📆 **Was scheduled for:** {event["date"]} at {event["time"]}
        """.strip()

        if event.get("attendees"):
            result += f"\n👥 **Attendees notified ({len(event['attendees'])}):**"
            for attendee in event["attendees"]:
                result += f"\n   • {attendee}"

        result += "\n\n💡 **Note:** Cancellation emails have been sent to all attendees."

        return result

    # Try to find event by title
    if title:
        # Search for matching events (mock - just match the first one)
        matching_events = [
            (eid, evt) for eid, evt in mock_events.items()
            if title.lower() in evt["title"].lower()
        ]

        if not matching_events:
            # Still return success for mock purposes
            return f"""
✅ **Event Deleted Successfully!**

📅 **Title:** {title}
🗑️  **Status:** Event removed from calendar
⏰ **Deleted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 **Note:** If there were multiple events with this title, only the first occurrence was deleted.
            """.strip()

        # Use the first matching event
        event_id, event = matching_events[0]

        result = f"""
✅ **Event Deleted Successfully!**

🗑️  **Event ID:** {event_id}
📅 **Title:** {event["title"]}
📆 **Was scheduled for:** {event["date"]} at {event["time"]}
        """.strip()

        if event.get("attendees"):
            result += f"\n👥 **Attendees notified ({len(event['attendees'])}):**"
            for attendee in event["attendees"]:
                result += f"\n   • {attendee}"

        if len(matching_events) > 1:
            result += f"\n\n⚠️  **Note:** Found {len(matching_events)} events matching '{title}'. Only the first was deleted."

        result += "\n\n💡 **Note:** Cancellation emails have been sent to all attendees."

        return result


@tool(
    domain="calendar",
    description="Delete multiple calendar events by date range or filter",
    tags=["calendar", "event", "delete", "bulk", "clear", "cleanup"],
    mock=True,
)
def delete_events(
    date_from: Annotated[str, "Start date (YYYY-MM-DD format)"] = "",
    date_to: Annotated[str, "End date (YYYY-MM-DD format)"] = "",
    calendar_name: Annotated[str, "Calendar name to filter by"] = "all",
    confirm: Annotated[bool, "Confirmation required for bulk delete"] = False,
) -> str:
    """Delete multiple calendar events within a date range.

    This is a mock implementation that simulates bulk deleting events.
    In production, this would integrate with Google Calendar, Outlook, etc.

    Args:
        date_from: Start date in YYYY-MM-DD format
        date_to: End date in YYYY-MM-DD format
        calendar_name: Filter by calendar name, or "all" for all calendars
        confirm: Must be True to proceed with bulk deletion

    Returns:
        Formatted string confirming bulk event deletion

    Example:
        >>> delete_events("2025-10-25", "2025-10-30", confirm=True)
        "✅ Deleted 5 events from October 25-30, 2025"
    """
    if not date_from or not date_to:
        return "❌ **Error:** Please provide both date_from and date_to in YYYY-MM-DD format."

    if not confirm:
        return f"""
⚠️  **Confirmation Required**

You are about to delete **all events** from {date_from} to {date_to}{f' in {calendar_name} calendar' if calendar_name != 'all' else ''}.

This action cannot be undone!

To proceed, call this function again with `confirm=True`:
```
delete_events(
    date_from="{date_from}",
    date_to="{date_to}",
    calendar_name="{calendar_name}",
    confirm=True
)
```
        """.strip()

    # Validate date format
    try:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        return "❌ **Error:** Invalid date format. Please use YYYY-MM-DD format."

    if end_date < start_date:
        return "❌ **Error:** End date must be after start date."

    # Mock deletion count
    days_span = (end_date - start_date).days + 1
    # Assume ~2-3 events per day on average
    estimated_events = max(1, days_span * 2)

    result = f"""
✅ **Bulk Delete Completed Successfully!**

📅 **Date Range:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
🗑️  **Events Deleted:** {estimated_events}
📁 **Calendar:** {calendar_name if calendar_name != 'all' else 'All calendars'}
⏰ **Deleted at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 **Breakdown:**
   • Meetings: {estimated_events // 2}
   • Appointments: {estimated_events // 3}
   • Other events: {estimated_events - (estimated_events // 2) - (estimated_events // 3)}

👥 **Notifications sent to all attendees**
    """.strip()

    return result
