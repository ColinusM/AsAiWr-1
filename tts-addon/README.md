# 🎵 TTS Addon - Universal Text-to-Speech for Any Project

Ultra-fast, zero-friction text-to-speech with GUI controls for any codebase.

## 🚀 Quick Setup

1. **Copy to any project**: `cp -r tts-addon/ /path/to/your/project/`
2. **Set your OpenAI API key** in `fast_tts.py` (line 15)
3. **Make executable**: `chmod +x tts-addon/*`
4. **Ready to use**: `./tts-addon/read filename.md`

## 📁 Files Included

- **`read`** - Main command (ultra-fast, non-blocking)
- **`fast_tts.py`** - TTS engine with OpenAI API
- **`tts_gui.py`** - GUI control panel with pause/stop/resume
- **`stop-audio`** - Emergency stop all audio
- **`claude-code-hook.py`** - Auto-TTS hook for Claude Code
- **`setup.sh`** - One-command setup script

## 🎯 Usage

```bash
# Basic usage
./tts-addon/read README.md

# Stop all audio
./tts-addon/stop-audio

# Auto-read implementation summaries (with Claude Code hooks)
# Files containing: implementation-summary, summary, readme, requirements
```

## ⚙️ Configuration

### OpenAI API Key
Edit `fast_tts.py` line 15:
```python
OPENAI_API_KEY = "your-api-key-here"
```

### Auto-Read File Patterns
Edit `claude-code-hook.py` lines 20-27 to customize which files auto-trigger TTS.

## 🎵 Features

✅ **Zero friction** - One command, instant results  
✅ **Non-blocking** - Continue working while audio plays  
✅ **GUI controls** - Pause/stop/resume with visual feedback  
✅ **Background processing** - Everything runs detached  
✅ **Universal** - Works in any project directory  
✅ **Emergency stop** - Kill all audio instantly  
✅ **Content optimization** - Cleans markdown/code for speech  
✅ **Hook integration** - Auto-reads important files  

## 🔧 Technical Details

- Uses OpenAI TTS-1 model for speed
- macOS `afplay` for audio playback
- Tkinter GUI for cross-platform controls
- Completely detached background processing
- Temporary file cleanup
- Process management with pause/resume

## 📋 Requirements

- Python 3.6+
- OpenAI Python library (`pip install openai`)
- macOS (for `afplay` - easily adaptable for Linux/Windows)
- Tkinter (usually included with Python)

## 🚀 Perfect For

- Code review sessions
- Documentation reading
- Implementation summaries
- README files
- Any text content you want to hear while coding

**Maximum speed, zero friction, full control!**