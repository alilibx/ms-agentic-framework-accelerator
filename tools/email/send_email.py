"""Send email tool - Compose and send emails."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool
import os

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
    description="Send an email to a recipient",
    tags=["email", "send", "compose", "outbox"],
    mock=not USE_REAL_GMAIL,
)
def send_email(
    to: Annotated[str, "The recipient email address"],
    subject: Annotated[str, "The email subject line"],
    body: Annotated[str, "The email body content"],
    cc: Annotated[str, "CC recipients (optional)"] = "",
) -> str:
    """Send an email to a recipient.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        cc: Optional CC recipients

    Returns:
        Formatted string confirming email was sent

    Example:
        >>> send_email("user@example.com", "Meeting", "Let's meet at 3pm")
        "✅ Email sent successfully!
        📧 To: user@example.com
        📝 Subject: Meeting
        ⏰ Sent: 2025-10-24 15:30:00"
    """
    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            gmail = get_gmail_client()
            result_data = gmail.send_email(to, subject, body, cc or None)

            if result_data['success']:
                result = f"""
✅ **Email Sent Successfully!** (via Gmail)

📧 **To:** {to}
📝 **Subject:** {subject}
💬 **Message:** {body[:100]}{'...' if len(body) > 100 else ''}
⏰ **Sent:** {result_data['timestamp']}
🔢 **Message ID:** {result_data['message_id']}
                """.strip()

                if cc:
                    result += f"\n📎 **CC:** {cc}"

                return result
            else:
                return f"❌ **Failed to send email:** {result_data.get('error', 'Unknown error')}"

        except Exception as e:
            # Fall back to mock if Gmail fails
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _send_email_mock(to, subject, body, cc)

    # Mock implementation
    return _send_email_mock(to, subject, body, cc)


def _send_email_mock(to: str, subject: str, body: str, cc: str = "") -> str:
    """Mock implementation of email sending.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        cc: Optional CC recipients

    Returns:
        Formatted mock confirmation message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = f"""
✅ **Email Sent Successfully!** (MOCK)

📧 **To:** {to}
📝 **Subject:** {subject}
💬 **Message:** {body[:100]}{'...' if len(body) > 100 else ''}
⏰ **Sent:** {timestamp}
    """.strip()

    if cc:
        result += f"\n📎 **CC:** {cc}"

    result += f"\n🔢 **Message ID:** MSG-{hash(f'{to}{subject}{timestamp}') % 100000}"

    return result
