"""Read WhatsApp messages tool."""

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
    description="Read recent WhatsApp messages",
    tags=["whatsapp", "read", "messages", "inbox"],
    mock=not USE_REAL_WHATSAPP,
)
def read_whatsapp_messages(
    limit: Annotated[int, "Maximum number of messages to retrieve"] = 10,
    filter_unread: Annotated[bool, "Show only unread messages"] = False,
) -> str:
    """Read recent WhatsApp messages.

    Args:
        limit: Maximum number of messages to retrieve (default: 10)
        filter_unread: If True, show only unread messages

    Returns:
        Formatted string with WhatsApp messages

    Example:
        >>> read_whatsapp_messages(limit=5)
        "💬 **WhatsApp Messages** (5 messages)

        1. 📱 From: John Doe (+1234567890)
           💬 Message: Hey, how are you?
           ⏰ Received: 2025-11-22 14:30

        2. 👥 Group: Project Team
           👤 Sender: Alice
           💬 Message: Meeting at 3pm today
           ⏰ Received: 2025-11-22 13:15
        ..."
    """
    if USE_REAL_WHATSAPP and is_whatsapp_configured():
        try:
            client = get_whatsapp_client()

            if not client.is_authenticated():
                return "⚠️ **WhatsApp not authenticated!** Please scan QR code first."

            messages = client.read_messages(limit=limit, filter_unread=filter_unread)

            if not messages:
                return "📭 **No WhatsApp messages found** matching your criteria."

            header = "💬 **WhatsApp Unread Messages**" if filter_unread else "💬 **WhatsApp Messages**"
            result = [f"{header} ({len(messages)} {'message' if len(messages) == 1 else 'messages'})\n"]

            for i, msg in enumerate(messages, 1):
                # Format timestamp
                try:
                    ts = datetime.fromtimestamp(msg['timestamp'])
                    time_str = ts.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = 'Unknown'

                # Group or individual
                if msg.get('is_group'):
                    result.append(f"""
{i}. 👥 **Group:** {msg['chat']}
   👤 **Sender:** {msg['sender']}
   💬 **Message:** {msg['preview']}
   ⏰ **Received:** {time_str}
                    """.strip())
                else:
                    result.append(f"""
{i}. 📱 **From:** {msg['from']}
   💬 **Message:** {msg['preview']}
   ⏰ **Received:** {time_str}
                    """.strip())

            return "\n\n".join(result)

        except Exception as e:
            return f"⚠️ **WhatsApp error (using mock):** {str(e)}\n\n" + _read_messages_mock(limit, filter_unread)

    # Mock implementation
    return _read_messages_mock(limit, filter_unread)


def _read_messages_mock(limit: int = 10, filter_unread: bool = False) -> str:
    """Mock implementation of reading WhatsApp messages."""
    sample_messages = [
        {
            "from": "John Doe (+1234567890)",
            "message": "Hey, how are you doing today?",
            "is_group": False,
            "unread": True
        },
        {
            "from": "Project Team",
            "sender": "Alice",
            "message": "Meeting at 3pm today, don't forget!",
            "is_group": True,
            "unread": True
        },
        {
            "from": "Mom ❤️",
            "message": "Don't forget to call grandma",
            "is_group": False,
            "unread": False
        },
        {
            "from": "Work Group",
            "sender": "Boss",
            "message": "Need the report by EOD",
            "is_group": True,
            "unread": True
        },
        {
            "from": "Friend (+9876543210)",
            "message": "Want to grab coffee this weekend?",
            "is_group": False,
            "unread": False
        }
    ]

    # Filter if requested
    if filter_unread:
        messages = [m for m in sample_messages if m.get("unread")]
        header = "💬 **WhatsApp Unread Messages**"
    else:
        messages = sample_messages
        header = "💬 **WhatsApp Messages**"

    # Limit results
    messages = messages[:min(limit, len(messages))]

    if not messages:
        return "📭 **No WhatsApp messages found** matching your criteria."

    result = [f"{header} ({len(messages)} {'message' if len(messages) == 1 else 'messages'})\n"]

    for i, msg in enumerate(messages, 1):
        hours_ago = random.randint(1, 24)
        timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")

        if msg.get("is_group"):
            result.append(f"""
{i}. 👥 **Group:** {msg['from']}
   👤 **Sender:** {msg['sender']}
   💬 **Message:** {msg['message']}
   ⏰ **Received:** {timestamp}
            """.strip())
        else:
            status = "🟢" if msg.get("unread") else "⚪"
            result.append(f"""
{i}. {status} **From:** {msg['from']}
   💬 **Message:** {msg['message']}
   ⏰ **Received:** {timestamp}
            """.strip())

    return "\n\n".join(result)
