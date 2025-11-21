# Personal AI Assistant - Setup Guide

Complete guide to setting up your Personal AI Assistant for email and WhatsApp management.

## Overview

The Personal AI Assistant is a comprehensive agentic system that helps you manage:
- **Multiple email accounts** (Gmail + Outlook/Microsoft 365)
- **WhatsApp messages** (via WhatsApp Web)
- **Smart draft generation** (AI-powered reply drafts for review)
- **Message analytics** (categorization, task extraction, daily summaries)

## Quick Start

### 1. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# LLM Provider (at least one required)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini

# Email API Mode
USE_REAL_EMAIL_API=true

# Multi-Account Email Configuration (JSON format)
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
    "client_secret": "your-client-secret",
    "email": "you@outlook.com"
  }
]'

# Default account
DEFAULT_EMAIL_ACCOUNT=work

# WhatsApp (optional)
USE_WHATSAPP_API=true
WHATSAPP_SESSION_PATH=./whatsapp_session

# Draft storage
DRAFT_STORAGE_PATH=./data/drafts.json
```

### 2. Gmail Setup (per account)

For each Gmail account:

1. **Google Cloud Console** (https://console.cloud.google.com/):
   - Create project or use existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download as `work_credentials.json`, `personal_credentials.json`, etc.

2. **Place credentials** in project root

3. **First run** will open browser for authentication
   - Generates `work_token.json`, `personal_token.json`, etc.
   - Subsequent runs use token (no browser needed)

### 3. Outlook/Microsoft 365 Setup (optional)

1. **Azure Portal** (https://portal.azure.com/):
   - Register application in Azure AD
   - Add API permissions:
     - Mail.Read
     - Mail.Send
     - Mail.ReadWrite
     - User.Read
   - Create client secret
   - Note tenant ID, client ID, and secret

2. **Add to EMAIL_ACCOUNTS** in .env (see example above)

### 4. WhatsApp Setup (optional)

1. **Install Node.js** (https://nodejs.org/)

2. **Install WhatsApp bridge dependencies**:
   ```bash
   cd tools/whatsapp/bridge
   npm install
   ```

3. **First run authentication**:
   ```bash
   # Terminal 1: Start bridge
   cd tools/whatsapp/bridge
   node server.js

   # Terminal 2: Use assistant
   python run_devui.py
   ```

4. **Scan QR code** with WhatsApp mobile app

5. **Session persists** - no need to scan QR again

## Usage

### Running the Assistant

```bash
# Start DevUI
python run_devui.py

# Access at http://localhost:8080
# Select "Personal AI Assistant" agent
```

### Common Commands

**Check all messages:**
```
Check my messages from all accounts
```

**Read specific account:**
```
Read my work email inbox
```

**Unified inbox:**
```
Show me unified inbox across all accounts
```

**WhatsApp:**
```
Check my WhatsApp messages
```

**Generate drafts:**
```
Generate draft replies for urgent emails
```

**Review drafts:**
```
Show me pending drafts
```

**Approve draft:**
```
Approve and send draft draft_20251122_153000_0
```

**Daily summary:**
```
Give me a summary of today's messages
```

**Extract tasks:**
```
Extract action items from my inbox
```

## Features

### 1. Multi-Account Email

**Unified View:**
- `unified_inbox()` - All accounts in one view
- `list_email_accounts()` - See configured accounts

**Account-Specific:**
- All email tools support `account_id` parameter
- Auto-uses default if not specified
- Example: `send_email(to="...", subject="...", account_id="work")`

### 2. Smart Draft System

**Auto-generate drafts** for review before sending:

1. **Message arrives** → Read with `read_inbox()`
2. **Analyze** → `should_generate_draft()` decides if draft needed
3. **Generate** → `generate_draft_reply()` creates draft
4. **Review** → `list_drafts()` shows pending drafts
5. **Approve** → `approve_draft(draft_id)` sends message

**Benefits:**
- Never send accidentally
- Review AI-generated replies
- Edit before sending
- Safety net for important messages

### 3. Message Analytics

**Categorization:**
```python
categorize_message(
    message_from="boss@company.com",
    message_subject="Q4 Report",
    message_body="Need the Q4 financial report by Friday"
)
```

**Returns:**
- Topic/category
- Urgency level
- Message type
- Suggested labels
- Recommended actions

**Task Extraction:**
```python
extract_tasks_from_message(
    message_subject="Project Updates",
    message_body="Please send report by Friday and schedule meeting for Tuesday at 2pm"
)
```

**Finds:**
- Action items
- Deadlines
- Meeting times
- Deliverables

### 4. Intelligent Workflows

The assistant can execute complex workflows:

**Morning Routine:**
1. Check unified inbox
2. Identify urgent messages
3. Generate drafts for high-priority items
4. Extract today's action items
5. Present summary with recommendations

**Throughout Day:**
1. Monitor for new messages
2. Auto-categorize by importance
3. Generate drafts for actionable items
4. Track tasks and deadlines

## Troubleshooting

### Gmail Authentication Issues

**Error:** "Credentials file not found"
- Ensure `credentials.json` is in project root
- Check filename matches .env config

**Error:** "Token expired"
- Delete `token.json`
- Re-authenticate (browser will open)

### Outlook Authentication Issues

**Error:** "Failed to acquire access token"
- Verify tenant_id, client_id, client_secret
- Check API permissions in Azure portal
- Ensure client secret hasn't expired

### WhatsApp Issues

**Error:** "WhatsApp bridge failed to start"
- Install Node.js: https://nodejs.org/
- Run `cd tools/whatsapp/bridge && npm install`
- Check port 3123 is available

**Error:** "WhatsApp not authenticated"
- Start bridge: `node tools/whatsapp/bridge/server.js`
- Scan QR code with phone
- Wait for "Client is ready" message

### Draft System Issues

**Drafts not saving:**
- Check `DRAFT_STORAGE_PATH` directory exists
- Ensure write permissions
- Default: `./data/drafts.json`

## Architecture

```
Personal AI Assistant
├── Email Management
│   ├── Gmail Integration (multiple accounts)
│   ├── Outlook Integration (Microsoft 365)
│   ├── Unified Inbox
│   └── Account Manager
├── WhatsApp Integration
│   ├── Node.js Bridge (whatsapp-web.js)
│   ├── Python Client
│   └── Message Management
├── Draft System
│   ├── Smart Filtering
│   ├── AI Generation
│   ├── Draft Storage
│   └── Approval Workflow
└── Analytics
    ├── Categorization
    ├── Summarization
    ├── Task Extraction
    └── Priority Detection
```

## Next Steps

1. **Configure accounts** in .env
2. **Authenticate** Gmail/Outlook/WhatsApp
3. **Test** with `python run_devui.py`
4. **Create workflows** (see workflows/ directory)
5. **Customize** agent instructions
6. **Automate** daily routines

## Support

For issues:
1. Check logs in DevUI
2. Verify .env configuration
3. Test individual tools
4. Review authentication status

## Security Notes

- **Credentials**: Keep credentials.json and secrets secure
- **Tokens**: Excluded from git (.gitignore)
- **Drafts**: Review before sending
- **Privacy**: All processing local (except LLM API calls)
- **Permissions**: Only grant necessary Gmail/Outlook permissions
