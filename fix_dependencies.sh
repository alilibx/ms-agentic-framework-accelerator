#!/bin/bash

# =============================================================================
# Fix Dependencies - Install Microsoft Agent Framework
# =============================================================================

echo "🔧 Fixing dependencies..."
echo ""

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run 'bun run agent' first."
    exit 1
fi

# Install agent framework with --pre flag
echo "📥 Installing Microsoft Agent Framework (preview)..."
pip install --pre agent-framework

# Install remaining dependencies
echo "📥 Installing remaining dependencies..."
pip install --pre -r requirements.txt

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "🚀 Now run: bun run agent"
