"""Microsoft Outlook/365 API utilities for email operations.

This module provides utilities for authenticating with Microsoft Graph API
and common email operations using Outlook/Microsoft 365.

Setup:
1. Go to https://portal.azure.com/
2. Register a new application in Azure AD
3. Add Microsoft Graph API permissions:
   - Mail.Read
   - Mail.Send
   - Mail.ReadWrite
4. Create a client secret
5. Set environment variables in .env:
   - OUTLOOK_TENANT_ID=your-tenant-id
   - OUTLOOK_CLIENT_ID=your-client-id
   - OUTLOOK_CLIENT_SECRET=your-client-secret
   - OUTLOOK_TOKEN_FILE=outlook_token.json
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Microsoft Graph API imports (optional - only loaded if needed)
try:
    import msal
    import requests
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False


# Microsoft Graph API scopes
SCOPES = [
    'Mail.Read',
    'Mail.Send',
    'Mail.ReadWrite',
    'User.Read'
]


class OutlookClient:
    """Microsoft Outlook/365 Graph API client for email operations."""

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        """Initialize Outlook client.

        Args:
            tenant_id: Azure AD tenant ID (default: from env)
            client_id: Azure AD application/client ID (default: from env)
            client_secret: Azure AD client secret (default: from env)
            token_file: Path to token cache file (default: from env)
        """
        if not OUTLOOK_AVAILABLE:
            raise ImportError(
                "Microsoft Graph API dependencies not installed. "
                "Install with: pip install msal requests"
            )

        self.tenant_id = tenant_id or os.getenv('OUTLOOK_TENANT_ID')
        self.client_id = client_id or os.getenv('OUTLOOK_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('OUTLOOK_CLIENT_SECRET')
        self.token_file = token_file or os.getenv('OUTLOOK_TOKEN_FILE', 'outlook_token.json')

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required Outlook credentials. "
                "Please set OUTLOOK_TENANT_ID, OUTLOOK_CLIENT_ID, and OUTLOOK_CLIENT_SECRET"
            )

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

        self._app = None
        self._token_cache = self._load_token_cache()
        self._access_token = None
        self._authenticate()

    def _load_token_cache(self) -> msal.SerializableTokenCache:
        """Load token cache from file."""
        cache = msal.SerializableTokenCache()

        if Path(self.token_file).exists():
            with open(self.token_file, 'r') as f:
                cache.deserialize(f.read())

        return cache

    def _save_token_cache(self):
        """Save token cache to file."""
        if self._token_cache.has_state_changed:
            with open(self.token_file, 'w') as f:
                f.write(self._token_cache.serialize())

    def _authenticate(self):
        """Authenticate with Microsoft Graph API."""
        # Create MSAL confidential client app
        self._app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
            token_cache=self._token_cache
        )

        # Try to acquire token silently first
        accounts = self._app.get_accounts()
        result = None

        if accounts:
            result = self._app.acquire_token_silent(
                scopes=SCOPES,
                account=accounts[0]
            )

        # If silent acquisition fails, use client credentials flow
        if not result:
            result = self._app.acquire_token_for_client(scopes=SCOPES)

        if 'access_token' in result:
            self._access_token = result['access_token']
            self._save_token_cache()
        else:
            error = result.get('error_description', result.get('error', 'Unknown error'))
            raise Exception(f"Failed to acquire access token: {error}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make authenticated request to Microsoft Graph API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (relative to graph_endpoint)
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }

        url = f"{self.graph_endpoint}/{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        )

        if response.status_code >= 400:
            raise Exception(f"Graph API error ({response.status_code}): {response.text}")

        return response.json() if response.text else {}

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        html: bool = False
    ) -> Dict:
        """Send an email via Outlook/Microsoft 365.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: Optional CC recipients (comma-separated)
            html: If True, send as HTML email

        Returns:
            Dictionary with send status and message details
        """
        try:
            # Build recipients list
            to_recipients = [{'emailAddress': {'address': addr.strip()}} for addr in to.split(',')]

            cc_recipients = []
            if cc:
                cc_recipients = [{'emailAddress': {'address': addr.strip()}} for addr in cc.split(',')]

            # Build message
            message = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'HTML' if html else 'Text',
                        'content': body
                    },
                    'toRecipients': to_recipients,
                    'ccRecipients': cc_recipients
                },
                'saveToSentItems': True
            }

            # Send via Graph API
            self._make_request('POST', 'me/sendMail', data=message)

            return {
                'success': True,
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat(),
                'message_id': 'sent'  # Graph API doesn't return message ID for sendMail
            }

        except Exception as error:
            return {
                'success': False,
                'error': str(error),
                'to': to,
                'subject': subject
            }

    def read_inbox(
        self,
        limit: int = 10,
        filter_unread: bool = False,
        folder: str = 'inbox'
    ) -> List[Dict]:
        """Read emails from inbox.

        Args:
            limit: Maximum number of emails to retrieve
            filter_unread: If True, only return unread emails
            folder: Folder to read from (default: inbox)

        Returns:
            List of email dictionaries with metadata and content
        """
        try:
            # Build query parameters
            params = {
                '$top': limit,
                '$orderby': 'receivedDateTime DESC',
                '$select': 'id,subject,from,toRecipients,receivedDateTime,bodyPreview,body,isRead'
            }

            if filter_unread:
                params['$filter'] = 'isRead eq false'

            # Get messages
            response = self._make_request('GET', f'me/mailFolders/{folder}/messages', params=params)

            messages = response.get('value', [])

            if not messages:
                return []

            # Parse messages
            emails = []
            for msg in messages:
                email_data = self._parse_message(msg)
                emails.append(email_data)

            return emails

        except Exception as error:
            raise Exception(f"Failed to read inbox: {error}")

    def search_emails(
        self,
        query: str,
        limit: int = 20,
        search_in: str = 'all'
    ) -> List[Dict]:
        """Search emails using Microsoft Graph search.

        Args:
            query: Search query
            limit: Maximum results to return
            search_in: Where to search ('all', 'subject', 'body', 'from')

        Returns:
            List of matching email dictionaries
        """
        try:
            # Build search query
            if search_in == 'subject':
                filter_query = f"subject:'{query}'"
            elif search_in == 'from':
                filter_query = f"from:'{query}'"
            elif search_in == 'body':
                filter_query = f"body:'{query}'"
            else:
                filter_query = query

            # Search using Graph API
            params = {
                '$search': f'"{filter_query}"',
                '$top': limit,
                '$orderby': 'receivedDateTime DESC',
                '$select': 'id,subject,from,toRecipients,receivedDateTime,bodyPreview,body,isRead'
            }

            response = self._make_request('GET', 'me/messages', params=params)

            messages = response.get('value', [])

            if not messages:
                return []

            # Parse messages
            emails = []
            for msg in messages:
                email_data = self._parse_message(msg)
                emails.append(email_data)

            return emails

        except Exception as error:
            raise Exception(f"Search failed: {error}")

    def _parse_message(self, message: Dict) -> Dict:
        """Parse Graph API message into a standardized format.

        Args:
            message: Raw Graph API message

        Returns:
            Parsed email dictionary
        """
        # Extract from address
        from_addr = message.get('from', {}).get('emailAddress', {})
        from_email = from_addr.get('address', 'Unknown')
        from_name = from_addr.get('name', from_email)

        # Extract to addresses
        to_recipients = message.get('toRecipients', [])
        to_emails = [r.get('emailAddress', {}).get('address', '') for r in to_recipients]
        to_str = ', '.join(to_emails)

        # Parse date
        received_date_str = message.get('receivedDateTime', '')
        try:
            received_date = datetime.fromisoformat(received_date_str.replace('Z', '+00:00'))
            formatted_date = received_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_date = received_date_str

        # Get body
        body_obj = message.get('body', {})
        body = body_obj.get('content', '')
        body_preview = message.get('bodyPreview', '')

        return {
            'id': message.get('id', ''),
            'thread_id': message.get('conversationId', ''),
            'from': f"{from_name} <{from_email}>",
            'to': to_str,
            'subject': message.get('subject', '(No Subject)'),
            'body': body[:500],  # Limit body length
            'preview': body_preview[:200] if body_preview else body[:200],
            'received': formatted_date,
            'unread': not message.get('isRead', False),
            'labels': [],  # Outlook uses categories, not labels
            'snippet': body_preview
        }

    def get_inbox_stats(self) -> Dict:
        """Get inbox statistics.

        Returns:
            Dictionary with inbox stats
        """
        try:
            # Get user profile
            profile = self._make_request('GET', 'me')

            # Get mail folders
            folders_response = self._make_request('GET', 'me/mailFolders')
            folders = folders_response.get('value', [])

            stats = {
                'email_address': profile.get('mail', profile.get('userPrincipalName', '')),
                'display_name': profile.get('displayName', ''),
            }

            # Get counts from folders
            for folder in folders:
                folder_name = folder.get('displayName', '').lower()
                if folder_name in ['inbox', 'sent items', 'deleted items', 'drafts', 'junk email']:
                    stats[folder_name.replace(' ', '_')] = folder.get('totalItemCount', 0)
                    stats[f'{folder_name.replace(" ", "_")}_unread'] = folder.get('unreadItemCount', 0)

            return stats

        except Exception as error:
            raise Exception(f"Failed to get inbox stats: {error}")


def get_outlook_client() -> Optional[OutlookClient]:
    """Get authenticated Outlook client.

    Returns:
        OutlookClient instance or None if credentials not configured
    """
    try:
        return OutlookClient()
    except (ValueError, ImportError) as e:
        print(f"Outlook not configured: {e}")
        return None


def is_outlook_configured() -> bool:
    """Check if Outlook is properly configured.

    Returns:
        True if credentials are set and dependencies are installed
    """
    if not OUTLOOK_AVAILABLE:
        return False

    required_vars = ['OUTLOOK_TENANT_ID', 'OUTLOOK_CLIENT_ID', 'OUTLOOK_CLIENT_SECRET']
    return all(os.getenv(var) for var in required_vars)
