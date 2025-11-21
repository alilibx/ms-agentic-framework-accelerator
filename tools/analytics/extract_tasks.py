"""Task extraction tool - Parse action items from messages."""

from typing import Annotated
from tools._decorators import tool
import re


@tool(
    domain="analytics",
    description="Extract actionable tasks and deadlines from a message",
    tags=["analytics", "tasks", "todos", "deadlines", "extract"],
    mock=False,
)
def extract_tasks_from_message(
    message_subject: Annotated[str, "Message subject or summary"],
    message_body: Annotated[str, "Message content"],
    message_from: Annotated[str, "Sender of the message"] = "",
) -> str:
    """Extract tasks, action items, and deadlines from a message.

    Intelligently parses messages to identify:
    - Action items and todos
    - Deadlines and due dates
    - Meeting times
    - Deliverables
    - Requests

    Args:
        message_subject: Message subject
        message_body: Message content
        message_from: Optional sender info

    Returns:
        Structured list of extracted tasks

    Example:
        >>> extract_tasks_from_message(
        ...     message_subject="Project Updates",
        ...     message_body="Please send the Q4 report by Friday. Also, can you review the proposal and schedule a meeting for next Tuesday at 2pm?"
        ... )
        "📋 **Extracted Tasks**

        Found 3 action items:

        1. ✅ **Send Q4 report**
           📅 Deadline: Friday
           🎯 Priority: High
           👤 Requested by: Unknown

        2. ✅ **Review proposal**
           📅 Deadline: Not specified
           🎯 Priority: Medium
           👤 Requested by: Unknown

        3. 📅 **Schedule meeting**
           🕐 When: next Tuesday at 2pm
           🎯 Priority: Medium
           👤 Requested by: Unknown"
    """
    content = f"{message_subject} {message_body}"

    # Extract tasks
    tasks = _extract_action_items(content)

    # Extract deadlines
    deadlines = _extract_deadlines(content)

    # Extract meetings
    meetings = _extract_meetings(content)

    # Combine all
    all_items = []
    all_items.extend([{'type': 'task', **task} for task in tasks])
    all_items.extend([{'type': 'deadline', **dl} for dl in deadlines])
    all_items.extend([{'type': 'meeting', **mtg} for mtg in meetings])

    if not all_items:
        return """
📋 **Extracted Tasks**

❌ No actionable tasks found in this message.

This appears to be informational or doesn't contain specific action items.
        """.strip()

    # Format result
    result = [f"📋 **Extracted Tasks**\n"]
    result.append(f"Found {len(all_items)} action {'item' if len(all_items) == 1 else 'items'}:\n")

    for i, item in enumerate(all_items, 1):
        if item['type'] == 'task':
            result.append(f"""
{i}. ✅ **{item['description']}**
   📅 Deadline: {item.get('deadline', 'Not specified')}
   🎯 Priority: {item.get('priority', 'Medium')}
   👤 Requested by: {message_from or 'Unknown'}
            """.strip())

        elif item['type'] == 'meeting':
            result.append(f"""
{i}. 📅 **{item['description']}**
   🕐 When: {item.get('when', 'Not specified')}
   🎯 Priority: {item.get('priority', 'Medium')}
   👤 With: {message_from or 'Unknown'}
            """.strip())

        elif item['type'] == 'deadline':
            result.append(f"""
{i}. ⏰ **Deadline: {item['description']}**
   📅 Due: {item.get('when', 'Not specified')}
   🎯 Priority: High
            """.strip())

    return "\n\n".join(result)


def _extract_action_items(content: str) -> list:
    """Extract action items from content."""
    tasks = []

    # Common action patterns
    action_patterns = [
        r'please\s+([^.!?]+)',
        r'can you\s+([^.!?]+)',
        r'could you\s+([^.!?]+)',
        r'need(?:ed)?\s+to\s+([^.!?]+)',
        r'send\s+([^.!?]+)',
        r'provide\s+([^.!?]+)',
        r'review\s+([^.!?]+)',
        r'prepare\s+([^.!?]+)',
        r'complete\s+([^.!?]+)',
    ]

    content_lower = content.lower()

    for pattern in action_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        for match in matches:
            description = match.strip()
            if len(description) > 10 and len(description) < 100:  # Reasonable length
                # Detect deadline in the same sentence
                deadline = "Not specified"
                if any(day in description for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                    deadline = "This week"
                elif 'today' in description:
                    deadline = "Today"
                elif 'tomorrow' in description:
                    deadline = "Tomorrow"
                elif 'friday' in description:
                    deadline = "Friday"

                # Detect priority
                priority = "High" if any(word in description for word in ['urgent', 'asap', 'immediately']) else "Medium"

                tasks.append({
                    'description': description.capitalize(),
                    'deadline': deadline,
                    'priority': priority
                })

    return tasks[:5]  # Limit to top 5


def _extract_deadlines(content: str) -> list:
    """Extract explicit deadlines."""
    deadlines = []

    # Deadline patterns
    deadline_patterns = [
        r'(?:due|deadline|by)\s+([^.!?]+)',
        r'(?:before|until)\s+([^.!?]+)',
    ]

    content_lower = content.lower()

    for pattern in deadline_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        for match in matches:
            when = match.strip()
            if len(when) > 3 and len(when) < 50:
                deadlines.append({
                    'description': f"Deadline: {when}",
                    'when': when.capitalize()
                })

    return deadlines[:3]


def _extract_meetings(content: str) -> list:
    """Extract meeting requests."""
    meetings = []

    # Meeting patterns
    meeting_keywords = ['meeting', 'call', 'discussion', 'session', 'appointment']

    content_lower = content.lower()

    for keyword in meeting_keywords:
        if keyword in content_lower:
            # Try to extract time information
            time_pattern = r'((?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|next week)[^.!?]*(?:\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?)'
            time_matches = re.findall(time_pattern, content_lower, re.IGNORECASE)

            if time_matches:
                for when in time_matches:
                    meetings.append({
                        'description': f"Schedule {keyword}",
                        'when': when.strip().capitalize(),
                        'priority': 'Medium'
                    })
            else:
                meetings.append({
                    'description': f"Schedule {keyword}",
                    'when': 'Time not specified',
                    'priority': 'Medium'
                })

    return meetings[:3]
