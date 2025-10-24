#!/bin/bash

# Kill existing processes
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

# Start the agent in background
echo "🚀 Starting weather agent..."
python run_devui.py &

# Get the process ID
AGENT_PID=$!

# Save PID to file for easy stopping
echo $AGENT_PID > .agent.pid

echo "✅ Agent started with PID: $AGENT_PID"
echo "🌐 DevUI available at: http://localhost:8080"
echo "📝 To stop: bun run stop"
echo "🔄 To restart: bun run restart"
