"""Approve and send draft tool."""

from typing import Annotated
from tools._decorators import tool

try:
    from .draft_store import get_draft_store
    DRAFT_STORE_AVAILABLE = True
except ImportError:
    DRAFT_STORE_AVAILABLE = False


@tool(
    domain="drafts",
    description="Approve and send a draft message",
    tags=["drafts", "approve", "send"],
    mock=False,
)
def approve_draft(
    draft_id: Annotated[str, "The draft ID to approve and send"],
) -> str:
    """Approve and send a draft message.

    This will send the draft using the appropriate email or WhatsApp tool.

    Args:
        draft_id: ID of the draft to approve

    Returns:
        Confirmation of approval and sending

    Example:
        >>> approve_draft(draft_id="draft_20251122_153000_0")
        "✅ Draft approved and sent successfully!

        Sent to: boss@company.com
        Type: Email
        Subject: Re: Q4 Report

        Message ID: MSG-123456"
    """
    if not DRAFT_STORE_AVAILABLE:
        return "❌ Draft store not available"

    try:
        store = get_draft_store()
        draft = store.get_draft(draft_id)

        if not draft:
            return f"❌ **Draft not found:** {draft_id}"

        if draft.get('status') == 'sent':
            return f"⚠️ **Draft already sent:** {draft_id}"

        # Send the message based on type
        message_type = draft.get('message_type')
        send_result = None

        if message_type == 'email':
            # Import email send tool
            try:
                from tools.email.send_email import send_email

                send_result = send_email(
                    to=draft['to'],
                    subject=draft['subject'],
                    body=draft['body'],
                    account_id=draft.get('account_id', '')
                )

            except Exception as e:
                return f"❌ **Failed to send email:** {str(e)}"

        elif message_type == 'whatsapp':
            # Import WhatsApp send tool
            try:
                from tools.whatsapp.send_message import send_whatsapp_message

                send_result = send_whatsapp_message(
                    to=draft['to'],
                    message=draft['body']
                )

            except Exception as e:
                return f"❌ **Failed to send WhatsApp message:** {str(e)}"

        else:
            return f"❌ **Unknown message type:** {message_type}"

        # Update draft status
        store.update_draft(draft_id, status='sent')

        return f"""
✅ **Draft Approved and Sent Successfully!**

🆔 **Draft ID:** {draft_id}
📧 **To:** {draft['to']}
📝 **Type:** {message_type.title()}
📝 **Subject:** {draft.get('subject', 'N/A')}

**Send Result:**
{send_result}
        """.strip()

    except Exception as e:
        return f"❌ **Error approving draft:** {str(e)}"


@tool(
    domain="drafts",
    description="Reject a draft message",
    tags=["drafts", "reject", "delete"],
    mock=False,
)
def reject_draft(
    draft_id: Annotated[str, "The draft ID to reject"],
    reason: Annotated[str, "Reason for rejection (optional)"] = "",
) -> str:
    """Reject a draft message.

    Args:
        draft_id: ID of the draft to reject
        reason: Optional reason for rejection

    Returns:
        Confirmation of rejection

    Example:
        >>> reject_draft(draft_id="draft_20251122_153000_0", reason="Not needed anymore")
        "✅ Draft rejected successfully!

        Draft ID: draft_20251122_153000_0
        Reason: Not needed anymore"
    """
    if not DRAFT_STORE_AVAILABLE:
        return "❌ Draft store not available"

    try:
        store = get_draft_store()
        draft = store.get_draft(draft_id)

        if not draft:
            return f"❌ **Draft not found:** {draft_id}"

        # Update draft status
        metadata = draft.get('metadata', {})
        if reason:
            metadata['rejection_reason'] = reason

        store.update_draft(draft_id, status='rejected', metadata=metadata)

        return f"""
✅ **Draft Rejected Successfully!**

🆔 **Draft ID:** {draft_id}
📧 **To:** {draft['to']}
📝 **Type:** {draft.get('message_type', 'unknown').title()}
{f'📝 **Reason:** {reason}' if reason else ''}

The draft has been marked as rejected and will not be sent.
        """.strip()

    except Exception as e:
        return f"❌ **Error rejecting draft:** {str(e)}"
