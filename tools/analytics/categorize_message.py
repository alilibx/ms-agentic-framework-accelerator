"""Message categorization tool."""

from typing import Annotated
from tools._decorators import tool


@tool(
    domain="analytics",
    description="Categorize and label a message by topic, urgency, and type",
    tags=["analytics", "categorize", "label", "organize"],
    mock=False,
)
def categorize_message(
    message_from: Annotated[str, "Sender of the message"],
    message_subject: Annotated[str, "Subject or summary"],
    message_body: Annotated[str, "Message content"],
) -> str:
    """Analyze and categorize a message with labels and metadata.

    Automatically categorizes messages by:
    - Topic/Category (work, personal, finance, etc.)
    - Urgency level (high, medium, low)
    - Message type (request, question, notification, etc.)
    - Sentiment (positive, neutral, negative)

    Args:
        message_from: Sender of the message
        message_subject: Subject or summary
        message_body: Message content

    Returns:
        Categorization results with recommended labels

    Example:
        >>> categorize_message(
        ...     message_from="boss@company.com",
        ...     message_subject="Q4 Report Needed",
        ...     message_body="Please send the Q4 financial report by Friday"
        ... )
        "📊 **Message Categorization**

        **Primary Category:** Work - Reports
        **Type:** Request / Action Required
        **Urgency:** High
        **Sentiment:** Neutral

        **Suggested Labels:**
        🏷️ work
        🏷️ finance
        🏷️ reports
        🏷️ urgent
        🏷️ action-required

        **Recommended Actions:**
        - Add to task list with Friday deadline
        - Flag as high priority
        - Set reminder for Thursday"
    """
    content = f"{message_subject} {message_body}".lower()

    # Topic categorization
    topics = _detect_topics(content)

    # Urgency level
    urgency = _detect_urgency(content)

    # Message type
    msg_type = _detect_message_type(content)

    # Sentiment
    sentiment = _detect_sentiment(content)

    # Generate labels
    labels = _generate_labels(topics, urgency, msg_type, message_from)

    # Recommended actions
    actions = _recommend_actions(urgency, msg_type, content)

    # Format result
    result = f"""
📊 **Message Categorization**

**Primary Category:** {topics[0] if topics else 'General'}
**Type:** {msg_type}
**Urgency:** {urgency}
**Sentiment:** {sentiment}

**Suggested Labels:**
{chr(10).join(['🏷️ ' + label for label in labels])}

**Recommended Actions:**
{chr(10).join(['- ' + action for action in actions])}
    """.strip()

    return result


def _detect_topics(content: str) -> list:
    """Detect message topics/categories."""
    topic_keywords = {
        'Work - Meetings': ['meeting', 'schedule', 'calendar', 'appointment', 'call'],
        'Work - Reports': ['report', 'quarterly', 'monthly', 'analysis', 'data'],
        'Work - Projects': ['project', 'deliverable', 'milestone', 'deadline'],
        'Finance': ['invoice', 'payment', 'budget', 'expense', 'financial'],
        'HR/Admin': ['leave', 'vacation', 'benefits', 'payroll', 'hr'],
        'Technical': ['bug', 'issue', 'error', 'technical', 'system', 'code'],
        'Personal': ['personal', 'family', 'friend', 'weekend'],
        'Marketing': ['campaign', 'marketing', 'social media', 'promotion'],
    }

    detected = []
    for topic, keywords in topic_keywords.items():
        if any(kw in content for kw in keywords):
            detected.append(topic)

    return detected if detected else ['General']


def _detect_urgency(content: str) -> str:
    """Detect message urgency."""
    high_urgency = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'now']
    medium_urgency = ['soon', 'today', 'this week', 'important']

    if any(kw in content for kw in high_urgency):
        return "High"
    elif any(kw in content for kw in medium_urgency):
        return "Medium"
    else:
        return "Low"


def _detect_message_type(content: str) -> str:
    """Detect message type."""
    if '?' in content or any(kw in content for kw in ['can you', 'could you', 'would you', 'how', 'what', 'when']):
        return "Question / Inquiry"
    elif any(kw in content for kw in ['please', 'need', 'require', 'send', 'provide']):
        return "Request / Action Required"
    elif any(kw in content for kw in ['fyi', 'update', 'notification', 'inform']):
        return "Notification / FYI"
    elif any(kw in content for kw in ['thanks', 'thank you', 'appreciate']):
        return "Acknowledgment / Thanks"
    else:
        return "General Communication"


def _detect_sentiment(content: str) -> str:
    """Detect message sentiment."""
    positive_words = ['thanks', 'great', 'excellent', 'appreciate', 'good', 'well done']
    negative_words = ['urgent', 'issue', 'problem', 'concern', 'disappointed', 'error']

    positive_count = sum(1 for word in positive_words if word in content)
    negative_count = sum(1 for word in negative_words if word in content)

    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"


def _generate_labels(topics: list, urgency: str, msg_type: str, sender: str) -> list:
    """Generate recommended labels."""
    labels = []

    # Topic-based labels
    for topic in topics:
        if 'work' in topic.lower():
            labels.append('work')
        if 'personal' in topic.lower():
            labels.append('personal')

    # Topic-specific labels
    if 'Meeting' in ' '.join(topics):
        labels.append('meeting')
    if 'Report' in ' '.join(topics):
        labels.append('reports')
    if 'Finance' in ' '.join(topics):
        labels.append('finance')
    if 'Project' in ' '.join(topics):
        labels.append('project')

    # Urgency labels
    if urgency == "High":
        labels.append('urgent')
    if urgency == "Medium":
        labels.append('important')

    # Type labels
    if 'Action Required' in msg_type:
        labels.append('action-required')
    if 'Question' in msg_type:
        labels.append('question')

    # Sender-based labels
    if 'boss' in sender.lower() or 'manager' in sender.lower():
        labels.append('from-manager')

    return list(set(labels))  # Remove duplicates


def _recommend_actions(urgency: str, msg_type: str, content: str) -> list:
    """Recommend actions based on categorization."""
    actions = []

    if urgency == "High":
        actions.append("Flag as high priority")
        actions.append("Respond within 24 hours")

    if 'Action Required' in msg_type:
        actions.append("Add to task list")
        if any(day in content for day in ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
            actions.append("Set deadline reminder")

    if 'Question' in msg_type:
        actions.append("Research and prepare response")

    if 'meeting' in content or 'schedule' in content:
        actions.append("Check calendar availability")
        actions.append("Add to calendar if confirmed")

    if not actions:
        actions.append("Review and file appropriately")

    return actions
