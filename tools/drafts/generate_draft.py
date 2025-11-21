"""Generate draft reply tool - AI-powered draft generation."""

from typing import Annotated
from tools._decorators import tool
import os

try:
    from .draft_store import get_draft_store
    DRAFT_STORE_AVAILABLE = True
except ImportError:
    DRAFT_STORE_AVAILABLE = False


@tool(
    domain="drafts",
    description="Generate a draft reply for an email or WhatsApp message",
    tags=["drafts", "generate", "reply", "ai"],
    mock=False,
)
def generate_draft_reply(
    message_type: Annotated[str, "Type of message: 'email' or 'whatsapp'"],
    from_sender: Annotated[str, "Who sent the original message"],
    original_message: Annotated[str, "The original message content"],
    reply_tone: Annotated[str, "Tone for the reply: 'professional', 'casual', 'friendly', 'formal'"] = "professional",
    key_points: Annotated[str, "Key points to include in the reply (optional)"] = "",
    account_id: Annotated[str, "Email account to use (for email only, optional)"] = "",
) -> str:
    """Generate a draft reply to a message using AI.

    This tool analyzes the original message and generates an appropriate draft reply
    that can be reviewed before sending.

    Args:
        message_type: Type of message ('email' or 'whatsapp')
        from_sender: Sender of the original message
        original_message: Original message content
        reply_tone: Desired tone for the reply
        key_points: Specific points to address in the reply
        account_id: Email account to use (for email)

    Returns:
        Confirmation with draft ID and preview

    Example:
        >>> generate_draft_reply(
        ...     message_type="email",
        ...     from_sender="boss@company.com",
        ...     original_message="Can you send me the Q4 report?",
        ...     reply_tone="professional"
        ... )
        "✅ Draft generated successfully!
        Draft ID: draft_20251122_153000_0

        Preview:
        To: boss@company.com
        Subject: Re: Q4 Report

        Hi,

        Thank you for your email. I'll prepare the Q4 report and send it to you
        by end of day today.

        Best regards"
    """
    if not DRAFT_STORE_AVAILABLE:
        return "❌ Draft store not available"

    try:
        # Generate subject/summary based on original message
        if message_type.lower() == 'email':
            subject = f"Re: {original_message[:50]}..." if len(original_message) > 50 else f"Re: {original_message}"
        else:
            subject = f"Reply to message from {from_sender}"

        # Generate draft body based on tone and key points
        body = _generate_reply_content(
            original_message=original_message,
            tone=reply_tone,
            key_points=key_points,
            message_type=message_type
        )

        # Save draft
        store = get_draft_store()
        draft_id = store.add_draft(
            message_type=message_type.lower(),
            to=from_sender,
            subject=subject,
            body=body,
            account_id=account_id if account_id else None,
            original_message={'from': from_sender, 'content': original_message},
            metadata={'tone': reply_tone, 'key_points': key_points}
        )

        # Format response
        preview = body[:200] + "..." if len(body) > 200 else body

        return f"""
✅ **Draft Generated Successfully!**

🆔 **Draft ID:** {draft_id}
📧 **To:** {from_sender}
📝 **Type:** {message_type.title()}
{'📨 **Account:** ' + account_id if account_id else ''}

**Preview:**
{subject if message_type.lower() == 'email' else ''}

{preview}

💡 **Next steps:**
- Review draft: Use `list_drafts()` to see all drafts
- Approve and send: Use `approve_draft(draft_id="{draft_id}")`
- Edit: Modify the draft before sending
- Reject: Use `reject_draft(draft_id="{draft_id}")`
        """.strip()

    except Exception as e:
        return f"❌ **Error generating draft:** {str(e)}"


def _generate_reply_content(
    original_message: str,
    tone: str,
    key_points: str,
    message_type: str
) -> str:
    """Generate reply content based on parameters.

    This is a simplified implementation. In a real system, this would use
    an LLM to generate contextually appropriate replies.
    """
    # Greeting based on tone
    greetings = {
        'professional': 'Thank you for your message.',
        'casual': 'Thanks for reaching out!',
        'friendly': 'Hi! Thanks for your message.',
        'formal': 'Dear Sender,\n\nThank you for your correspondence.'
    }

    greeting = greetings.get(tone, 'Thank you for your message.')

    # Generate acknowledgment
    acknowledgment = f"I've received your message regarding: \"{original_message[:100]}...\""

    # Include key points if provided
    if key_points:
        response = f"{greeting}\n\n{acknowledgment}\n\n{key_points}"
    else:
        # Generic helpful response
        response = f"{greeting}\n\n{acknowledgment}\n\nI'll look into this and get back to you shortly."

    # Closing based on tone
    closings = {
        'professional': '\n\nBest regards',
        'casual': '\n\nCheers',
        'friendly': '\n\nTalk soon!',
        'formal': '\n\nYours sincerely'
    }

    closing = closings.get(tone, '\n\nBest regards')

    return response + closing
