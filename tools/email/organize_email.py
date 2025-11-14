"""Organize email tool - Tag, categorize, and prioritize emails."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool


@tool(
    domain="email",
    description="Tag and organize emails by priority, category, or status",
    tags=["email", "organize", "tag", "label", "priority", "categorize"],
    mock=True,
)
def tag_email(
    email_id: Annotated[str, "Email ID or subject to tag"] = "",
    subject: Annotated[str, "Email subject to search for"] = "",
    tags: Annotated[str, "Comma-separated tags to apply (e.g., 'needs-response,urgent,important')"] = "",
    priority: Annotated[str, "Priority level: low, normal, high, urgent"] = "normal",
    category: Annotated[str, "Category: work, personal, finance, travel, etc."] = "",
) -> str:
    """Tag and organize an email for better inbox management.

    This is a mock implementation that simulates email tagging and organization.
    In production, this would integrate with Gmail labels, Outlook categories, etc.

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

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Build result
    email_identifier = email_id if email_id else f"Email matching '{subject}'"

    result = f"""
✅ **Email Tagged Successfully!**

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
    mock=True,
)
def bulk_tag_emails(
    filter_by: Annotated[str, "Filter criteria: sender, subject, date, unread"] = "unread",
    filter_value: Annotated[str, "Filter value (e.g., sender email, keyword)"] = "",
    tags: Annotated[str, "Tags to apply (e.g., 'needs-response,important')"] = "",
    priority: Annotated[str, "Priority to set: low, normal, high, urgent"] = "",
    limit: Annotated[int, "Maximum number of emails to tag"] = 10,
) -> str:
    """Bulk tag multiple emails based on filter criteria.

    This is a mock implementation that simulates bulk email tagging.
    In production, this would process multiple emails matching criteria.

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

    # Mock: Generate number of emails processed
    import random
    num_emails = random.randint(1, min(limit, 15))

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    result = f"""
✅ **Bulk Tagging Completed!**

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
    mock=True,
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

    This is a mock implementation of email filtering/rules.
    In production, this would create Gmail filters, Outlook rules, etc.

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

    result = f"""
✅ **Email Filter Created Successfully!**

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
    mock=True,
)
def get_inbox_summary(
    include_stats: Annotated[bool, "Include detailed statistics"] = True,
) -> str:
    """Get a summary of inbox organization and priorities.

    This is a mock implementation showing inbox organization status.
    In production, this would analyze your actual inbox.

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
    import random

    total = random.randint(30, 100)
    urgent = random.randint(2, 8)
    needs_response = random.randint(5, 20)
    important = random.randint(10, 25)
    unread = random.randint(5, 30)

    result = f"""
📊 **Inbox Organization Summary**

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
