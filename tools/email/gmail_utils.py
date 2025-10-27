"""Gmail API utilities for email operations.

This module provides utilities for authenticating with Gmail API
and common email operations using the Gmail API.

Setup:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json and place in project root
6. Set environment variables in .env:
   - GMAIL_CREDENTIALS_FILE=credentials.json
   - GMAIL_TOKEN_FILE=token.json
   - GMAIL_USER_EMAIL=your.email@gmail.com
"""

import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

# Gmail API imports (optional - only loaded if needed)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
]


class GmailClient:
    """Gmail API client for email operations."""

    def __init__(self, credentials_file: Optional[str] = None, token_file: Optional[str] = None):
        """Initialize Gmail client.

        Args:
            credentials_file: Path to credentials.json (default: from env)
            token_file: Path to token.json (default: from env)
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail API dependencies not installed. "
                "Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )

        self.credentials_file = credentials_file or os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = token_file or os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        self.user_email = os.getenv('GMAIL_USER_EMAIL', 'me')

        self._service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None

        # Token file stores user's access and refresh tokens
        if Path(self.token_file).exists():
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path(self.credentials_file).exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download from Google Cloud Console and place in project root."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        self._service = build('gmail', 'v1', credentials=creds)

    @property
    def service(self):
        """Get authenticated Gmail service."""
        return self._service

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        html: bool = False
    ) -> Dict:
        """Send an email via Gmail.

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
            message = MIMEMultipart() if cc else MIMEText(body, 'html' if html else 'plain')

            if cc:
                message = MIMEMultipart()
                message.attach(MIMEText(body, 'html' if html else 'plain'))

            message['To'] = to
            message['From'] = self.user_email
            message['Subject'] = subject

            if cc:
                message['Cc'] = cc

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            # Send via Gmail API
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            return {
                'success': True,
                'message_id': result['id'],
                'thread_id': result['threadId'],
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            }

        except HttpError as error:
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
        label: str = 'INBOX'
    ) -> List[Dict]:
        """Read emails from inbox.

        Args:
            limit: Maximum number of emails to retrieve
            filter_unread: If True, only return unread emails
            label: Gmail label to read from (default: INBOX)

        Returns:
            List of email dictionaries with metadata and content
        """
        try:
            # Build query
            query = f'label:{label}'
            if filter_unread:
                query += ' is:unread'

            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            # Fetch full message details
            emails = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                email_data = self._parse_message(msg_data)
                emails.append(email_data)

            return emails

        except HttpError as error:
            raise Exception(f"Failed to read inbox: {error}")

    def search_emails(
        self,
        query: str,
        limit: int = 20,
        search_in: str = 'all'
    ) -> List[Dict]:
        """Search emails using Gmail query syntax.

        Args:
            query: Search query (Gmail search syntax)
            limit: Maximum results to return
            search_in: Where to search ('all', 'subject', 'body', 'from')

        Returns:
            List of matching email dictionaries
        """
        try:
            # Build Gmail query
            if search_in == 'subject':
                gmail_query = f'subject:{query}'
            elif search_in == 'from':
                gmail_query = f'from:{query}'
            elif search_in == 'body':
                gmail_query = query
            else:
                gmail_query = query

            # Search messages
            results = self.service.users().messages().list(
                userId='me',
                q=gmail_query,
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            # Fetch full details
            emails = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                email_data = self._parse_message(msg_data)
                emails.append(email_data)

            return emails

        except HttpError as error:
            raise Exception(f"Search failed: {error}")

    def _parse_message(self, message: Dict) -> Dict:
        """Parse Gmail API message into a standardized format.

        Args:
            message: Raw Gmail API message

        Returns:
            Parsed email dictionary
        """
        headers = {h['name']: h['value'] for h in message['payload']['headers']}

        # Extract body
        body = self._get_message_body(message['payload'])

        # Parse date
        timestamp = int(message['internalDate']) / 1000
        received_date = datetime.fromtimestamp(timestamp)

        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', '(No Subject)'),
            'body': body,
            'preview': body[:200] if body else '',
            'received': received_date.strftime('%Y-%m-%d %H:%M:%S'),
            'unread': 'UNREAD' in message.get('labelIds', []),
            'labels': message.get('labelIds', []),
            'snippet': message.get('snippet', '')
        }

    def _get_message_body(self, payload: Dict) -> str:
        """Extract message body from payload.

        Args:
            payload: Gmail message payload

        Returns:
            Decoded message body
        """
        body = ''

        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            # Simple message
            if 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body


def get_gmail_client() -> Optional[GmailClient]:
    """Get authenticated Gmail client.

    Returns:
        GmailClient instance or None if credentials not configured
    """
    try:
        return GmailClient()
    except (FileNotFoundError, ImportError) as e:
        print(f"Gmail not configured: {e}")
        return None


def is_gmail_configured() -> bool:
    """Check if Gmail is properly configured.

    Returns:
        True if credentials file exists and dependencies are installed
    """
    if not GMAIL_AVAILABLE:
        return False

    credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    return Path(credentials_file).exists()
