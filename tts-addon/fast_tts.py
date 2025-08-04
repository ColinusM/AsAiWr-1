#!/Users/colinmignot/miniforge3/bin/python3
"""
FAST TTS - Zero friction file-to-speech
Instantly reads file and plays audio without external apps
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
import openai

# Your OpenAI API Key - set via environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def fast_read(file_path):
    """Ultra-fast file to speech with immediate playback"""
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print(f"❌ File {file_path} is empty")
            return
        
        print(f"🎯 Reading: {Path(file_path).name} ({len(content)} chars)")
        
        # Progress indicator setup
        file_size = len(content)
        progress_steps = [
            (10, "📝 Processing content..."),
            (30, "🔧 Cleaning for speech..."),
            (50, "🚀 Generating audio..."),
            (80, "💾 Creating audio file..."),
            (100, "🎵 Launching controls...")
        ]
        
        def show_progress(step_pct, message):
            bar_length = 20
            filled = int(bar_length * step_pct / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r{message} [{bar}] {step_pct}%", end="", flush=True)
        
        # Step 1: Processing (10%)
        show_progress(10, "📝 Processing content...")
        
        # Quick content cleanup for speech
        content = content.replace("```", " code block ")
        content = content.replace("#", "")
        content = content.replace("*", "")
        content = content.replace("-", " ")
        
        # Step 2: Cleaning (30%)
        show_progress(30, "🔧 Cleaning for speech...")
        
        # Handle long files by chunking (OpenAI limit is 4096 chars)
        max_chunk_size = 4000  # Leave some buffer
        if len(content) > max_chunk_size:
            print(f"\n📄 File is {len(content)} chars, using first {max_chunk_size} chars...")
            content = content[:max_chunk_size] + "... Content truncated for TTS playback."
        
        # Step 3: Generating (50%)
        show_progress(50, "🚀 Generating audio...")
        
        # Initialize OpenAI client
        client = openai.Client(api_key=OPENAI_API_KEY)
        
        # Generate speech with fastest model
        response = client.audio.speech.create(
            model="tts-1",  # Fastest model
            voice="nova",   # Clear, fast voice
            input=content,
            speed=1.1       # Slightly faster speech
        )
        
        # Step 4: Creating file (80%)
        show_progress(80, "💾 Creating audio file...")
        
        # Create temporary file for immediate playback
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name
        
        # Step 5: Launching (100%)
        show_progress(100, "🎵 Launching controls...")
        print()  # New line after progress bar
        
        # Try GUI first, fallback to simple audio playback
        script_dir = Path(__file__).parent
        gui_script = script_dir / "tts_gui.py"
        
        try:
            if gui_script.exists():
                subprocess.Popen([
                    '/Users/colinmignot/miniforge3/bin/python3', str(gui_script), temp_path, Path(file_path).name
                ])
                print("✅ Done! GUI launched.")
                sys.exit(0)
        except Exception as e:
            print(f"GUI failed ({e}), using simple playback...")
        
        # Fallback to simple background play
        subprocess.Popen(['afplay', temp_path])
        print("🎵 Playing audio...")
        print("⏹️  To stop: killall afplay")
        print("✅ Done!")
        sys.exit(0)
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except subprocess.CalledProcessError:
        print("❌ Audio playback failed. Falling back to file save...")
        # Fallback: save file and open
        audio_path = f"quick-{Path(file_path).stem}.mp3"
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        subprocess.run(['open', audio_path])
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 fast_tts.py filename.md")
        print("Example: python3 fast_tts.py implementation-summary.md")
        sys.exit(1)
    
    fast_read(sys.argv[1])