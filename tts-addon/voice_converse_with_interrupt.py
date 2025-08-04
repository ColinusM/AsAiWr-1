#!/usr/bin/env python3
"""
Voice Converse with Interrupt
Enhanced voice conversation with real-time interrupt capability
"""

import subprocess
import threading
import signal
import sys
import os
from pathlib import Path

class VoiceConverseWithInterrupt:
    def __init__(self):
        self.gui_process = None
        self.conversation_active = True
        
    def launch_interrupt_gui(self):
        """Launch the interrupt GUI in background"""
        try:
            script_dir = Path(__file__).parent
            gui_script = script_dir / "voice_interrupt_gui.py"
            
            self.gui_process = subprocess.Popen([
                sys.executable, str(gui_script)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("🗣️ Voice interrupt GUI launched (top-right corner)")
            print("⏹️  Press SPACE in GUI or click STOP to interrupt audio")
            return True
        except Exception as e:
            print(f"⚠️  GUI launch failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes"""
        if self.gui_process:
            try:
                self.gui_process.terminate()
                self.gui_process.wait(timeout=2)
            except:
                try:
                    self.gui_process.kill()
                except:
                    pass
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n🛑 Conversation interrupted")
        self.conversation_active = False
        self.cleanup()
        sys.exit(0)

def main():
    """Main function"""
    print("🚀 Starting Voice Converse with Interrupt...")
    
    # Set up interrupt handler
    conversation = VoiceConverseWithInterrupt()
    signal.signal(signal.SIGINT, conversation.signal_handler)
    signal.signal(signal.SIGTERM, conversation.signal_handler)
    
    # Launch interrupt GUI
    gui_launched = conversation.launch_interrupt_gui()
    
    if gui_launched:
        print("✅ Ready for voice conversation!")
        print("💡 Use Claude Code's /voice-mode:converse command normally")
        print("💡 The interrupt GUI will handle audio stopping")
        print("💡 Press Ctrl+C here to exit completely")
        
        try:
            # Keep this script running to maintain GUI
            while conversation.conversation_active:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("❌ Failed to launch interrupt GUI")
        print("💡 You can still use regular voice mode without interrupt")
    
    # Cleanup
    conversation.cleanup()
    print("👋 Voice interrupt system stopped")

if __name__ == "__main__":
    main()