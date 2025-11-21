"""List drafts tool - View pending and saved drafts."""

from typing import Annotated
from tools._decorators import tool

try:
    from .draft_store import get_draft_store
    DRAFT_STORE_AVAILABLE = True
except ImportError:
    DRAFT_STORE_AVAILABLE = False


@tool(
    domain="drafts",
    description="List all draft messages",
    tags=["drafts", "list", "pending", "review"],
    mock=False,
)
def list_drafts(
    status: Annotated[str, "Filter by status: 'pending', 'approved', 'rejected', 'sent', or 'all'"] = "pending",
    limit: Annotated[int, "Maximum number of drafts to show"] = 10,
) -> str:
    """List draft messages for review.

    Args:
        status: Filter by status ('pending', 'approved', 'rejected', 'sent', or 'all')
        limit: Maximum number of drafts to show

    Returns:
        Formatted list of drafts

    Example:
        >>> list_drafts(status="pending")
        "📝 **Pending Drafts** (3 drafts)

        1. Draft ID: draft_20251122_153000_0
           📧 Type: Email
           To: boss@company.com
           Subject: Re: Q4 Report
           Created: 2025-11-22 15:30:00
           Preview: Thank you for your message...

        2. Draft ID: draft_20251122_153015_1
           💬 Type: WhatsApp
           To: John Doe (+1234567890)
           Created: 2025-11-22 15:30:15
           Preview: Thanks for reaching out!..."
    """
    if not DRAFT_STORE_AVAILABLE:
        return "❌ Draft store not available"

    try:
        store = get_draft_store()

        # Get drafts
        if status.lower() == 'all':
            drafts = store.list_drafts(limit=limit)
        else:
            drafts = store.list_drafts(status=status.lower(), limit=limit)

        if not drafts:
            return f"📭 **No {status} drafts found.**"

        # Format output
        status_emojis = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌',
            'sent': '📤'
        }

        header = f"📝 **{status.title()} Drafts** ({len(drafts)} {'draft' if len(drafts) == 1 else 'drafts'})\n"
        result = [header]

        for i, draft in enumerate(drafts, 1):
            message_type = draft.get('message_type', 'unknown').title()
            type_emoji = "📧" if draft.get('message_type') == 'email' else "💬"
            status_emoji = status_emojis.get(draft.get('status'), '❓')

            preview = draft.get('body', '')[:100]
            if len(draft.get('body', '')) > 100:
                preview += "..."

            draft_info = f"""
{i}. {status_emoji} **Draft ID:** {draft['id']}
   {type_emoji} **Type:** {message_type}
   📧 **To:** {draft.get('to', 'Unknown')}
   📝 **Subject:** {draft.get('subject', 'N/A')}
   🕐 **Created:** {draft.get('created_at', 'Unknown')[:19]}
   💬 **Preview:** {preview}
            """.strip()

            # Add account info for email
            if draft.get('account_id'):
                draft_info += f"\n   📨 **Account:** {draft['account_id']}"

            result.append(draft_info)

        footer = f"""

💡 **Next steps:**
- Approve and send: `approve_draft(draft_id="DRAFT_ID")`
- Reject: `reject_draft(draft_id="DRAFT_ID")`
- View specific draft: Use the draft ID
        """.strip()

        return "\n\n".join(result) + "\n\n" + footer

    except Exception as e:
        return f"❌ **Error listing drafts:** {str(e)}"
