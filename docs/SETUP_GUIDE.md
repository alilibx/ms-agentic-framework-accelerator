# Setup Guide - Multi-Agent System

Complete setup guide for configuring the multi-agent system with OpenRouter and Gmail integration.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Configuration](#environment-configuration)
3. [OpenRouter Setup](#openrouter-setup)
4. [Gmail API Setup](#gmail-api-setup)
5. [Running the System](#running-the-system)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd ms-agentic-framework-accelerator

# Install Python dependencies
pip install -r requirements.txt

# Or using bun (recommended)
bun install
```

### 2. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### 3. Run the System

```bash
# Start the DevUI (using bun)
bun run agent

# Or using the shell script directly
./start_agent.sh

# Or using Python directly
python run_devui.py
```

Access the web interface at: **http://localhost:8080**

---

## Environment Configuration

### Basic Configuration

The `.env` file contains all configuration for the system. Here's what you need to configure:

#### 1. LLM Provider (Choose One)

**Option A: Azure OpenAI (Default)**
```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
# Leave empty to use Azure CLI authentication
AZURE_OPENAI_API_KEY=
```

**Option B: OpenRouter** (Recommended for testing)
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4-turbo
OPENROUTER_APP_NAME=ms-agentic-framework
```

**Option C: Direct OpenAI**
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview
```

#### 2. Email Configuration

```env
# Set to 'true' to use real Gmail, 'false' for mock mode
USE_REAL_EMAIL_API=false

# Gmail credentials (only needed if USE_REAL_EMAIL_API=true)
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_USER_EMAIL=your.email@gmail.com
```

#### 3. Tool API Keys (Optional)

```env
# Weather data
OPENWEATHER_API_KEY=your_key_here

# Stock market data
ALPHA_VANTAGE_API_KEY=your_key_here
```

---

## OpenRouter Setup

OpenRouter provides access to multiple LLM providers through a single API. This is the easiest way to test different models.

### Step 1: Get API Key

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up or log in
3. Navigate to [API Keys](https://openrouter.ai/keys)
4. Click "Create Key"
5. Copy your API key (starts with `sk-or-v1-`)

### Step 2: Configure Environment

Add to your `.env` file:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4-turbo
```

### Step 3: Create or Use OpenRouter Agent

**Option A: Use the pre-configured agent**

The system includes `general_openrouter_agent.yaml` which uses OpenRouter by default.

```yaml
# agents/general_openrouter_agent.yaml
model:
  provider: "openrouter"
  # API credentials loaded from environment
```

**Option B: Create a custom agent**

Create a new file `agents/my_custom_agent.yaml`:

```yaml
name: "My Custom Agent"
description: "Custom agent using OpenRouter"

tool_domains:
  - email
  - weather

instructions: |
  You are a helpful assistant...

model:
  provider: "openrouter"
  model: "anthropic/claude-3-opus"  # Optional: override default model
```

### Available OpenRouter Models

Popular models you can use (update `OPENROUTER_MODEL` in `.env`):

| Model | Best For | Cost |
|-------|----------|------|
| `openai/gpt-4-turbo` | General purpose, balanced | $$ |
| `anthropic/claude-3-opus` | Complex reasoning, long context | $$$ |
| `anthropic/claude-3-sonnet` | Balanced performance/cost | $$ |
| `google/gemini-pro-1.5` | Long context, multimodal | $ |
| `meta-llama/llama-3-70b` | Open source, cost-effective | $ |
| `mistralai/mistral-large` | European option, fast | $$ |

Full list: https://openrouter.ai/models

### Step 4: Test the Configuration

```bash
# Start the system
bun run agent

# Visit http://localhost:8080
# Select "General Assistant (OpenRouter)" from the dropdown
# Try sending a message
```

---

## Gmail API Setup

Enable real Gmail integration for the email agent.

### Prerequisites

- Google account
- Google Cloud Console access
- Python Gmail API libraries

### Step 1: Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

### Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Step 3: Enable Gmail API

1. In the Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (for personal Gmail)
   - App name: `Multi-Agent System`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add Gmail scopes (will be configured later)
4. Return to **Create OAuth client ID**:
   - Application type: **Desktop app**
   - Name: `Gmail Agent`
5. Click **Create**
6. **Download JSON** - Save as `credentials.json`

### Step 5: Place Credentials File

```bash
# Move credentials.json to project root
mv ~/Downloads/credentials.json /path/to/ms-agentic-framework-accelerator/

# Verify it's in the right place
ls -la credentials.json
```

### Step 6: Configure Environment

Update `.env`:

```env
# Enable real Gmail API
USE_REAL_EMAIL_API=true

# Gmail configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_USER_EMAIL=your.actual.email@gmail.com
```

### Step 7: First-Time Authorization

On the first run, the system will open a browser window for authorization:

```bash
# Start the agent
bun run agent

# Visit http://localhost:8080
# Select "Email Assistant" agent
# Try: "Read my inbox"

# A browser window will open
# 1. Sign in to your Google account
# 2. Click "Advanced" if you see a warning
# 3. Click "Go to Multi-Agent System (unsafe)"
# 4. Grant permissions:
#    - Read email
#    - Send email
# 5. Click "Allow"

# The system will save a token.json file for future use
```

### Step 8: Test Email Features

Try these commands in the DevUI:

```
Read my inbox
Show me unread emails
Search for emails about "project"
Send an email to test@example.com with subject "Test" and body "Hello!"
```

### Gmail API Scopes

The system uses these OAuth scopes:

- `gmail.readonly` - Read emails
- `gmail.send` - Send emails
- `gmail.compose` - Create drafts
- `gmail.modify` - Mark as read/unread

### Security Notes

- `credentials.json` contains your OAuth client ID (not a secret, but keep private)
- `token.json` contains access tokens (NEVER commit to git)
- Both files are in `.gitignore`
- Tokens expire after 7 days of inactivity
- Refresh happens automatically

---

## Running the System

### Start the DevUI

**Using bun (recommended):**
```bash
bun run agent
```

**Using shell script:**
```bash
./start_agent.sh
```

**Using Python directly:**
```bash
python run_devui.py
```

### Access the Interface

Open your browser to: **http://localhost:8080**

### Available Agents

After setup, you'll have access to:

1. **Weather Agent** - Weather information and forecasts
2. **Stock Agent** - Stock market data and analysis
3. **Email Assistant** - Gmail integration (mock or real)
4. **Calendar Agent** - Calendar management
5. **General Assistant (OpenRouter)** - All tools, OpenRouter-powered

### Stop the System

```bash
# Using bun
bun run stop

# Or find and kill the process
lsof -i :8080
kill <PID>
```

---

## Troubleshooting

### OpenRouter Issues

**Error: "OPENROUTER_API_KEY not found"**
- Check `.env` file exists and contains `OPENROUTER_API_KEY=...`
- Restart the system after updating `.env`

**Error: "OpenAI package required"**
```bash
pip install openai
```

**Error: "Model not found"**
- Check model name at https://openrouter.ai/models
- Use exact model ID (e.g., `openai/gpt-4-turbo`, not just `gpt-4-turbo`)

### Gmail Issues

**Error: "credentials.json not found"**
- Ensure file is in project root
- Check filename matches `GMAIL_CREDENTIALS_FILE` in `.env`

**Error: "Gmail API dependencies not installed"**
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**Error: "Invalid grant" during authorization**
- Delete `token.json`
- Run again to re-authorize
- Check system time is correct

**Browser doesn't open for authorization**
- Copy the URL from terminal and open manually
- Check firewall settings

**"This app isn't verified" warning**
- Click "Advanced"
- Click "Go to [app name] (unsafe)"
- This is normal for development apps

### General Issues

**Port 8080 already in use**
```bash
# Find and kill the process
lsof -i :8080
kill <PID>

# Or change port in .env
DEVUI_PORT=8081
```

**Tools not discovered**
```bash
# Check tool registry
python -c "from tools import ToolRegistry; r = ToolRegistry(); print(r.list_all_tools())"
```

**Agent not loading**
- Check YAML syntax in `agents/*.yaml`
- View logs in terminal
- Ensure all required fields are present

---

## Next Steps

### Testing the System

1. **Test Mock Mode** (no API keys needed)
   - Start system
   - Try each agent
   - All tools return mock data

2. **Test OpenRouter** (requires API key)
   - Configure OpenRouter
   - Use General Assistant agent
   - Test different models

3. **Test Gmail** (requires OAuth setup)
   - Complete Gmail setup
   - Set `USE_REAL_EMAIL_API=true`
   - Test email operations

### Advanced Configuration

- **Create custom agents**: Add YAML files to `agents/`
- **Create custom tools**: Add Python files to `tools/domain/`
- **Build workflows**: See `workflows/` directory
- **Parallel execution**: See `docs/PARALLEL_EXECUTION_QUICKSTART.md`

### Documentation

- [Agent & Workflow Architecture](./AGENT_WORKFLOW_ARCHITECTURE.md)
- [Dynamic Tool System](./DYNAMIC_TOOL_SYSTEM_COMPLETE.md)
- [Email Agent Demo](./EMAIL_AGENT_DEMO.md)
- [Parallel Execution Guide](./PARALLEL_EXECUTION_QUICKSTART.md)

---

## Support

For issues and feature requests:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Documentation: See `docs/` directory
- Examples: See `workflows/` directory

---

**Happy Building! 🚀**
