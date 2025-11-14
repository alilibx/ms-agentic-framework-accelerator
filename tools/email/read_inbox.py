"""Read inbox tool - View recent emails."""

from typing import Annotated
from datetime import datetime, timedelta
import random
import os
from tools._decorators import tool

# Try to import Gmail utilities
try:
    from .gmail_utils import get_gmail_client, is_gmail_configured
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    is_gmail_configured = lambda: False

# Check if we should use real Gmail or mock
USE_REAL_GMAIL = os.getenv("USE_REAL_EMAIL_API", "false").lower() == "true" and GMAIL_AVAILABLE


@tool(
    domain="email",
    description="Read recent emails from inbox",
    tags=["email", "inbox", "read", "messages"],
    mock=not USE_REAL_GMAIL,
)
def read_inbox(
    limit: Annotated[int, "Maximum number of emails to retrieve"] = 5,
    filter_unread: Annotated[bool, "Show only unread emails"] = False,
) -> str:
    """Read recent emails from the inbox.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        limit: Maximum number of emails to retrieve (default: 5, max: 20)
        filter_unread: If True, show only unread emails

    Returns:
        Formatted string with inbox emails

    Example:
        >>> read_inbox(limit=3)
        "📬 **Your Inbox (3 messages)**

        1. 🟢 From: boss@company.com
           📝 Subject: Project Update Required
           ⏰ Received: 2025-10-24 14:30

        2. ⚪ From: team@slack.com
           📝 Subject: New notification from Slack
           ⏰ Received: 2025-10-24 13:15
        ..."
    """
    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            gmail = get_gmail_client()
            emails = gmail.read_inbox(limit=limit, filter_unread=filter_unread)

            if not emails:
                return "📭 **No emails found** matching your criteria."

            header = "📬 **Unread Messages** (via Gmail)" if filter_unread else "📬 **Your Inbox** (via Gmail)"
            result = [f"{header} ({len(emails)} {'message' if len(emails) == 1 else 'messages'})\n"]

            for i, email in enumerate(emails, 1):
                status = "🟢" if email['unread'] else "⚪"

                result.append(f"""
{i}. {status} **From:** {email['from']}
   📝 **Subject:** {email['subject']}
   💬 **Preview:** {email['preview']}
   ⏰ **Received:** {email['received']}
                """.strip())

            return "\n\n".join(result)

        except Exception as e:
            # Fall back to mock if Gmail fails
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _read_inbox_mock(limit, filter_unread)

    # Mock implementation
    return _read_inbox_mock(limit, filter_unread)


def _read_inbox_mock(limit: int = 5, filter_unread: bool = False) -> str:
    """Mock implementation of inbox reading.

    Args:
        limit: Maximum number of emails to retrieve
        filter_unread: If True, show only unread emails

    Returns:
        Formatted mock inbox data
    """
    # Mock email data
    sample_emails = [
        {
            "from": "boss@company.com",
            "subject": "Project Update Required",
            "preview": "Hi, can you provide an update on the Q4 project status...",
            "unread": True,
            "priority": "high"
        },
        {
            "from": "team@slack.com",
            "subject": "New notification from Slack",
            "preview": "You have 3 unread messages in #engineering channel...",
            "unread": True,
            "priority": "normal"
        },
        {
            "from": "notifications@github.com",
            "subject": "Pull Request Review Requested",
            "preview": "johndoe requested your review on PR #142: Add email agent...",
            "unread": False,
            "priority": "normal"
        },
        {
            "from": "news@techcrunch.com",
            "subject": "Daily Tech News Digest",
            "preview": "Today's top stories: AI breakthrough, new startup funding...",
            "unread": False,
            "priority": "low"
        },
        {
            "from": "client@bigcorp.com",
            "subject": "Meeting Confirmation - Tomorrow 2PM",
            "preview": "Looking forward to our meeting tomorrow to discuss...",
            "unread": True,
            "priority": "high"
        },
    ]

    # Filter if requested
    if filter_unread:
        emails = [e for e in sample_emails if e["unread"]]
        header = "📬 **Unread Messages**"
    else:
        emails = sample_emails
        header = "📬 **Your Inbox**"

    # Limit results
    emails = emails[:min(limit, len(emails))]

    if not emails:
        return "📭 **No emails found** matching your criteria."

    result = [f"{header} ({len(emails)} {'message' if len(emails) == 1 else 'messages'})\n"]

    for i, email in enumerate(emails, 1):
        # Generate realistic timestamp
        hours_ago = random.randint(1, 48)
        timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")

        # Status indicator
        status = "🟢" if email["unread"] else "⚪"
        priority_icon = "🔴" if email["priority"] == "high" else "🟡" if email["priority"] == "normal" else ""

        result.append(f"""
{i}. {status} **From:** {email['from']} {priority_icon}
   📝 **Subject:** {email['subject']}
   💬 **Preview:** {email['preview']}
   ⏰ **Received:** {timestamp}
        """.strip())

    return "\n\n".join(result)
