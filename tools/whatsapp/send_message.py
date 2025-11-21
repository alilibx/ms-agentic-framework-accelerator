"""Send WhatsApp message tool."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool
import os

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
    description="Send a WhatsApp message to a contact or phone number",
    tags=["whatsapp", "send", "message", "chat"],
    mock=not USE_REAL_WHATSAPP,
)
def send_whatsapp_message(
    to: Annotated[str, "Phone number (with country code, e.g., '1234567890') or contact name"],
    message: Annotated[str, "Message text to send"],
) -> str:
    """Send a WhatsApp message to a contact or phone number.

    Args:
        to: Phone number with country code (e.g., '1234567890') or contact name
        message: Message text to send

    Returns:
        Formatted string confirming message was sent

    Example:
        >>> send_whatsapp_message("1234567890", "Hello from AI agent!")
        "✅ WhatsApp message sent successfully!
        📱 To: 1234567890
        💬 Message: Hello from AI agent!
        ⏰ Sent: 2025-11-22 15:30:00"
    """
    if USE_REAL_WHATSAPP and is_whatsapp_configured():
        try:
            client = get_whatsapp_client()

            # Check if authenticated
            if not client.is_authenticated():
                return """
⚠️ **WhatsApp not authenticated!**

Please authenticate by:
1. Run the WhatsApp bridge: `cd tools/whatsapp/bridge && node server.js`
2. Scan the QR code displayed in the terminal with your WhatsApp mobile app
3. Wait for authentication confirmation
4. Try sending the message again
                """.strip()

            result = client.send_message(to, message)

            if result['success']:
                return f"""
✅ **WhatsApp Message Sent Successfully!**

📱 **To:** {to}
💬 **Message:** {message[:100]}{'...' if len(message) > 100 else ''}
⏰ **Sent:** {result.get('timestamp', 'now')}
🔢 **Message ID:** {result.get('message_id', 'N/A')}
                """.strip()
            else:
                return f"❌ **Failed to send WhatsApp message:** {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"⚠️ **WhatsApp error (using mock):** {str(e)}\n\n" + _send_message_mock(to, message)

    # Mock implementation
    return _send_message_mock(to, message)


def _send_message_mock(to: str, message: str) -> str:
    """Mock implementation of WhatsApp message sending."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
✅ **WhatsApp Message Sent Successfully!** (MOCK)

📱 **To:** {to}
💬 **Message:** {message[:100]}{'...' if len(message) > 100 else ''}
⏰ **Sent:** {timestamp}
🔢 **Message ID:** WA-MSG-{hash(f'{to}{message}{timestamp}') % 100000}

💡 **Note:** This is a mock response. To send real WhatsApp messages:
1. Install Node.js dependencies: `cd tools/whatsapp/bridge && npm install`
2. Set USE_WHATSAPP_API=true in .env
3. Start the bridge and authenticate with QR code
    """.strip()
