"""Draft storage and management.

Simple JSON-based storage for draft messages.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class DraftStore:
    """Manages draft messages in JSON storage."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize draft store.

        Args:
            storage_path: Path to JSON storage file
        """
        self.storage_path = storage_path or os.getenv(
            'DRAFT_STORAGE_PATH',
            './data/drafts.json'
        )

        # Ensure directory exists
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize storage if needed
        if not Path(self.storage_path).exists():
            self._save_drafts([])

    def _load_drafts(self) -> List[Dict]:
        """Load drafts from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_drafts(self, drafts: List[Dict]):
        """Save drafts to storage."""
        with open(self.storage_path, 'w') as f:
            json.dump(drafts, f, indent=2)

    def add_draft(
        self,
        message_type: str,  # 'email' or 'whatsapp'
        to: str,
        subject: str,
        body: str,
        account_id: Optional[str] = None,
        original_message: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Add a new draft.

        Args:
            message_type: Type of message ('email' or 'whatsapp')
            to: Recipient
            subject: Subject line (for email) or summary (for WhatsApp)
            body: Message body
            account_id: Account to send from (for email)
            original_message: Original message being replied to
            metadata: Additional metadata

        Returns:
            Draft ID
        """
        drafts = self._load_drafts()

        draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(drafts)}"

        draft = {
            'id': draft_id,
            'message_type': message_type,
            'to': to,
            'subject': subject,
            'body': body,
            'account_id': account_id,
            'original_message': original_message,
            'metadata': metadata or {},
            'status': 'pending',  # 'pending', 'approved', 'rejected', 'sent'
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        drafts.append(draft)
        self._save_drafts(drafts)

        return draft_id

    def get_draft(self, draft_id: str) -> Optional[Dict]:
        """Get a specific draft by ID."""
        drafts = self._load_drafts()

        for draft in drafts:
            if draft['id'] == draft_id:
                return draft

        return None

    def list_drafts(
        self,
        status: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """List drafts with optional filtering.

        Args:
            status: Filter by status ('pending', 'approved', 'rejected', 'sent')
            message_type: Filter by type ('email' or 'whatsapp')
            limit: Maximum number of drafts to return

        Returns:
            List of draft dictionaries
        """
        drafts = self._load_drafts()

        # Filter by status
        if status:
            drafts = [d for d in drafts if d.get('status') == status]

        # Filter by message type
        if message_type:
            drafts = [d for d in drafts if d.get('message_type') == message_type]

        # Sort by created_at descending (newest first)
        drafts.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Apply limit
        if limit:
            drafts = drafts[:limit]

        return drafts

    def update_draft(
        self,
        draft_id: str,
        status: Optional[str] = None,
        body: Optional[str] = None,
        subject: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Update a draft.

        Args:
            draft_id: Draft ID
            status: New status
            body: New body
            subject: New subject
            **kwargs: Other fields to update

        Returns:
            True if updated successfully
        """
        drafts = self._load_drafts()

        for draft in drafts:
            if draft['id'] == draft_id:
                if status:
                    draft['status'] = status
                if body:
                    draft['body'] = body
                if subject:
                    draft['subject'] = subject

                # Update other fields
                for key, value in kwargs.items():
                    draft[key] = value

                draft['updated_at'] = datetime.now().isoformat()

                self._save_drafts(drafts)
                return True

        return False

    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft.

        Args:
            draft_id: Draft ID

        Returns:
            True if deleted successfully
        """
        drafts = self._load_drafts()
        original_count = len(drafts)

        drafts = [d for d in drafts if d['id'] != draft_id]

        if len(drafts) < original_count:
            self._save_drafts(drafts)
            return True

        return False

    def clear_old_drafts(self, days: int = 30):
        """Clear drafts older than specified days.

        Args:
            days: Number of days to keep drafts
        """
        from datetime import timedelta

        drafts = self._load_drafts()
        cutoff = datetime.now() - timedelta(days=days)

        # Keep drafts that are recent OR still pending
        filtered_drafts = []
        for draft in drafts:
            created_at = datetime.fromisoformat(draft.get('created_at', ''))
            if created_at > cutoff or draft.get('status') == 'pending':
                filtered_drafts.append(draft)

        self._save_drafts(filtered_drafts)


# Singleton instance
_store = None


def get_draft_store() -> DraftStore:
    """Get the singleton DraftStore instance."""
    global _store
    if _store is None:
        _store = DraftStore()
    return _store
