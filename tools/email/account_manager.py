"""Multi-account email manager for Gmail and Outlook.

This module provides a unified interface for managing multiple email accounts
across different providers (Gmail, Outlook/Microsoft 365).

Setup:
1. Configure accounts in .env using EMAIL_ACCOUNTS JSON array
2. Each account should have: id, provider, credentials, token (if needed)
3. Use account_id parameter in email tools to specify which account

Example .env configuration:
EMAIL_ACCOUNTS='[
  {
    "id": "work",
    "provider": "gmail",
    "credentials": "work_credentials.json",
    "token": "work_token.json",
    "email": "work@company.com"
  },
  {
    "id": "personal",
    "provider": "gmail",
    "credentials": "personal_credentials.json",
    "token": "personal_token.json",
    "email": "personal@gmail.com"
  },
  {
    "id": "outlook",
    "provider": "outlook",
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "email": "you@outlook.com"
  }
]'
"""

import os
import json
from typing import Optional, List, Dict, Union
from pathlib import Path

from tools.email.gmail_utils import GmailClient, is_gmail_configured


class EmailAccount:
    """Represents a single email account configuration."""

    def __init__(
        self,
        account_id: str,
        provider: str,
        email: str,
        credentials: Optional[str] = None,
        token: Optional[str] = None,
        **kwargs
    ):
        """Initialize email account.

        Args:
            account_id: Unique identifier for this account
            provider: Email provider ('gmail', 'outlook')
            email: Email address
            credentials: Path to credentials file (provider-specific)
            token: Path to token file (provider-specific)
            **kwargs: Additional provider-specific configuration
        """
        self.account_id = account_id
        self.provider = provider.lower()
        self.email = email
        self.credentials = credentials
        self.token = token
        self.config = kwargs
        self._client = None

    def get_client(self):
        """Get or create email client for this account.

        Returns:
            Provider-specific email client (GmailClient or OutlookClient)
        """
        if self._client is None:
            if self.provider == 'gmail':
                self._client = self._create_gmail_client()
            elif self.provider == 'outlook':
                self._client = self._create_outlook_client()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        return self._client

    def _create_gmail_client(self):
        """Create Gmail client for this account."""
        try:
            return GmailClient(
                credentials_file=self.credentials,
                token_file=self.token
            )
        except Exception as e:
            raise Exception(f"Failed to create Gmail client for {self.account_id}: {e}")

    def _create_outlook_client(self):
        """Create Outlook client for this account."""
        try:
            # Import here to avoid dependency if not using Outlook
            from tools.email.outlook_utils import OutlookClient

            return OutlookClient(
                tenant_id=self.config.get('tenant_id'),
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                token_file=self.token
            )
        except ImportError:
            raise ImportError(
                "Outlook support not available. "
                "Install dependencies: pip install msal msgraph-core"
            )
        except Exception as e:
            raise Exception(f"Failed to create Outlook client for {self.account_id}: {e}")

    def to_dict(self) -> Dict:
        """Convert account to dictionary representation."""
        return {
            'account_id': self.account_id,
            'provider': self.provider,
            'email': self.email,
            'credentials': self.credentials,
            'token': self.token,
            **self.config
        }


class EmailAccountManager:
    """Manages multiple email accounts across providers.

    This is a singleton class that provides centralized account management.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize account manager."""
        if self._initialized:
            return

        self.accounts: Dict[str, EmailAccount] = {}
        self.default_account_id: Optional[str] = None
        self._load_accounts()
        self._initialized = True

    def _load_accounts(self):
        """Load all configured accounts from environment."""
        # Try to load from EMAIL_ACCOUNTS JSON
        accounts_json = os.getenv('EMAIL_ACCOUNTS', '[]')

        try:
            accounts_config = json.loads(accounts_json)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse EMAIL_ACCOUNTS: {e}")
            accounts_config = []

        # Load each account
        for config in accounts_config:
            account_id = config.get('id')
            if not account_id:
                print(f"Warning: Account missing 'id' field, skipping: {config}")
                continue

            try:
                account = EmailAccount(**config)
                self.accounts[account_id] = account

                # Set first account as default if not set
                if self.default_account_id is None:
                    self.default_account_id = account_id

            except Exception as e:
                print(f"Warning: Failed to load account {account_id}: {e}")

        # Fallback: If no accounts configured, try to create a default Gmail account
        if not self.accounts:
            self._try_create_default_gmail_account()

        # Set default account from env if specified
        default_from_env = os.getenv('DEFAULT_EMAIL_ACCOUNT')
        if default_from_env and default_from_env in self.accounts:
            self.default_account_id = default_from_env

    def _try_create_default_gmail_account(self):
        """Try to create a default Gmail account from legacy env vars."""
        if is_gmail_configured():
            try:
                default_account = EmailAccount(
                    account_id='default',
                    provider='gmail',
                    email=os.getenv('GMAIL_USER_EMAIL', 'me'),
                    credentials=os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json'),
                    token=os.getenv('GMAIL_TOKEN_FILE', 'token.json')
                )
                self.accounts['default'] = default_account
                self.default_account_id = 'default'
                print("Created default Gmail account from legacy environment variables")
            except Exception as e:
                print(f"Warning: Failed to create default Gmail account: {e}")

    def get_account(self, account_id: Optional[str] = None) -> EmailAccount:
        """Get account by ID, or default account if not specified.

        Args:
            account_id: Account identifier, or None for default

        Returns:
            EmailAccount instance

        Raises:
            ValueError: If account not found or no accounts configured
        """
        if account_id is None:
            account_id = self.default_account_id

        if not account_id:
            raise ValueError(
                "No email accounts configured. "
                "Please configure EMAIL_ACCOUNTS in .env or set up Gmail credentials."
            )

        if account_id not in self.accounts:
            available = ', '.join(self.accounts.keys())
            raise ValueError(
                f"Account '{account_id}' not found. "
                f"Available accounts: {available or 'none'}"
            )

        return self.accounts[account_id]

    def get_client(self, account_id: Optional[str] = None):
        """Get email client for specified account.

        Args:
            account_id: Account identifier, or None for default

        Returns:
            Provider-specific email client
        """
        account = self.get_account(account_id)
        return account.get_client()

    def list_accounts(self) -> List[Dict]:
        """List all configured accounts.

        Returns:
            List of account dictionaries with metadata
        """
        return [
            {
                'account_id': acc.account_id,
                'provider': acc.provider,
                'email': acc.email,
                'is_default': acc.account_id == self.default_account_id
            }
            for acc in self.accounts.values()
        ]

    def add_account(self, **kwargs):
        """Dynamically add a new account at runtime.

        Args:
            **kwargs: Account configuration (id, provider, email, etc.)
        """
        account_id = kwargs.get('id')
        if not account_id:
            raise ValueError("Account must have 'id' field")

        if account_id in self.accounts:
            raise ValueError(f"Account '{account_id}' already exists")

        account = EmailAccount(**kwargs)
        self.accounts[account_id] = account

        # Set as default if it's the first account
        if self.default_account_id is None:
            self.default_account_id = account_id

    def remove_account(self, account_id: str):
        """Remove an account from the manager.

        Args:
            account_id: Account identifier to remove
        """
        if account_id not in self.accounts:
            raise ValueError(f"Account '{account_id}' not found")

        del self.accounts[account_id]

        # Update default if we removed it
        if self.default_account_id == account_id:
            self.default_account_id = next(iter(self.accounts.keys()), None)

    def set_default_account(self, account_id: str):
        """Set the default account.

        Args:
            account_id: Account identifier to set as default
        """
        if account_id not in self.accounts:
            raise ValueError(f"Account '{account_id}' not found")

        self.default_account_id = account_id

    def reload(self):
        """Reload accounts from environment (useful for testing/config changes)."""
        self.accounts.clear()
        self.default_account_id = None
        self._load_accounts()


# Singleton instance
_manager = None


def get_account_manager() -> EmailAccountManager:
    """Get the singleton EmailAccountManager instance.

    Returns:
        EmailAccountManager singleton
    """
    global _manager
    if _manager is None:
        _manager = EmailAccountManager()
    return _manager


def get_email_client(account_id: Optional[str] = None):
    """Convenience function to get email client directly.

    Args:
        account_id: Account identifier, or None for default

    Returns:
        Provider-specific email client
    """
    manager = get_account_manager()
    return manager.get_client(account_id)
