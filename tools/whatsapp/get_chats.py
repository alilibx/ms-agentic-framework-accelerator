"""Get WhatsApp chats/conversations tool."""

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
    description="Get list of WhatsApp chats/conversations",
    tags=["whatsapp", "chats", "conversations", "list"],
    mock=not USE_REAL_WHATSAPP,
)
def get_whatsapp_chats(
    limit: Annotated[int, "Maximum number of chats to retrieve"] = 20,
) -> str:
    """Get list of WhatsApp chats/conversations.

    Args:
        limit: Maximum number of chats to retrieve

    Returns:
        Formatted string with chat list

    Example:
        >>> get_whatsapp_chats(limit=10)
        "💬 **WhatsApp Chats** (10 chats)

        1. 📱 John Doe
           🔔 Unread: 3 messages
           ⏰ Last activity: 2025-11-22 14:30

        2. 👥 Project Team (Group)
           🔔 Unread: 5 messages
           ⏰ Last activity: 2025-11-22 13:15
        ..."
    """
    if USE_REAL_WHATSAPP and is_whatsapp_configured():
        try:
            client = get_whatsapp_client()

            if not client.is_authenticated():
                return "⚠️ **WhatsApp not authenticated!** Please scan QR code first."

            chats = client.get_chats(limit=limit)

            if not chats:
                return "📭 **No WhatsApp chats found.**"

            result = [f"💬 **WhatsApp Chats** ({len(chats)} {'chat' if len(chats) == 1 else 'chats'})\n"]

            for i, chat in enumerate(chats, 1):
                # Format timestamp
                try:
                    ts = datetime.fromtimestamp(chat.get('timestamp', 0))
                    time_str = ts.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = 'Unknown'

                # Chat type
                chat_type = "👥" if chat.get('isGroup') else "📱"
                group_label = " (Group)" if chat.get('isGroup') else ""

                # Unread count
                unread = chat.get('unreadCount', 0)
                unread_str = f"🔔 Unread: {unread} {'message' if unread == 1 else 'messages'}" if unread > 0 else "✅ All read"

                result.append(f"""
{i}. {chat_type} **{chat.get('name', 'Unknown')}**{group_label}
   {unread_str}
   ⏰ **Last activity:** {time_str}
                """.strip())

            return "\n\n".join(result)

        except Exception as e:
            return f"⚠️ **WhatsApp error (using mock):** {str(e)}\n\n" + _get_chats_mock(limit)

    # Mock implementation
    return _get_chats_mock(limit)


def _get_chats_mock(limit: int = 20) -> str:
    """Mock implementation of getting WhatsApp chats."""
    mock_chats = [
        {"name": "John Doe", "is_group": False, "unread": 3},
        {"name": "Project Team", "is_group": True, "unread": 5},
        {"name": "Mom ❤️", "is_group": False, "unread": 0},
        {"name": "Work Group", "is_group": True, "unread": 12},
        {"name": "Friend", "is_group": False, "unread": 1},
        {"name": "Family", "is_group": True, "unread": 0},
        {"name": "Boss", "is_group": False, "unread": 2},
        {"name": "Sports Team", "is_group": True, "unread": 8},
    ]

    chats = mock_chats[:min(limit, len(mock_chats))]

    result = [f"💬 **WhatsApp Chats** ({len(chats)} {'chat' if len(chats) == 1 else 'chats'})\n"]

    for i, chat in enumerate(chats, 1):
        hours_ago = random.randint(1, 48)
        timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")

        chat_type = "👥" if chat.get("is_group") else "📱"
        group_label = " (Group)" if chat.get("is_group") else ""

        unread = chat.get("unread", 0)
        unread_str = f"🔔 Unread: {unread} {'message' if unread == 1 else 'messages'}" if unread > 0 else "✅ All read"

        result.append(f"""
{i}. {chat_type} **{chat['name']}**{group_label}
   {unread_str}
   ⏰ **Last activity:** {timestamp}
        """.strip())

    return "\n\n".join(result)
