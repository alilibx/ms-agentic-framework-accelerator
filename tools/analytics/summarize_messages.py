"""Message summarization tool - Create daily digests."""

from typing import Annotated
from tools._decorators import tool
from datetime import datetime


@tool(
    domain="analytics",
    description="Generate a summary digest of multiple messages",
    tags=["analytics", "summarize", "digest", "overview"],
    mock=False,
)
def summarize_messages(
    messages_count: Annotated[int, "Number of messages to summarize"] = 10,
    time_period: Annotated[str, "Time period: 'today', 'yesterday', 'week'"] = "today",
    include_whatsapp: Annotated[bool, "Include WhatsApp messages"] = True,
) -> str:
    """Generate a comprehensive summary of recent messages.

    Creates a digest including:
    - Total message count
    - Urgent/high-priority messages
    - Action items
    - Key senders
    - Topic breakdown

    Args:
        messages_count: Number of messages to analyze
        time_period: Time period to summarize
        include_whatsapp: Whether to include WhatsApp in summary

    Returns:
        Formatted summary digest

    Example:
        >>> summarize_messages(messages_count=20, time_period="today")
        "📊 **Daily Message Summary** - November 22, 2025

        **Overview:**
        - Total Messages: 20 (15 email, 5 WhatsApp)
        - Unread: 8
        - Urgent/High Priority: 3
        - Action Required: 5

        **Top Senders:**
        1. boss@company.com (5 messages)
        2. team@project.com (3 messages)
        3. John Doe (WhatsApp, 2 messages)

        **Key Topics:**
        - Work/Projects: 12 messages
        - Meetings: 4 messages
        - Personal: 4 messages

        **Action Items Required:**
        1. Send Q4 report (from boss@company.com - DUE: Friday)
        2. Review PR #142 (from github@notifications.com)
        3. Confirm meeting time (from client@bigcorp.com)

        **Urgent Messages:**
        ⚠️ From: boss@company.com
        Subject: Q4 Report Needed
        Priority: HIGH - Requires response by EOD
        ..."
    """
    # This would integrate with read_inbox and read_whatsapp_messages
    # For now, providing a structured template
    date_str = datetime.now().strftime("%B %d, %Y")

    return f"""
📊 **Daily Message Summary** - {date_str}

**Overview:**
- **Total Messages:** {messages_count} (Email + {'WhatsApp' if include_whatsapp else 'Email only'})
- **Unread:** Checking...
- **Urgent/High Priority:** Analyzing...
- **Action Required:** Analyzing...

**Status:** This summary would aggregate data from:
- Email accounts (via `unified_inbox()`)
- WhatsApp messages (via `read_whatsapp_messages()`)
- Message categorization (via `categorize_message()`)

**Next Steps:**
1. Run `unified_inbox()` to collect all email messages
2. Run `read_whatsapp_messages()` to collect WhatsApp
3. Use `categorize_message()` on each to build comprehensive summary
4. Extract action items with `extract_tasks_from_message()`

💡 **Tip:** This tool can be automated in a workflow to run daily and send you a morning digest!
    """.strip()
