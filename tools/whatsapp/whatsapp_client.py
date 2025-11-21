"""WhatsApp Web client for Python using whatsapp-web.js bridge.

This module provides a Python interface to WhatsApp Web via a Node.js bridge.

Setup:
1. Install Node.js (https://nodejs.org/)
2. Install whatsapp-web.js:
   cd tools/whatsapp/bridge
   npm install whatsapp-web.js qrcode-terminal

3. Set environment variables:
   - USE_WHATSAPP_API=true
   - WHATSAPP_SESSION_PATH=./whatsapp_session

Usage:
The client starts a Node.js subprocess running whatsapp-web.js and communicates
via JSON-RPC over HTTP.
"""

import os
import json
import time
import subprocess
import requests
from typing import Optional, List, Dict
from pathlib import Path
import signal
import atexit


WHATSAPP_AVAILABLE = True  # We'll check at runtime

class WhatsAppClient:
    """WhatsApp Web client using Node.js bridge."""

    def __init__(self, session_path: Optional[str] = None, port: int = 3123):
        """Initialize WhatsApp client.

        Args:
            session_path: Path to store WhatsApp session data
            port: Port for Node.js bridge server (default: 3123)
        """
        self.session_path = session_path or os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
        self.port = port
        self.base_url = f"http://localhost:{self.port}"

        self._process = None
        self._is_ready = False

        # Ensure session directory exists
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

        # Register cleanup
        atexit.register(self.cleanup)

    def start(self):
        """Start the WhatsApp Web bridge server."""
        if self._process is not None:
            return  # Already running

        # Path to bridge script
        bridge_path = Path(__file__).parent / 'bridge' / 'server.js'

        if not bridge_path.exists():
            raise FileNotFoundError(
                f"WhatsApp bridge script not found at {bridge_path}. "
                "Please ensure the bridge is set up correctly."
            )

        # Start Node.js bridge process
        try:
            self._process = subprocess.Popen(
                ['node', str(bridge_path)],
                env={
                    **os.environ,
                    'WHATSAPP_SESSION_PATH': self.session_path,
                    'BRIDGE_PORT': str(self.port)
                },
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to be ready
            self._wait_for_ready()

        except FileNotFoundError:
            raise Exception(
                "Node.js not found. Please install Node.js from https://nodejs.org/"
            )
        except Exception as e:
            raise Exception(f"Failed to start WhatsApp bridge: {e}")

    def _wait_for_ready(self, timeout: int = 30):
        """Wait for bridge server to be ready."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    self._is_ready = True
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)

        raise TimeoutError("WhatsApp bridge failed to start within timeout period")

    def cleanup(self):
        """Cleanup and terminate bridge process."""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except:
                self._process.kill()
            self._process = None

    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make request to WhatsApp bridge.

        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data

        Returns:
            Response data as dictionary
        """
        if not self._is_ready:
            self.start()

        url = f"{self.base_url}/{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)

            if response.status_code >= 400:
                raise Exception(f"WhatsApp API error ({response.status_code}): {response.text}")

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to communicate with WhatsApp bridge: {e}")

    def get_qr_code(self) -> str:
        """Get QR code for WhatsApp authentication.

        Returns:
            QR code as ASCII art or status message
        """
        try:
            response = self._make_request('qr')
            return response.get('qr', 'QR code not available')
        except Exception as e:
            return f"Error getting QR code: {e}"

    def is_authenticated(self) -> bool:
        """Check if WhatsApp is authenticated.

        Returns:
            True if authenticated
        """
        try:
            response = self._make_request('status')
            return response.get('authenticated', False)
        except:
            return False

    def send_message(
        self,
        to: str,
        message: str
    ) -> Dict:
        """Send WhatsApp message.

        Args:
            to: Phone number with country code (e.g., '1234567890@c.us') or contact name
            message: Message text

        Returns:
            Dictionary with send status
        """
        try:
            # Format phone number if needed
            if not to.endswith('@c.us') and not to.endswith('@g.us'):
                # Assume it's a phone number
                to = to.replace('+', '').replace('-', '').replace(' ', '')
                to = f"{to}@c.us"

            response = self._make_request(
                'send',
                method='POST',
                data={'to': to, 'message': message}
            )

            return {
                'success': response.get('success', False),
                'to': to,
                'message': message,
                'timestamp': response.get('timestamp'),
                'message_id': response.get('id')
            }

        except Exception as error:
            return {
                'success': False,
                'error': str(error),
                'to': to,
                'message': message
            }

    def read_messages(
        self,
        limit: int = 10,
        filter_unread: bool = False
    ) -> List[Dict]:
        """Read recent WhatsApp messages.

        Args:
            limit: Maximum number of messages to retrieve
            filter_unread: If True, only return unread messages

        Returns:
            List of message dictionaries
        """
        try:
            response = self._make_request(
                'messages',
                method='POST',
                data={'limit': limit, 'unreadOnly': filter_unread}
            )

            messages = response.get('messages', [])

            # Parse messages into standardized format
            parsed_messages = []
            for msg in messages:
                parsed_messages.append(self._parse_message(msg))

            return parsed_messages

        except Exception as error:
            raise Exception(f"Failed to read messages: {error}")

    def search_messages(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search WhatsApp messages.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching messages
        """
        try:
            response = self._make_request(
                'search',
                method='POST',
                data={'query': query, 'limit': limit}
            )

            messages = response.get('messages', [])

            # Parse messages
            parsed_messages = []
            for msg in messages:
                parsed_messages.append(self._parse_message(msg))

            return parsed_messages

        except Exception as error:
            raise Exception(f"Search failed: {error}")

    def get_chats(self, limit: int = 20) -> List[Dict]:
        """Get list of chats.

        Args:
            limit: Maximum number of chats

        Returns:
            List of chat dictionaries
        """
        try:
            response = self._make_request(
                'chats',
                method='POST',
                data={'limit': limit}
            )

            return response.get('chats', [])

        except Exception as error:
            raise Exception(f"Failed to get chats: {error}")

    def _parse_message(self, message: Dict) -> Dict:
        """Parse WhatsApp message into standardized format.

        Args:
            message: Raw WhatsApp message

        Returns:
            Parsed message dictionary
        """
        return {
            'id': message.get('id', {}).get('id', ''),
            'from': message.get('from', 'Unknown'),
            'to': message.get('to', ''),
            'body': message.get('body', ''),
            'preview': message.get('body', '')[:200],
            'timestamp': message.get('timestamp', 0),
            'is_group': message.get('isGroupMsg', False),
            'sender': message.get('sender', {}).get('pushname', 'Unknown'),
            'chat': message.get('chatId', ''),
            'unread': not message.get('isRead', True)
        }


def get_whatsapp_client() -> Optional[WhatsAppClient]:
    """Get WhatsApp client instance.

    Returns:
        WhatsAppClient instance or None if not available
    """
    try:
        return WhatsAppClient()
    except Exception as e:
        print(f"WhatsApp not available: {e}")
        return None


def is_whatsapp_configured() -> bool:
    """Check if WhatsApp is properly configured.

    Returns:
        True if bridge is set up
    """
    bridge_path = Path(__file__).parent / 'bridge' / 'server.js'
    return bridge_path.exists()
