#!/usr/bin/env python3
"""
Claude Code Hook for Auto-TTS
Triggers when a conversation ends to automatically read implementation summaries
"""

import os
import sys
import subprocess
from pathlib import Path

def should_auto_read(file_path):
    """Check if file should be auto-read"""
    if not file_path or not os.path.exists(file_path):
        return False
    
    filename = Path(file_path).name.lower()
    
    # Auto-read these file patterns
    auto_read_patterns = [
        'implementation-summary',
        'summary',
        'readme',
        'implementation',
        'todo',
        'plan',
        'requirements'
    ]
    
    return any(pattern in filename for pattern in auto_read_patterns)

def auto_tts(file_path):
    """Run TTS in background for the file"""
    try:
        script_dir = Path(__file__).parent
        fast_tts_path = script_dir / "fast_tts.py"
        
        if not fast_tts_path.exists():
            print(f"❌ TTS script not found: {fast_tts_path}")
            return
        
        print(f"🎵 Auto-reading: {Path(file_path).name}")
        
        # Run TTS in background (completely detached)
        subprocess.Popen([
            'python3', str(fast_tts_path), file_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    except Exception as e:
        print(f"❌ Auto-TTS failed: {e}")

def main():
    """Hook entry point"""
    if len(sys.argv) < 2:
        return
    
    # Get the file path from Claude Code hook
    file_path = sys.argv[1]
    
    if should_auto_read(file_path):
        auto_tts(file_path)

if __name__ == "__main__":
    main()