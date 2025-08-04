#!/usr/bin/env python3
"""
Voice Mode Interrupt GUI
Real-time audio interruption control for voice conversations
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import signal
import os
import sys
import threading
import time
# import psutil  # Optional dependency
import json
from pathlib import Path

class VoiceInterruptController:
    def __init__(self):
        self.audio_processes = []
        self.is_active = False
        self.conversation_active = True
        
    def find_audio_processes(self):
        """Find all running audio processes (afplay, etc.) - fallback without psutil"""
        processes = []
        try:
            # Use pgrep as fallback
            result = subprocess.run(['pgrep', 'afplay'], capture_output=True, text=True)
            if result.returncode == 0:
                processes = [int(pid.strip()) for pid in result.stdout.split() if pid.strip()]
        except Exception as e:
            print(f"Error finding processes: {e}")
        return processes
    
    def stop_all_audio(self):
        """Stop all audio playback immediately"""
        stopped_count = 0
        
        # Method 1: Kill known audio processes
        audio_processes = self.find_audio_processes()
        for pid in audio_processes:
            try:
                os.kill(pid, signal.SIGTERM)
                stopped_count += 1
            except OSError:
                pass
        
        # Method 2: Killall common audio players
        try:
            subprocess.run(['killall', 'afplay'], capture_output=True)
            subprocess.run(['killall', 'aplay'], capture_output=True)
            subprocess.run(['killall', 'paplay'], capture_output=True)
        except:
            pass
        
        return stopped_count > 0
    
    def pause_all_audio(self):
        """Pause all audio playback"""
        paused_count = 0
        audio_processes = self.find_audio_processes()
        for pid in audio_processes:
            try:
                os.kill(pid, signal.SIGSTOP)
                paused_count += 1
            except OSError:
                pass
        return paused_count > 0
    
    def resume_all_audio(self):
        """Resume all audio playback"""
        resumed_count = 0
        audio_processes = self.find_audio_processes()
        for pid in audio_processes:
            try:
                os.kill(pid, signal.SIGCONT)
                resumed_count += 1
            except OSError:
                pass
        return resumed_count > 0

class VoiceInterruptGUI:
    def __init__(self):
        self.controller = VoiceInterruptController()
        self.is_paused = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("🗣️ Voice Interrupt")
        self.root.geometry("250x200")
        self.root.resizable(False, False)
        
        # Keep window on top and focus
        self.root.wm_attributes("-topmost", 1)
        self.root.attributes('-alpha', 0.9)  # Slight transparency
        
        # Position in top-right corner
        self.root.geometry("+{}+{}".format(
            self.root.winfo_screenwidth() - 270, 20
        ))
        
        # Create UI
        self.create_widgets()
        
        # Start monitoring
        self.monitor_audio()
        
    def create_widgets(self):
        """Create GUI controls"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🗣️ Voice Control", 
            font=("Arial", 14, "bold"),
            fg="#2196F3"
        )
        title_label.pack(pady=10)
        
        # Status indicator
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=5)
        
        self.status_dot = tk.Label(
            self.status_frame,
            text="🔴",
            font=("Arial", 16)
        )
        self.status_dot.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Listening...",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Main controls
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        # STOP button (large and prominent)
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ STOP",
            font=("Arial", 16, "bold"),
            width=10,
            height=2,
            bg="#f44336",
            fg="white",
            command=self.emergency_stop,
            relief=tk.RAISED,
            bd=3
        )
        self.stop_btn.pack(pady=5)
        
        # Secondary controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        
        self.pause_btn = tk.Button(
            control_frame,
            text="⏸️ Pause",
            font=("Arial", 12),
            width=8,
            command=self.toggle_pause
        )
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.close_btn = tk.Button(
            control_frame,
            text="❌ Close",
            font=("Arial", 12),
            width=8,
            command=self.close_app
        )
        self.close_btn.pack(side=tk.LEFT, padx=2)
        
        # Keyboard shortcuts info
        info_label = tk.Label(
            self.root,
            text="Shortcut: Space = Stop",
            font=("Arial", 8),
            fg="gray"
        )
        info_label.pack(pady=2)
        
        # Bind keyboard shortcuts
        self.root.bind('<space>', lambda e: self.emergency_stop())
        self.root.bind('<Escape>', lambda e: self.close_app())
        self.root.focus_set()  # Enable keyboard focus
        
    def emergency_stop(self):
        """Emergency stop all audio"""
        success = self.controller.stop_all_audio()
        if success:
            self.status_dot.config(text="🟡")
            self.status_label.config(text="Audio stopped", fg="orange")
            self.stop_btn.config(text="✅ Stopped", bg="#4CAF50")
            
            # Flash the button
            self.root.after(1000, self.reset_stop_button)
        else:
            self.status_label.config(text="No audio found", fg="gray")
    
    def reset_stop_button(self):
        """Reset stop button appearance"""
        self.stop_btn.config(text="⏹️ STOP", bg="#f44336")
        self.status_dot.config(text="🔴")
        self.status_label.config(text="Listening...", fg="green")
    
    def toggle_pause(self):
        """Toggle pause/resume"""
        if self.is_paused:
            success = self.controller.resume_all_audio()
            if success:
                self.pause_btn.config(text="⏸️ Pause")
                self.status_label.config(text="Resumed", fg="green")
                self.is_paused = False
        else:
            success = self.controller.pause_all_audio()
            if success:
                self.pause_btn.config(text="▶️ Resume")
                self.status_label.config(text="Paused", fg="orange")
                self.is_paused = True
    
    def monitor_audio(self):
        """Monitor audio processes"""
        def check_audio():
            while self.controller.conversation_active:
                processes = self.controller.find_audio_processes()
                if processes:
                    self.root.after(0, lambda: self.status_dot.config(text="🔊"))
                else:
                    self.root.after(0, lambda: self.status_dot.config(text="🔴"))
                time.sleep(0.5)
        
        monitor_thread = threading.Thread(target=check_audio, daemon=True)
        monitor_thread.start()
    
    def close_app(self):
        """Close the application"""
        self.controller.conversation_active = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        
        # Show instructions briefly
        self.show_instructions()
        
        self.root.mainloop()
    
    def show_instructions(self):
        """Show brief instructions"""
        original_title = self.root.title()
        self.root.title("🗣️ Voice Interrupt - Press SPACE to stop audio!")
        self.root.after(3000, lambda: self.root.title(original_title))

def main():
    """Launch the Voice Interrupt GUI"""
    print("🗣️ Starting Voice Interrupt GUI...")
    print("⏹️  Press SPACE or click STOP to interrupt audio")
    print("📍 GUI will appear in top-right corner")
    
    gui = VoiceInterruptGUI()
    gui.run()

if __name__ == "__main__":
    main()