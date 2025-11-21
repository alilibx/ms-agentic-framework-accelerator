"""Search WhatsApp messages tool."""

from typing import Annotated
from datetime import datetime, timedelta
import random
import os
from tools._decorators import tool

# Try to import WhatsApp client
try:
    from .whatsapp_client import get_whatsapp_client, is_whatsapp_configured
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    is_whatsapp_configured = lambda: False


USE_REAL_WHATSAPP = os.getenv("USE_WHATSAPP_API", "false").lower() == "true" and WHATSAPP_AVAILABLE


@tool(
    domain="whatsapp",
    description="Search WhatsApp messages by keyword or phrase",
    tags=["whatsapp", "search", "find", "query"],
    mock=not USE_REAL_WHATSAPP,
)
def search_whatsapp_messages(
    query: Annotated[str, "Search query (keyword or phrase)"],
    limit: Annotated[int, "Maximum number of results"] = 20,
) -> str:
    """Search WhatsApp messages by keyword or phrase.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted string with search results

    Example:
        >>> search_whatsapp_messages("meeting")
        "🔍 **WhatsApp Search Results for 'meeting'**

        Found 3 matching messages:

        1. 👥 Group: Project Team
           👤 Sender: Alice
           💬 Message: **Meeting** at 3pm today
           ⏰ Received: 2025-11-22 13:15
        ..."
    """
    if USE_REAL_WHATSAPP and is_whatsapp_configured():
        try:
            client = get_whatsapp_client()

            if not client.is_authenticated():
                return "⚠️ **WhatsApp not authenticated!** Please scan QR code first."

            messages = client.search_messages(query=query, limit=limit)

            header = f"🔍 **WhatsApp Search Results for '{query}'**\n"

            if not messages:
                return header + "\n❌ No messages found matching your query."

            result_text = [header, f"\nFound {len(messages)} matching {'message' if len(messages) == 1 else 'messages'}:\n"]

            for i, msg in enumerate(messages, 1):
                # Format timestamp
                try:
                    ts = datetime.fromtimestamp(msg['timestamp'])
                    time_str = ts.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = 'Unknown'

                # Highlight query in message (simple)
                highlighted = msg['body']
                if query.lower() in msg['body'].lower():
                    # Case-insensitive highlight
                    import re
                    highlighted = re.sub(
                        f"({re.escape(query)})",
                        r"**\1**",
                        msg['body'],
                        flags=re.IGNORECASE
                    )

                if msg.get('is_group'):
                    result_text.append(f"""
{i}. 👥 **Group:** {msg['chat']}
   👤 **Sender:** {msg['sender']}
   💬 **Message:** {highlighted[:200]}
   ⏰ **Received:** {time_str}
                    """.strip())
                else:
                    result_text.append(f"""
{i}. 📱 **From:** {msg['from']}
   💬 **Message:** {highlighted[:200]}
   ⏰ **Received:** {time_str}
                    """.strip())

            return "\n\n".join(result_text)

        except Exception as e:
            return f"⚠️ **WhatsApp error (using mock):** {str(e)}\n\n" + _search_messages_mock(query, limit)

    # Mock implementation
    return _search_messages_mock(query, limit)


def _search_messages_mock(query: str, limit: int = 20) -> str:
    """Mock implementation of WhatsApp message search."""
    # Mock search results
    search_results = {
        "meeting": [
            {
                "from": "Project Team",
                "sender": "Alice",
                "message": "Meeting at 3pm today, don't forget!",
                "is_group": True
            },
            {
                "from": "Boss",
                "sender": "Boss",
                "message": "Can we schedule a meeting for tomorrow?",
                "is_group": False
            }
        ],
        "coffee": [
            {
                "from": "Friend",
                "sender": "Friend",
                "message": "Want to grab coffee this weekend?",
                "is_group": False
            }
        ],
        "report": [
            {
                "from": "Work Group",
                "sender": "Boss",
                "message": "Need the report by EOD",
                "is_group": True
            }
        ]
    }

    # Find matching results
    query_lower = query.lower()
    results = []

    for keyword, messages in search_results.items():
        if query_lower in keyword or keyword in query_lower:
            results.extend(messages)

    # If no specific matches, return generic
    if not results:
        results = [{
            "from": "Search Results",
            "sender": "System",
            "message": f"Results for '{query}' (no exact matches in mock data)",
            "is_group": False
        }]

    results = results[:limit]

    header = f"🔍 **WhatsApp Search Results for '{query}'**\n"

    if not results:
        return header + "\n❌ No messages found matching your query."

    result_text = [header, f"\nFound {len(results)} matching {'message' if len(results) == 1 else 'messages'}:\n"]

    for i, msg in enumerate(results, 1):
        hours_ago = random.randint(1, 72)
        timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")

        # Simple highlight
        highlighted = msg["message"].replace(query.title(), f"**{query.title()}**")

        if msg.get("is_group"):
            result_text.append(f"""
{i}. 👥 **Group:** {msg['from']}
   👤 **Sender:** {msg['sender']}
   💬 **Message:** {highlighted}
   ⏰ **Received:** {timestamp}
            """.strip())
        else:
            result_text.append(f"""
{i}. 📱 **From:** {msg['from']}
   💬 **Message:** {highlighted}
   ⏰ **Received:** {timestamp}
            """.strip())

    return "\n\n".join(result_text)
