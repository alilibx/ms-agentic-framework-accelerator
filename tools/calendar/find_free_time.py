"""Find free time tool - Find available time slots."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="calendar",
    description="Find available time slots in the calendar",
    tags=["calendar", "availability", "free", "schedule", "time"],
    mock=True,
)
def find_free_time(
    date: Annotated[str, "Date to check (YYYY-MM-DD format, or 'today'/'tomorrow')"],
    duration_minutes: Annotated[int, "Required duration in minutes"] = 60,
    preferred_time: Annotated[str, "Preferred time range: 'morning', 'afternoon', 'evening', or 'any'"] = "any",
) -> str:
    """Find available time slots in the calendar.

    This is a mock implementation that simulates finding free time.
    In production, this would analyze real calendar data.

    Args:
        date: Date to check (YYYY-MM-DD, 'today', or 'tomorrow')
        duration_minutes: Required duration in minutes
        preferred_time: Time preference - 'morning', 'afternoon', 'evening', or 'any'

    Returns:
        Formatted string with available time slots

    Example:
        >>> find_free_time("2025-10-25", 60, "morning")
        "🕐 **Available Time Slots**
        Date: Friday, October 25, 2025
        Duration needed: 60 minutes

        Morning slots:
        ✅ 08:00 - 09:00 (1 hour)
        ✅ 09:30 - 10:30 (1 hour)
        ..."
    """
    # Parse date
    if date.lower() == "today":
        check_date = datetime.now()
    elif date.lower() == "tomorrow":
        check_date = datetime.now() + timedelta(days=1)
    else:
        try:
            check_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "❌ Invalid date format. Use YYYY-MM-DD, 'today', or 'tomorrow'."

    # Define time ranges
    time_ranges = {
        "morning": [(8, 0), (9, 30), (11, 0)],
        "afternoon": [(13, 0), (14, 30), (16, 0)],
        "evening": [(17, 30), (18, 30), (19, 30)],
        "any": [(8, 0), (9, 30), (11, 0), (13, 0), (14, 30), (16, 0), (17, 30), (19, 0)]
    }

    if preferred_time.lower() not in time_ranges:
        preferred_time = "any"

    slots = time_ranges[preferred_time.lower()]

    # Build response
    result = [f"""
🕐 **Available Time Slots**

📅 **Date:** {check_date.strftime('%A, %B %d, %Y')}
⏱️  **Duration needed:** {duration_minutes} minutes
🎯 **Preference:** {preferred_time.title()}
    """.strip()]

    result.append("\n\n**Available slots:**\n")

    # Generate time slots
    for hour, minute in slots:
        start = datetime(check_date.year, check_date.month, check_date.day, hour, minute)
        end = start + timedelta(minutes=duration_minutes)

        result.append(f"✅ **{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}** ({duration_minutes} min)")

    # Add recommendations
    result.append("\n\n💡 **Recommendations:**")
    if preferred_time == "morning":
        result.append("• Morning slots are best for focused work")
        result.append("• Earlier times have less scheduling conflicts")
    elif preferred_time == "afternoon":
        result.append("• Afternoon slots work well for collaborative meetings")
        result.append("• Post-lunch time is good for discussions")
    elif preferred_time == "evening":
        result.append("• Evening slots are ideal for flexible schedules")
        result.append("• Good for international team meetings")
    else:
        result.append("• Consider attendee time zones when choosing")
        result.append("• Morning slots typically have better availability")

    result.append("\n📝 **Tip:** Use create_event to schedule one of these slots!")

    return "\n".join(result)
