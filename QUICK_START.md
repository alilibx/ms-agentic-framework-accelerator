# Personal AI Assistant - Quick Start Guide

## 30-Second Setup (Mock Mode)

Test the assistant without any configuration:

```bash
# 1. Run DevUI
python run_devui.py

# 2. Open browser
# http://localhost:8080

# 3. Select agent
# "Personal AI Assistant"

# 4. Try commands
"Check my messages"
"Generate a draft reply to an urgent email"
"Show me my drafts"
```

All tools work in mock mode by default!

## 5-Minute Setup (Real Gmail)

Get real Gmail integration working:

```bash
# 1. Get Gmail credentials
# - Go to https://console.cloud.google.com/
# - Enable Gmail API
# - Create OAuth 2.0 Desktop credentials
# - Download as credentials.json

# 2. Configure .env
cp .env.example .env
# Add:
USE_REAL_EMAIL_API=true
EMAIL_ACCOUNTS='[{"id":"default","provider":"gmail","credentials":"credentials.json","token":"token.json","email":"you@gmail.com"}]'

# 3. Run
python run_devui.py
# Browser opens for authentication
# Scan QR code or login

# 4. Use assistant
"Check my real inbox"
```

## Common Commands

### Reading Messages
```
"Check my messages"
"Show me my work email inbox"
"Read my WhatsApp messages"
"Show unified inbox across all accounts"
"List my email accounts"
```

### Generating Drafts
```
"Should I reply to this email from boss@company.com about Q4 report?"
"Generate a draft reply for urgent emails"
"Show me pending drafts"
"Approve draft draft_20251122_153000_0"
```

### Analytics
```
"Categorize this message"
"Extract tasks from my inbox"
"Give me a daily summary"
```

### Sending (via drafts)
```
"Generate draft reply to boss@company.com saying I'll send the report by Friday"
"List drafts"
"Approve and send draft_12345"
```

## Architecture

```
YOU → DevUI (http://localhost:8080) → Personal Assistant Agent
                                       ├─ Email Tools (Gmail/Outlook)
                                       ├─ WhatsApp Tools
                                       ├─ Draft System
                                       └─ Analytics Tools
```

## Key Features

1. **Safety First**: Never sends without approval (draft mode)
2. **Multi-Account**: Gmail + Outlook support
3. **WhatsApp**: Full messaging integration
4. **Smart AI**: Categorization, task extraction, summaries
5. **Zero Code**: Pure YAML configuration

## Troubleshooting

**Q: "No email accounts configured"**
A: Set USE_REAL_EMAIL_API=true and configure EMAIL_ACCOUNTS in .env

**Q: "WhatsApp not authenticated"**
A: Run `node tools/whatsapp/bridge/server.js` and scan QR code

**Q: "Import errors"**
A: Install dependencies: `pip install -r requirements.txt`

**Q: "Want to test without real accounts?"**
A: Leave USE_REAL_EMAIL_API=false - everything works in mock mode!

## Next Steps

1. ✅ Try mock mode (works immediately)
2. ⚡ Add Gmail (5 minutes)
3. 🚀 Add Outlook (10 minutes)
4. 💬 Add WhatsApp (15 minutes)
5. 🤖 Customize agent behavior (agents/*.yaml)
6. 📊 Create workflows (workflows/*.py)

## Files to Know

- `.env` - Your configuration
- `agents/personal_assistant_agent.yaml` - Agent behavior
- `PERSONAL_ASSISTANT_SETUP.md` - Detailed setup
- `data/drafts.json` - Your draft storage

## Pro Tips

1. **Start with mock mode** to learn the system
2. **Add one account at a time** to troubleshoot easier
3. **Review drafts before approving** - safety first!
4. **Use account_id parameter** for specific accounts
5. **Check tools/*/README** for tool-specific docs

## Support

- 📖 Full setup: `PERSONAL_ASSISTANT_SETUP.md`
- 🏗️ Architecture: `IMPLEMENTATION_SUMMARY.md`
- 💡 Examples: See `agents/*.yaml` instructions
- 🐛 Issues: Check DevUI logs

---

**Ready?** Run `python run_devui.py` and start chatting with your Personal AI Assistant!
