"""Send email tool - Compose and send emails."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool


@tool(
    domain="email",
    description="Send an email to a recipient",
    tags=["email", "send", "compose", "outbox"],
    mock=True,
)
def send_email(
    to: Annotated[str, "The recipient email address"],
    subject: Annotated[str, "The email subject line"],
    body: Annotated[str, "The email body content"],
    cc: Annotated[str, "CC recipients (optional)"] = "",
) -> str:
    """Send an email to a recipient.

    This is a mock implementation that simulates sending emails.
    In production, this would integrate with SMTP or email service APIs.

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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = f"""
✅ **Email Sent Successfully!**

📧 **To:** {to}
📝 **Subject:** {subject}
💬 **Message:** {body[:100]}{'...' if len(body) > 100 else ''}
⏰ **Sent:** {timestamp}
    """.strip()

    if cc:
        result += f"\n📎 **CC:** {cc}"

    result += f"\n🔢 **Message ID:** MSG-{hash(f'{to}{subject}{timestamp}') % 100000}"

    return result
