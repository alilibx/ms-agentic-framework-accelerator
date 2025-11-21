"""Unified inbox tool - View emails from all accounts in one place."""

from typing import Annotated
from tools._decorators import tool
import os

# Try to import account manager
try:
    from .account_manager import get_account_manager
    ACCOUNT_MANAGER_AVAILABLE = True
except ImportError:
    ACCOUNT_MANAGER_AVAILABLE = False


USE_REAL_EMAIL_API = os.getenv("USE_REAL_EMAIL_API", "false").lower() == "true" and ACCOUNT_MANAGER_AVAILABLE


@tool(
    domain="email",
    description="Read emails from all accounts in a unified view",
    tags=["email", "unified", "inbox", "all-accounts", "aggregate"],
    mock=not USE_REAL_EMAIL_API,
)
def unified_inbox(
    limit_per_account: Annotated[int, "Maximum emails per account"] = 5,
    filter_unread: Annotated[bool, "Show only unread emails"] = False,
) -> str:
    """Read emails from all configured accounts in a unified view.

    Aggregates inbox across all email accounts and displays them together.

    Args:
        limit_per_account: Maximum number of emails to retrieve per account
        filter_unread: If True, show only unread emails

    Returns:
        Formatted string with unified inbox view

    Example:
        >>> unified_inbox(limit_per_account=3)
        "📬 **Unified Inbox** (3 accounts, 9 messages total)

        ═══ work@company.com (Gmail) ═══

        1. 🟢 From: boss@company.com
           📝 Subject: Project Update
           ⏰ Received: 2025-11-22 14:30

        ═══ personal@gmail.com (Gmail) ═══
        ..."
    """
    if USE_REAL_EMAIL_API:
        try:
            manager = get_account_manager()
            accounts = manager.list_accounts()

            if not accounts:
                return "📭 **No email accounts configured.**"

            all_results = []
            total_messages = 0

            for account in accounts:
                try:
                    # Get client for this account
                    client = manager.get_client(account['account_id'])

                    # Read inbox
                    emails = client.read_inbox(
                        limit=limit_per_account,
                        filter_unread=filter_unread
                    )

                    if emails:
                        # Format account header
                        account_header = f"\n═══ {account['email']} ({account['provider'].title()}) ═══\n"
                        all_results.append(account_header)

                        # Format emails
                        for i, email in enumerate(emails, 1):
                            status = "🟢" if email['unread'] else "⚪"

                            all_results.append(f"""
{i}. {status} **From:** {email['from']}
   📝 **Subject:** {email['subject']}
   💬 **Preview:** {email['preview']}
   ⏰ **Received:** {email['received']}
                            """.strip())

                        total_messages += len(emails)

                except Exception as e:
                    all_results.append(f"\n⚠️ **Error reading {account['email']}:** {str(e)}\n")

            if total_messages == 0:
                filter_text = "unread " if filter_unread else ""
                return f"📭 **No {filter_text}emails found** across all accounts."

            # Build final result
            header = f"📬 **Unified Inbox** ({len(accounts)} accounts, {total_messages} messages total)"

            if filter_unread:
                header = f"📬 **Unified Inbox - Unread Only** ({len(accounts)} accounts, {total_messages} unread)"

            return header + "\n" + "\n\n".join(all_results)

        except Exception as e:
            return f"⚠️ **Error accessing unified inbox:** {str(e)}"

    # Mock implementation
    return _unified_inbox_mock(limit_per_account, filter_unread)


def _unified_inbox_mock(limit_per_account: int = 5, filter_unread: bool = False) -> str:
    """Mock implementation of unified inbox."""
    filter_text = " - Unread Only" if filter_unread else ""

    return f"""
📬 **Unified Inbox{filter_text}** (MOCK - 2 accounts, 6 messages total)

═══ work@company.com (Gmail) ═══

1. 🟢 **From:** boss@company.com
   📝 **Subject:** Q4 Project Status
   💬 **Preview:** Hi, can you provide an update on the Q4 project...
   ⏰ **Received:** 2025-11-22 14:30

2. ⚪ **From:** hr@company.com
   📝 **Subject:** Benefits Enrollment Reminder
   💬 **Preview:** Don't forget to complete your benefits enrollment...
   ⏰ **Received:** 2025-11-22 10:15

3. 🟢 **From:** client@bigcorp.com
   📝 **Subject:** Meeting Tomorrow
   💬 **Preview:** Looking forward to our meeting tomorrow at 2pm...
   ⏰ **Received:** 2025-11-22 09:00

═══ personal@gmail.com (Gmail) ═══

1. 🟢 **From:** newsletter@techcrunch.com
   📝 **Subject:** Daily Tech News
   💬 **Preview:** Today's top stories in technology...
   ⏰ **Received:** 2025-11-22 08:00

2. ⚪ **From:** friend@example.com
   📝 **Subject:** Weekend Plans?
   💬 **Preview:** Hey! Want to grab coffee this weekend?
   ⏰ **Received:** 2025-11-21 19:45

3. 🟢 **From:** notifications@github.com
   📝 **Subject:** New PR Review Request
   💬 **Preview:** Someone requested your review on a pull request...
   ⏰ **Received:** 2025-11-21 16:30

💡 **Tip:** Use read_inbox with account_id parameter to view a specific account's inbox.
    """.strip()
