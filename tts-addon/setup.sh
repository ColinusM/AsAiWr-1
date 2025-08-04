#!/bin/bash
# TTS Addon Setup Script
# Run this in any project to set up TTS functionality

echo "🎵 Setting up TTS Addon..."

# Make all scripts executable
chmod +x read fast_tts.py tts_gui.py stop-audio claude-code-hook.py

echo "✅ Scripts made executable"

# Check for OpenAI library
if python3 -c "import openai" 2>/dev/null; then
    echo "✅ OpenAI library available"
else
    echo "⚠️  Installing OpenAI library..."
    pip3 install openai
fi

# Create audio output directory
mkdir -p audio-output
echo "✅ Audio output directory created"

echo ""
echo "🎯 Setup complete! Usage:"
echo "  ./read filename.md     # Read any file with TTS"
echo "  ./stop-audio          # Stop all audio"
echo ""
echo "⚙️  Don't forget to set your OpenAI API key in fast_tts.py (line 15)"
echo ""
echo "🚀 Ready to use!"