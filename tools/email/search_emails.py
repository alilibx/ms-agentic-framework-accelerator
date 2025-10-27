"""Search emails tool - Find emails by query."""

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
    description="Search emails by keyword, sender, or subject",
    tags=["email", "search", "find", "query"],
    mock=not USE_REAL_GMAIL,
)
def search_emails(
    query: Annotated[str, "Search query (keywords, sender, or subject)"],
    search_in: Annotated[str, "Where to search: 'all', 'subject', 'from', 'body'"] = "all",
) -> str:
    """Search emails by keyword, sender, or subject.

    Supports both Gmail API (when configured) and mock mode.

    Args:
        query: Search query string
        search_in: Where to search - 'all', 'subject', 'from', 'body'

    Returns:
        Formatted string with search results

    Example:
        >>> search_emails("project", search_in="subject")
        "🔍 **Search Results for 'project' in subject**

        Found 2 matching emails:

        1. From: boss@company.com
           📝 Subject: **Project** Update Required
           ⏰ Received: 2025-10-24 14:30
        ..."
    """
    # Try real Gmail if configured
    if USE_REAL_GMAIL and is_gmail_configured():
        try:
            gmail = get_gmail_client()
            emails = gmail.search_emails(query=query, search_in=search_in, limit=20)

            search_scope = f"in {search_in}" if search_in != "all" else "everywhere"
            header = f"🔍 **Search Results for '{query}' {search_scope}** (via Gmail)\n"

            if not emails:
                return header + "\n❌ No emails found matching your query."

            result_text = [header, f"\nFound {len(emails)} matching {'email' if len(emails) == 1 else 'emails'}:\n"]

            for i, email in enumerate(emails, 1):
                # Highlight query in subject
                highlighted_subject = email["subject"]
                if query.lower() in email["subject"].lower():
                    highlighted_subject = email["subject"].replace(
                        query, f"**{query}**"
                    )

                result_text.append(f"""
{i}. 📧 **From:** {email['from']}
   📝 **Subject:** {highlighted_subject}
   💬 **Preview:** {email['preview']}
   ⏰ **Received:** {email['received']}
                """.strip())

            return "\n\n".join(result_text)

        except Exception as e:
            # Fall back to mock if Gmail fails
            return f"⚠️ **Gmail error (using mock):** {str(e)}\n\n" + _search_emails_mock(query, search_in)

    # Mock implementation
    return _search_emails_mock(query, search_in)


def _search_emails_mock(query: str, search_in: str = "all") -> str:
    """Mock implementation of email search.

    Args:
        query: Search query string
        search_in: Where to search

    Returns:
        Formatted mock search results
    """
    # Mock search results based on query
    search_results = {
        "project": [
            {
                "from": "boss@company.com",
                "subject": "Project Update Required",
                "preview": "Hi, can you provide an update on the Q4 project status...",
                "match_score": 0.95
            },
            {
                "from": "pm@company.com",
                "subject": "New Project Assignment",
                "preview": "You've been assigned to the new mobile app project...",
                "match_score": 0.90
            },
        ],
        "meeting": [
            {
                "from": "client@bigcorp.com",
                "subject": "Meeting Confirmation - Tomorrow 2PM",
                "preview": "Looking forward to our meeting tomorrow to discuss...",
                "match_score": 0.98
            },
        ],
        "review": [
            {
                "from": "notifications@github.com",
                "subject": "Pull Request Review Requested",
                "preview": "johndoe requested your review on PR #142...",
                "match_score": 0.92
            },
        ],
    }

    # Find matching results (case-insensitive)
    query_lower = query.lower()
    results = []

    for keyword, emails in search_results.items():
        if query_lower in keyword or keyword in query_lower:
            results.extend(emails)

    # If no specific matches, return generic results
    if not results:
        results = [
            {
                "from": "notifications@system.com",
                "subject": f"Results for '{query}'",
                "preview": "No exact matches found, showing related results...",
                "match_score": 0.5
            }
        ]

    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)

    # Build response
    search_scope = f"in {search_in}" if search_in != "all" else "everywhere"
    header = f"🔍 **Search Results for '{query}' {search_scope}**\n"

    if not results:
        return header + "\n❌ No emails found matching your query."

    result_text = [header, f"\nFound {len(results)} matching {'email' if len(results) == 1 else 'emails'}:\n"]

    for i, email in enumerate(results, 1):
        # Generate realistic timestamp
        hours_ago = random.randint(1, 72)
        timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")

        # Highlight query in subject (mock)
        highlighted_subject = email["subject"].replace(
            query.title(),
            f"**{query.title()}**"
        )

        result_text.append(f"""
{i}. 📧 **From:** {email['from']}
   📝 **Subject:** {highlighted_subject}
   💬 **Preview:** {email['preview']}
   ⏰ **Received:** {timestamp}
   🎯 **Relevance:** {int(email['match_score'] * 100)}%
        """.strip())

    return "\n\n".join(result_text)
