# Quick Start Guide

Get up and running in 5 minutes!

## 🚀 First Time Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your OpenRouter API key (get from https://openrouter.ai/keys)
# Edit .env and add:
#   OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 3. Start the system (automatically creates venv and installs dependencies)
bun run agent
```

That's it! The script will:
- ✅ Find Python on your system
- ✅ Create virtual environment (`.venv`)
- ✅ Install all dependencies
- ✅ Start the agent system

Visit: **http://localhost:8080**

---

## 📝 Available Commands

### Start/Stop

```bash
# Start the agent system
bun run agent
# or
bun run start

# Stop the agent
bun run stop

# Restart the agent
bun run restart

# Check if agent is running
bun run status
```

### Setup & Installation

```bash
# Manual setup (if needed)
bun run setup

# Install/update dependencies
bun run install

# Clean everything and start fresh
bun run clean
```

### Other Commands

```bash
# Run workflows
bun run workflow

# Run demos
bun run demo

# View logs
bun run logs
```

---

## 🎯 What Happens on First Run?

When you run `bun run agent` for the first time:

1. **Finds Python** - Looks for `python3` or `python`
2. **Creates `.venv/`** - Virtual environment in project directory
3. **Installs dependencies** - From `requirements.txt`
4. **Starts DevUI** - Web interface on port 8080

**Output you'll see:**
```
🔍 Looking for Python installation...
✅ Found: Python 3.11.6
📦 Creating virtual environment...
✅ Virtual environment created at .venv
🔌 Activating virtual environment...
✅ Virtual environment activated
📚 Checking dependencies...
📥 Installing dependencies from requirements.txt...
✅ Dependencies installed
🚀 Starting multi-agent system...
✅ Agent started with PID: 12345
🌐 DevUI available at: http://localhost:8080
```

---

## 🔧 Configuration

### LLM Provider Options

**Option 1: OpenRouter** (Easiest - Recommended)
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4-turbo
```

**Option 2: Azure OpenAI**
```bash
az login  # First authenticate
```
```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

**Option 3: Direct OpenAI**
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Gmail Integration (Optional)

```env
# Enable real Gmail
USE_REAL_EMAIL_API=true

# Gmail credentials
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_USER_EMAIL=your.email@gmail.com
```

See [Setup Guide](docs/SETUP_GUIDE.md#gmail-api-setup) for detailed Gmail setup.

---

## 🌟 Available Agents

After starting, you'll have access to:

1. **General Assistant (OpenRouter)** - All tools, powered by OpenRouter
2. **Weather Agent** - Weather information and forecasts
3. **Stock Agent** - Stock market data and analysis
4. **Email Assistant** - Gmail integration (mock or real)
5. **Calendar Agent** - Calendar management

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'agent_framework'"

This means the Microsoft Agent Framework wasn't installed. Fix it:

```bash
# Clean and reinstall
bun run clean
bun run agent
```

Or manually:
```bash
source .venv/bin/activate
pip install --pre agent-framework
pip install --pre -r requirements.txt
```

**Note:** The framework is in preview, so the `--pre` flag is required.

### "python: command not found"

The new script automatically handles this! It looks for `python3` first.

If you still see this error:

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-venv
```

### "Port 8080 already in use"

```bash
# Stop existing process
bun run stop

# Or manually find and kill
lsof -i :8080
kill <PID>
```

### Virtual environment issues

```bash
# Clean and start fresh
bun run clean
bun run agent
```

### Dependencies not installing

```bash
# Manual installation
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💡 Tips

### Keep Terminal Open

The agent runs in the background, but keeping the terminal open shows logs.

### Use Multiple Terminals

Terminal 1: Run the agent
```bash
bun run agent
```

Terminal 2: Check status, restart, etc.
```bash
bun run status
bun run restart
```

### Activate venv Manually (for development)

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Then run Python commands directly
python run_devui.py
```

---

## 📚 Next Steps

1. **Test the system**: Visit http://localhost:8080
2. **Try different agents**: Use the dropdown to switch
3. **Configure Gmail**: See [Setup Guide](docs/SETUP_GUIDE.md)
4. **Create custom agents**: Add YAML files to `agents/`
5. **Read documentation**: Check `docs/` directory

---

## 🆘 Need Help?

- **Full Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **Architecture**: [docs/AGENT_WORKFLOW_ARCHITECTURE.md](docs/AGENT_WORKFLOW_ARCHITECTURE.md)
- **Email Setup**: [docs/SETUP_GUIDE.md#gmail-api-setup](docs/SETUP_GUIDE.md#gmail-api-setup)
- **OpenRouter Models**: https://openrouter.ai/models

---

**Happy Building! 🎉**
