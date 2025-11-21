"""List email accounts tool - View all configured email accounts."""

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
    description="List all configured email accounts",
    tags=["email", "accounts", "list", "config"],
    mock=not USE_REAL_EMAIL_API,
)
def list_email_accounts() -> str:
    """List all configured email accounts.

    Shows all email accounts available to the agent with their providers and email addresses.

    Returns:
        Formatted string with account information

    Example:
        >>> list_email_accounts()
        "📧 **Configured Email Accounts**

        1. ✅ work (default)
           Provider: Gmail
           Email: work@company.com

        2. personal
           Provider: Gmail
           Email: personal@gmail.com

        3. outlook
           Provider: Outlook
           Email: you@outlook.com"
    """
    if USE_REAL_EMAIL_API:
        try:
            manager = get_account_manager()
            accounts = manager.list_accounts()

            if not accounts:
                return "📭 **No email accounts configured.**\n\nPlease configure EMAIL_ACCOUNTS in your .env file."

            result = [f"📧 **Configured Email Accounts** ({len(accounts)} total)\n"]

            for i, account in enumerate(accounts, 1):
                default_marker = " ✅ (default)" if account['is_default'] else ""
                result.append(f"""
{i}.{default_marker} **{account['account_id']}**
   📨 Provider: {account['provider'].title()}
   📧 Email: {account['email']}
                """.strip())

            return "\n\n".join(result)

        except Exception as e:
            return f"⚠️ **Error listing accounts:** {str(e)}"

    # Mock implementation
    return _list_accounts_mock()


def _list_accounts_mock() -> str:
    """Mock implementation of account listing."""
    return """
📧 **Configured Email Accounts** (MOCK)

1. ✅ **default** (default)
   📨 Provider: Gmail
   📧 Email: you@gmail.com

2. **work**
   📨 Provider: Gmail
   📧 Email: work@company.com

💡 **Tip:** Use the account_id when calling other email tools to specify which account to use.
    """.strip()
