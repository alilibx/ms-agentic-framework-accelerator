"""Organize email tool - Tag, categorize, and prioritize emails."""

from typing import Annotated
from datetime import datetime
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
    description="Tag and organize emails by priority, category, or status",
    tags=["email", "organize", "tag", "label", "priority", "categorize"],
    mock=not USE_REAL_GMAIL,
)
def tag_email(
    email_id: Annotated[str, "Email ID or subject to tag"] = "",
    subject: Annotated[str, "Email subject to search for"] = "",
    tags: Annotated[str, "Comma-separated tags to apply (e.g., 'needs-response,urgent,important')"] = "",
    priority: Annotated[str, "Priority level: low, normal, high, urgent"] = "normal",
    category: Annotated[str, "Category: work, personal, finance, travel, etc."] = "",
) -> str:
    """Tag and organize an email for better inbox management.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        email_id: Unique email identifier (e.g., MSG-12345)
        subject: Email subject to search for (if email_id not provided)
        tags: Comma-separated list of tags to apply
        priority: Priority level (low, normal, high, urgent)
        category: Email category for organization

    Returns:
        Formatted string confirming email tagging

    Example:
        >>> tag_email(subject="Project Update", tags="needs-response,urgent", priority="high")
        "✅ Email Tagged Successfully!
        📧 Subject: Project Update
        🏷️  Tags: needs-response, urgent
        ⚡ Priority: High"
    """
    if not email_id and not subject:
        return "❌ **Error:** Please provide either email_id or subject to tag."

    if not tags and not priority and not category:
        return "❌ **Error:** Please specify at least one: tags, priority, or category."

    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            return _tag_email_real(email_id, subject, tags, priority, category)
        except Exception as e:
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _tag_email_mock(email_id, subject, tags, priority, category)

    # Mock implementation
    return _tag_email_mock(email_id, subject, tags, priority, category)


def _tag_email_real(
    email_id: str = "",
    subject: str = "",
    tags: str = "",
    priority: str = "normal",
    category: str = ""
) -> str:
    """Real Gmail API implementation of email tagging."""
    gmail = get_gmail_client()

    # If subject provided instead of email_id, search for the email
    if not email_id and subject:
        emails = gmail.search_emails(query=subject, search_in="subject", limit=1)
        if not emails:
            return f"❌ **Error:** No email found with subject '{subject}'"
        email_id = emails[0]['id']
        actual_subject = emails[0]['subject']
    elif email_id:
        # Fetch email to get subject
        try:
            msg = gmail.service.users().messages().get(userId='me', id=email_id, format='metadata').execute()
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            actual_subject = headers.get('Subject', '(No Subject)')
        except:
            actual_subject = subject or "(Unknown)"
    else:
        actual_subject = subject

    # Build list of labels to apply
    label_names = []

    # Add tags as labels
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        label_names.extend(tag_list)

    # Add priority label
    if priority and priority.lower() != "normal":
        label_names.append(f"Priority-{priority.title()}")

    # Add category label
    if category:
        label_names.append(f"Category-{category.title()}")

    # Apply labels via Gmail API
    result_data = gmail.add_labels_to_message(email_id, label_names)

    if not result_data['success']:
        return f"❌ **Error:** Failed to tag email: {result_data.get('error', 'Unknown error')}"

    # Build success response
    result = f"""
✅ **Email Tagged Successfully!** (via Gmail)

📧 **Email ID:** {email_id}
📝 **Subject:** {actual_subject}
    """.strip()

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    if tag_list:
        result += f"\n\n🏷️  **Tags Applied ({len(tag_list)}):**"
        for tag in tag_list:
            # Add emoji based on tag type
            if "urgent" in tag.lower() or "important" in tag.lower():
                emoji = "🔴"
            elif "needs-response" in tag.lower() or "reply" in tag.lower():
                emoji = "💬"
            elif "follow-up" in tag.lower():
                emoji = "🔄"
            elif "waiting" in tag.lower():
                emoji = "⏳"
            else:
                emoji = "🏷️"
            result += f"\n   {emoji} {tag}"

    if priority and priority.lower() != "normal":
        priority_emojis = {
            "low": "🟢",
            "normal": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }
        emoji = priority_emojis.get(priority.lower(), "⚪")
        result += f"\n\n⚡ **Priority:** {emoji} {priority.title()}"

    if category:
        category_emojis = {
            "work": "💼",
            "personal": "👤",
            "finance": "💰",
            "travel": "✈️",
            "shopping": "🛒",
            "health": "🏥",
            "family": "👨‍👩‍👧‍👦"
        }
        emoji = category_emojis.get(category.lower(), "📁")
        result += f"\n\n📁 **Category:** {emoji} {category.title()}"

    result += f"\n\n⏰ **Tagged at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Add helpful suggestions
    if any("needs-response" in tag.lower() for tag in tag_list):
        result += "\n\n💡 **Reminder:** This email requires a response. Set a follow-up reminder?"

    if priority.lower() == "urgent":
        result += "\n\n⚠️  **Urgent Priority:** This email has been flagged for immediate attention!"

    return result


def _tag_email_mock(
    email_id: str = "",
    subject: str = "",
    tags: str = "",
    priority: str = "normal",
    category: str = ""
) -> str:
    """Mock implementation of email tagging."""
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Build result
    email_identifier = email_id if email_id else f"Email matching '{subject}'"

    result = f"""
✅ **Email Tagged Successfully!** (MOCK)

📧 **Email:** {email_identifier}
    """.strip()

    if subject:
        result += f"\n📝 **Subject:** {subject}"

    if tag_list:
        result += f"\n🏷️  **Tags Applied ({len(tag_list)}):**"
        for tag in tag_list:
            # Add emoji based on tag type
            if "urgent" in tag.lower() or "important" in tag.lower():
                emoji = "🔴"
            elif "needs-response" in tag.lower() or "reply" in tag.lower():
                emoji = "💬"
            elif "follow-up" in tag.lower():
                emoji = "🔄"
            elif "waiting" in tag.lower():
                emoji = "⏳"
            else:
                emoji = "🏷️"

            result += f"\n   {emoji} {tag}"

    if priority:
        priority_emojis = {
            "low": "🟢",
            "normal": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }
        emoji = priority_emojis.get(priority.lower(), "⚪")
        result += f"\n⚡ **Priority:** {emoji} {priority.title()}"

    if category:
        category_emojis = {
            "work": "💼",
            "personal": "👤",
            "finance": "💰",
            "travel": "✈️",
            "shopping": "🛒",
            "health": "🏥",
            "family": "👨‍👩‍👧‍👦"
        }
        emoji = category_emojis.get(category.lower(), "📁")
        result += f"\n📁 **Category:** {emoji} {category.title()}"

    result += f"\n\n⏰ **Tagged at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Add helpful suggestions
    if any("needs-response" in tag.lower() for tag in tag_list):
        result += "\n\n💡 **Reminder:** This email requires a response. Set a follow-up reminder?"

    if priority.lower() == "urgent":
        result += "\n\n⚠️  **Urgent Priority:** This email has been flagged for immediate attention!"

    return result


@tool(
    domain="email",
    description="Mark multiple emails as requiring response or attention",
    tags=["email", "organize", "bulk", "triage", "priority", "needs-response"],
    mock=not USE_REAL_GMAIL,
)
def bulk_tag_emails(
    filter_by: Annotated[str, "Filter criteria: sender, subject, date, unread"] = "unread",
    filter_value: Annotated[str, "Filter value (e.g., sender email, keyword)"] = "",
    tags: Annotated[str, "Tags to apply (e.g., 'needs-response,important')"] = "",
    priority: Annotated[str, "Priority to set: low, normal, high, urgent"] = "",
    limit: Annotated[int, "Maximum number of emails to tag"] = 10,
) -> str:
    """Bulk tag multiple emails based on filter criteria.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        filter_by: How to filter emails (sender, subject, date, unread)
        filter_value: Value to match (sender email, keyword, etc.)
        tags: Comma-separated tags to apply
        priority: Priority level to set
        limit: Maximum emails to process

    Returns:
        Formatted string with bulk tagging summary

    Example:
        >>> bulk_tag_emails(filter_by="sender", filter_value="boss@company.com",
                           tags="needs-response", priority="high")
        "✅ Tagged 5 emails from boss@company.com"
    """
    if not tags and not priority:
        return "❌ **Error:** Please specify tags or priority to apply."

    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            return _bulk_tag_emails_real(filter_by, filter_value, tags, priority, limit)
        except Exception as e:
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _bulk_tag_emails_mock(filter_by, filter_value, tags, priority, limit)

    # Mock implementation
    return _bulk_tag_emails_mock(filter_by, filter_value, tags, priority, limit)


def _bulk_tag_emails_real(
    filter_by: str = "unread",
    filter_value: str = "",
    tags: str = "",
    priority: str = "",
    limit: int = 10
) -> str:
    """Real Gmail API implementation of bulk email tagging."""
    gmail = get_gmail_client()

    # Build Gmail query based on filter criteria
    if filter_by == "sender" and filter_value:
        query = f"from:{filter_value}"
    elif filter_by == "subject" and filter_value:
        query = f"subject:{filter_value}"
    elif filter_by == "unread":
        query = "is:unread"
    elif filter_by == "date" and filter_value:
        query = f"after:{filter_value}"
    else:
        query = filter_value if filter_value else "in:inbox"

    # Search for matching emails
    emails = gmail.search_emails(query=query, limit=limit)

    if not emails:
        return f"❌ **No emails found** matching filter: {filter_by} = {filter_value or 'all'}"

    # Build list of labels to apply
    label_names = []
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    label_names.extend(tag_list)

    if priority and priority.lower() != "normal":
        label_names.append(f"Priority-{priority.title()}")

    # Apply labels to all matching emails
    success_count = 0
    failed_count = 0

    for email in emails:
        result_data = gmail.add_labels_to_message(email['id'], label_names)
        if result_data['success']:
            success_count += 1
        else:
            failed_count += 1

    # Build result
    result = f"""
✅ **Bulk Tagging Completed!** (via Gmail)

📊 **Summary:**
   • Emails processed: {len(emails)}
   • Successfully tagged: {success_count}
   • Failed: {failed_count}
   • Filter: {filter_by}
   • Criteria: {filter_value if filter_value else 'All ' + filter_by}
    """.strip()

    if tag_list:
        result += f"\n\n🏷️  **Tags Applied:**"
        for tag in tag_list:
            result += f"\n   • {tag}"

    if priority:
        priority_emojis = {
            "low": "🟢",
            "normal": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }
        emoji = priority_emojis.get(priority.lower(), "⚪")
        result += f"\n\n⚡ **Priority Set:** {emoji} {priority.title()}"

    result += f"\n\n⏰ **Completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return result


def _bulk_tag_emails_mock(
    filter_by: str = "unread",
    filter_value: str = "",
    tags: str = "",
    priority: str = "",
    limit: int = 10
) -> str:
    """Mock implementation of bulk email tagging."""
    import random
    num_emails = random.randint(1, min(limit, 15))

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    result = f"""
✅ **Bulk Tagging Completed!** (MOCK)

📊 **Summary:**
   • Emails processed: {num_emails}
   • Filter: {filter_by}
   • Criteria: {filter_value if filter_value else 'All ' + filter_by}
    """.strip()

    if tag_list:
        result += f"\n\n🏷️  **Tags Applied:**"
        for tag in tag_list:
            result += f"\n   • {tag}"

    if priority:
        priority_emojis = {
            "low": "🟢",
            "normal": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }
        emoji = priority_emojis.get(priority.lower(), "⚪")
        result += f"\n\n⚡ **Priority Set:** {emoji} {priority.title()}"

    result += f"\n\n⏰ **Completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Add breakdown
    result += f"\n\n📈 **Breakdown:**"
    result += f"\n   • Needs Response: {num_emails // 2}"
    result += f"\n   • Urgent: {num_emails // 3}"
    result += f"\n   • Already Handled: {num_emails - (num_emails // 2) - (num_emails // 3)}"

    return result


@tool(
    domain="email",
    description="Create smart filters to auto-organize incoming emails",
    tags=["email", "organize", "filter", "automation", "rules"],
    mock=not USE_REAL_GMAIL,
)
def create_email_filter(
    filter_name: Annotated[str, "Name for this filter rule"],
    criteria: Annotated[str, "Filter criteria: from, to, subject, body"],
    criteria_value: Annotated[str, "Value to match (email, keyword, etc.)"],
    action: Annotated[str, "Action: tag, move, star, archive, delete"] = "tag",
    action_value: Annotated[str, "Action parameter (tag name, folder, etc.)"] = "",
    auto_tag: Annotated[str, "Auto-tags to apply (comma-separated)"] = "",
) -> str:
    """Create automated email filter rules for smart organization.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        filter_name: Descriptive name for the filter
        criteria: What to match (from, to, subject, body)
        criteria_value: Value to match against
        action: What action to perform (tag, move, star, archive, delete)
        action_value: Parameter for the action (tag name, folder, etc.)
        auto_tag: Tags to automatically apply

    Returns:
        Formatted string confirming filter creation

    Example:
        >>> create_email_filter(
                filter_name="Boss Emails - Urgent",
                criteria="from",
                criteria_value="boss@company.com",
                action="tag",
                auto_tag="needs-response,urgent"
            )
    """
    if not filter_name or not criteria or not criteria_value:
        return "❌ **Error:** filter_name, criteria, and criteria_value are required."

    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            return _create_email_filter_real(filter_name, criteria, criteria_value, action, action_value, auto_tag)
        except Exception as e:
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _create_email_filter_mock(filter_name, criteria, criteria_value, action, action_value, auto_tag)

    # Mock implementation
    return _create_email_filter_mock(filter_name, criteria, criteria_value, action, action_value, auto_tag)


def _create_email_filter_real(
    filter_name: str,
    criteria: str,
    criteria_value: str,
    action: str = "tag",
    action_value: str = "",
    auto_tag: str = ""
) -> str:
    """Real Gmail API implementation of filter creation."""
    gmail = get_gmail_client()

    # Build Gmail filter criteria
    gmail_criteria = {}
    if criteria == "from":
        gmail_criteria['from'] = criteria_value
    elif criteria == "to":
        gmail_criteria['to'] = criteria_value
    elif criteria == "subject":
        gmail_criteria['subject'] = criteria_value
    elif criteria == "body":
        gmail_criteria['query'] = criteria_value

    # Build Gmail filter actions
    gmail_actions = {}

    # Handle auto-tags
    if auto_tag:
        tag_list = [t.strip() for t in auto_tag.split(",")]
        label_ids = [gmail.get_or_create_label(tag) for tag in tag_list]
        gmail_actions['addLabelIds'] = label_ids

    # Handle primary action
    if action == "tag" and action_value:
        label_id = gmail.get_or_create_label(action_value)
        if 'addLabelIds' in gmail_actions:
            gmail_actions['addLabelIds'].append(label_id)
        else:
            gmail_actions['addLabelIds'] = [label_id]
    elif action == "archive":
        gmail_actions['removeLabelIds'] = ['INBOX']
    elif action == "star":
        gmail_actions['addLabelIds'] = gmail_actions.get('addLabelIds', []) + ['STARRED']
    elif action == "delete":
        gmail_actions['addLabelIds'] = gmail_actions.get('addLabelIds', []) + ['TRASH']

    # Create filter via Gmail API
    result_data = gmail.create_filter(gmail_criteria, gmail_actions)

    if not result_data['success']:
        return f"❌ **Error:** Failed to create filter: {result_data.get('error', 'Unknown error')}"

    # Build success response
    result = f"""
✅ **Email Filter Created Successfully!** (via Gmail)

🔧 **Filter Name:** {filter_name}
🆔 **Filter ID:** {result_data['filter_id']}

📋 **Criteria:**
   • Match: {criteria}
   • Value: {criteria_value}

⚙️  **Actions:**
   • Primary: {action.title()}
    """.strip()

    if action_value:
        result += f"\n   • Target: {action_value}"

    if auto_tag:
        tag_list = [t.strip() for t in auto_tag.split(",")]
        result += f"\n\n🏷️  **Auto-Tags ({len(tag_list)}):**"
        for tag in tag_list:
            if "urgent" in tag.lower():
                emoji = "🔴"
            elif "needs-response" in tag.lower():
                emoji = "💬"
            elif "important" in tag.lower():
                emoji = "⭐"
            else:
                emoji = "🏷️"
            result += f"\n   {emoji} {tag}"

    result += f"\n\n📊 **Filter Status:** Active"
    result += f"\n⏰ **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    result += f"\n\n💡 **Example Matches:**"
    if criteria == "from":
        result += f"\n   • All emails from {criteria_value}"
    elif criteria == "subject":
        result += f"\n   • Emails with '{criteria_value}' in subject"
    elif criteria == "to":
        result += f"\n   • Emails sent to {criteria_value}"

    result += f"\n\n✨ **Tip:** This filter will automatically process all future emails!"

    return result


def _create_email_filter_mock(
    filter_name: str,
    criteria: str,
    criteria_value: str,
    action: str = "tag",
    action_value: str = "",
    auto_tag: str = ""
) -> str:
    """Mock implementation of filter creation."""
    result = f"""
✅ **Email Filter Created Successfully!** (MOCK)

🔧 **Filter Name:** {filter_name}

📋 **Criteria:**
   • Match: {criteria}
   • Value: {criteria_value}

⚙️  **Actions:**
   • Primary: {action.title()}
    """.strip()

    if action_value:
        result += f"\n   • Target: {action_value}"

    if auto_tag:
        tag_list = [t.strip() for t in auto_tag.split(",")]
        result += f"\n\n🏷️  **Auto-Tags ({len(tag_list)}):**"
        for tag in tag_list:
            # Tag-specific emojis
            if "urgent" in tag.lower():
                emoji = "🔴"
            elif "needs-response" in tag.lower():
                emoji = "💬"
            elif "important" in tag.lower():
                emoji = "⭐"
            else:
                emoji = "🏷️"
            result += f"\n   {emoji} {tag}"

    result += f"\n\n📊 **Filter Status:** Active"
    result += f"\n⏰ **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Add examples
    result += f"\n\n💡 **Example Matches:**"
    if criteria == "from":
        result += f"\n   • All emails from {criteria_value}"
    elif criteria == "subject":
        result += f"\n   • Emails with '{criteria_value}' in subject"
    elif criteria == "to":
        result += f"\n   • Emails sent to {criteria_value}"

    result += f"\n\n✨ **Tip:** This filter will automatically process all future emails!"

    return result


@tool(
    domain="email",
    description="Get organized inbox summary with priority breakdown",
    tags=["email", "organize", "summary", "dashboard", "overview"],
    mock=not USE_REAL_GMAIL,
)
def get_inbox_summary(
    include_stats: Annotated[bool, "Include detailed statistics"] = True,
) -> str:
    """Get a summary of inbox organization and priorities.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        include_stats: Include detailed statistics and breakdowns

    Returns:
        Formatted inbox organization summary

    Example:
        >>> get_inbox_summary(include_stats=True)
        "📊 Inbox Organization Summary
        Total: 45 emails
        🔴 Urgent: 3
        💬 Needs Response: 12..."
    """
    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            return _get_inbox_summary_real(include_stats)
        except Exception as e:
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _get_inbox_summary_mock(include_stats)

    # Mock implementation
    return _get_inbox_summary_mock(include_stats)


def _get_inbox_summary_real(include_stats: bool = True) -> str:
    """Real Gmail API implementation of inbox summary."""
    gmail = get_gmail_client()
    stats = gmail.get_inbox_stats()

    result = f"""
📊 **Inbox Organization Summary** (via Gmail)

📧 **Account:** {stats.get('email_address', 'Unknown')}
📬 **Total Messages:** {stats.get('total_messages', 0)}
🧵 **Total Threads:** {stats.get('total_threads', 0)}

🎯 **Inbox Status:**
   📭 **Unread:** {stats.get('unread_inbox', 0)} emails
   ⭐ **Important:** {stats.get('important', 0)} emails
   📥 **Inbox:** {stats.get('inbox', 'N/A')} emails
   📤 **Sent:** {stats.get('sent', 'N/A')} emails
    """.strip()

    if include_stats:
        result += f"""

📁 **System Labels:**
   • Draft: {stats.get('draft', 0)}
   • Spam: {stats.get('spam', 0)}
   • Trash: {stats.get('trash', 0)}

⚡ **Quick Actions Needed:**
   1. {stats.get('unread_inbox', 0)} unread emails to review
   2. {stats.get('important', 0)} important emails flagged

💡 **Recommendations:**
   • Create filters for recurring senders
   • Archive old emails to clean up inbox
   • Set up auto-tags for common categories
        """

    result += f"\n\n⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return result


def _get_inbox_summary_mock(include_stats: bool = True) -> str:
    """Mock implementation of inbox summary."""
    import random

    total = random.randint(30, 100)
    urgent = random.randint(2, 8)
    needs_response = random.randint(5, 20)
    important = random.randint(10, 25)
    unread = random.randint(5, 30)

    result = f"""
📊 **Inbox Organization Summary** (MOCK)

📬 **Total Emails:** {total}

🎯 **Priority Breakdown:**
   🔴 **Urgent:** {urgent} emails
   💬 **Needs Response:** {needs_response} emails
   ⭐ **Important:** {important} emails
   📭 **Unread:** {unread} emails

📁 **Categories:**
   💼 Work: {total // 2}
   👤 Personal: {total // 3}
   💰 Finance: {total // 5}
   🛒 Shopping: {total // 10}
    """.strip()

    if include_stats:
        result += f"""

📈 **Weekly Trends:**
   • Response Rate: {random.randint(60, 95)}%
   • Average Response Time: {random.randint(2, 24)} hours
   • Emails Organized: {random.randint(100, 300)}

⚡ **Quick Actions Needed:**
   1. {urgent} urgent emails require immediate attention
   2. {needs_response} emails waiting for your response
   3. {unread} unread emails to review

💡 **Recommendations:**
   • Create filters for recurring senders
   • Archive old emails from last month
   • Set up auto-tags for common categories
        """

    result += f"\n\n⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return result
