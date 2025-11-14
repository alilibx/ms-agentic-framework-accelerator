#!/bin/bash

# =============================================================================
# Multi-Agent System Startup Script
# Automatically creates and activates virtual environment
# =============================================================================

set -e  # Exit on error

VENV_DIR=".venv"
PYTHON_CMD=""

# Function to find Python
find_python() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        echo ""
    fi
}

# Function to check if we're in a virtual environment
in_venv() {
    [ -n "$VIRTUAL_ENV" ]
}

# =============================================================================
# Step 1: Find Python
# =============================================================================
echo "🔍 Looking for Python installation..."

PYTHON_CMD=$(find_python)

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: Python not found!"
    echo "📥 Please install Python 3.11+ from:"
    echo "   - macOS: brew install python3"
    echo "   - https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "✅ Found: $PYTHON_VERSION"

# =============================================================================
# Step 2: Create virtual environment if it doesn't exist
# =============================================================================
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
    echo "✅ Virtual environment created at $VENV_DIR"
else
    echo "✅ Virtual environment already exists"
fi

# =============================================================================
# Step 3: Activate virtual environment
# =============================================================================
echo "🔌 Activating virtual environment..."

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo "❌ Error: Could not find activation script"
    exit 1
fi

echo "✅ Virtual environment activated"

# =============================================================================
# Step 4: Check and install dependencies
# =============================================================================
if [ -f "requirements.txt" ]; then
    echo "📚 Checking dependencies..."

    # Check if critical packages are installed
    if ! python -c "import agent_framework" &> /dev/null; then
        echo "📥 Installing dependencies from requirements.txt..."
        echo "   (This may take a few minutes on first run...)"
        pip install -q --upgrade pip
        # Use --pre flag for preview packages (agent-framework)
        pip install -q --pre -r requirements.txt
        echo "✅ Dependencies installed"
    else
        echo "✅ Dependencies already installed"
    fi
else
    echo "⚠️  Warning: requirements.txt not found"
fi

# =============================================================================
# Step 5: Kill existing processes
# =============================================================================
echo "🔄 Stopping existing agent processes..."
pkill -f 'python run_devui.py' 2>/dev/null || true
pkill -f 'uvicorn' 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Check if port 8080 is still in use
if lsof -i :8080 >/dev/null 2>&1; then
    echo "⚠️  Port 8080 is still in use, force killing..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# =============================================================================
# Step 6: Start the agent
# =============================================================================
echo "🚀 Starting multi-agent system..."
python run_devui.py &

# Get the process ID
AGENT_PID=$!

# Save PID to file for easy stopping
echo $AGENT_PID > .agent.pid

echo ""
echo "✅ Agent started with PID: $AGENT_PID"
echo "🌐 DevUI available at: http://localhost:8080"
echo "📝 To stop: bun run stop"
echo "🔄 To restart: bun run restart"
echo ""
echo "💡 Tip: Keep this terminal open or use 'bun run stop' to stop the agent"
