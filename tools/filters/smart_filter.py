"""Smart filtering logic for auto-draft decisions."""

from typing import Annotated
from tools._decorators import tool


@tool(
    domain="filters",
    description="Analyze a message and decide if it requires a draft reply",
    tags=["filter", "smart", "analyze", "decision"],
    mock=False,
)
def should_generate_draft(
    message_from: Annotated[str, "Sender of the message"],
    message_subject: Annotated[str, "Subject or summary of the message"],
    message_body: Annotated[str, "Message content"],
    message_type: Annotated[str, "Type of message: 'email' or 'whatsapp'"] = "email",
) -> str:
    """Analyze a message and intelligently decide if a draft reply should be generated.

    Uses AI-powered analysis to determine:
    - Message urgency
    - Whether a reply is needed
    - Appropriate response tone
    - Priority level

    Args:
        message_from: Sender of the message
        message_subject: Subject or summary
        message_body: Message content
        message_type: Type of message

    Returns:
        Analysis result with recommendation

    Example:
        >>> should_generate_draft(
        ...     message_from="boss@company.com",
        ...     message_subject="Urgent: Q4 Report Needed",
        ...     message_body="Please send me the Q4 report ASAP",
        ...     message_type="email"
        ... )
        "🤖 **Smart Filter Analysis**

        ✅ **Recommendation:** GENERATE DRAFT

        📊 **Analysis:**
        - Urgency: HIGH (contains 'urgent', 'ASAP')
        - Requires Reply: YES
        - Priority: HIGH
        - Suggested Tone: Professional
        - Estimated Response Time: Within 24 hours

        💡 **Reasoning:** Message appears urgent and actionable. Sender is from work
        domain. Contains request for deliverable. Recommend generating professional
        draft reply acknowledging request and providing timeline."
    """
    # Analyze the message
    analysis = _analyze_message(
        sender=message_from,
        subject=message_subject,
        body=message_body,
        msg_type=message_type
    )

    # Format result
    recommendation_emoji = "✅" if analysis['should_draft'] else "❌"
    recommendation_text = "GENERATE DRAFT" if analysis['should_draft'] else "NO DRAFT NEEDED"

    result = f"""
🤖 **Smart Filter Analysis**

{recommendation_emoji} **Recommendation:** {recommendation_text}

📊 **Analysis:**
- **Urgency:** {analysis['urgency']}
- **Requires Reply:** {analysis['requires_reply']}
- **Priority:** {analysis['priority']}
- **Suggested Tone:** {analysis['tone']}
- **Category:** {analysis['category']}

💡 **Reasoning:** {analysis['reasoning']}
    """.strip()

    if analysis['should_draft']:
        result += f"""

🎯 **Next Steps:**
1. Use `generate_draft_reply()` to create a draft
2. Review the draft with `list_drafts()`
3. Approve with `approve_draft()` when ready
        """

    return result


def _analyze_message(sender: str, subject: str, body: str, msg_type: str) -> dict:
    """Analyze message and return decision parameters.

    This is a simplified heuristic-based implementation. In production,
    this would use an LLM for more sophisticated analysis.
    """
    content = f"{subject} {body}".lower()

    # Urgency detection
    urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'important']
    urgency = "HIGH" if any(kw in content for kw in urgent_keywords) else "MEDIUM"

    # Question detection (requires reply)
    question_markers = ['?', 'can you', 'could you', 'would you', 'please', 'need', 'require']
    requires_reply = "YES" if any(marker in content for marker in question_markers) else "MAYBE"

    # Sender analysis
    is_work_email = any(domain in sender.lower() for domain in ['company', 'corp', 'work', '@'])
    is_boss = 'boss' in sender.lower() or 'manager' in sender.lower()

    # Priority calculation
    if urgency == "HIGH" or is_boss:
        priority = "HIGH"
    elif requires_reply == "YES":
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Category detection
    categories = {
        'meeting': ['meeting', 'schedule', 'calendar', 'appointment'],
        'request': ['send', 'provide', 'need', 'require', 'request'],
        'question': ['?', 'how', 'what', 'when', 'where', 'why'],
        'notification': ['notification', 'update', 'fyi', 'info'],
        'social': ['hi', 'hello', 'how are you', 'thanks', 'thank you']
    }

    detected_category = "general"
    for cat, keywords in categories.items():
        if any(kw in content for kw in keywords):
            detected_category = cat
            break

    # Tone suggestion
    if is_work_email or is_boss:
        tone = "Professional"
    elif msg_type == "whatsapp":
        tone = "Casual"
    else:
        tone = "Friendly"

    # Decision logic
    should_draft = False
    reasoning = ""

    if urgency == "HIGH" and requires_reply == "YES":
        should_draft = True
        reasoning = "Message appears urgent and requires a response. High priority sender."
    elif is_boss and requires_reply in ["YES", "MAYBE"]:
        should_draft = True
        reasoning = "Message from supervisor/manager. Professional response recommended."
    elif requires_reply == "YES" and detected_category in ["request", "question", "meeting"]:
        should_draft = True
        reasoning = f"Message contains actionable {detected_category}. Response expected."
    elif detected_category == "notification":
        should_draft = False
        reasoning = "Appears to be informational only. No response required."
    elif detected_category == "social" and priority == "LOW":
        should_draft = False
        reasoning = "Social/informal message. Can be handled manually when convenient."
    else:
        # Default: generate draft for anything uncertain
        should_draft = requires_reply == "YES"
        reasoning = "Message analysis suggests a reply may be appropriate. Draft recommended for review."

    return {
        'should_draft': should_draft,
        'urgency': urgency,
        'requires_reply': requires_reply,
        'priority': priority,
        'tone': tone,
        'category': detected_category,
        'reasoning': reasoning
    }
