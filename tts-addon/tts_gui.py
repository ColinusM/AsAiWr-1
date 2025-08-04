#!/usr/bin/env python3
"""
TTS GUI Control Panel
Provides pause/stop/resume controls for TTS playback
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import signal
import os
import sys
import threading
import time

class TTSController:
    def __init__(self):
        self.afplay_pid = None
        self.is_playing = False
        self.is_paused = False
        
    def start_playback(self, audio_file):
        """Start audio playback"""
        try:
            self.process = subprocess.Popen(['afplay', audio_file])
            self.afplay_pid = self.process.pid
            self.is_playing = True
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Error starting playback: {e}")
            return False
    
    def pause_playback(self):
        """Pause audio playback"""
        if self.afplay_pid and self.is_playing and not self.is_paused:
            try:
                os.kill(self.afplay_pid, signal.SIGSTOP)
                self.is_paused = True
                return True
            except:
                return False
        return False
    
    def resume_playback(self):
        """Resume audio playback"""
        if self.afplay_pid and self.is_playing and self.is_paused:
            try:
                os.kill(self.afplay_pid, signal.SIGCONT)
                self.is_paused = False
                return True
            except:
                return False
        return False
    
    def stop_playback(self):
        """Stop audio playback"""
        if self.afplay_pid:
            try:
                os.kill(self.afplay_pid, signal.SIGTERM)
                self.is_playing = False
                self.is_paused = False
                self.afplay_pid = None
                return True
            except:
                return False
        return False

class TTSControlGUI:
    def __init__(self, audio_file, filename):
        self.controller = TTSController()
        self.audio_file = audio_file
        self.filename = filename
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("TTS Control")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        
        # Keep window on top
        self.root.wm_attributes("-topmost", 1)
        
        # Create UI
        self.create_widgets()
        
        # Start playback immediately
        self.start_playback()
        
        # Monitor playback status
        self.monitor_playback()
        
    def create_widgets(self):
        """Create GUI controls"""
        # Title label
        title_label = tk.Label(
            self.root, 
            text=f"🎵 {self.filename}", 
            font=("Arial", 12, "bold"),
            wraplength=280
        )
        title_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Play/Pause button
        self.play_pause_btn = tk.Button(
            button_frame,
            text="⏸️ Pause",
            font=("Arial", 14),
            width=8,
            command=self.toggle_play_pause
        )
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Stop",
            font=("Arial", 14),
            width=8,
            command=self.stop_and_close
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="▶️ Playing...",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(pady=5)
        
        # Progress bar (fake - just for visual feedback)
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, padx=20, pady=5)
        self.progress.start(10)
    
    def start_playback(self):
        """Start audio playback"""
        if self.controller.start_playback(self.audio_file):
            self.status_label.config(text="▶️ Playing...", fg="green")
        else:
            self.status_label.config(text="❌ Playback failed", fg="red")
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.controller.is_paused:
            if self.controller.resume_playback():
                self.play_pause_btn.config(text="⏸️ Pause")
                self.status_label.config(text="▶️ Playing...", fg="green")
                self.progress.start(10)
        else:
            if self.controller.pause_playback():
                self.play_pause_btn.config(text="▶️ Resume")
                self.status_label.config(text="⏸️ Paused", fg="orange")
                self.progress.stop()
    
    def stop_and_close(self):
        """Stop playback and close GUI"""
        self.controller.stop_playback()
        self.root.quit()
        self.root.destroy()
    
    def monitor_playback(self):
        """Monitor if playback is still running"""
        def check_status():
            while True:
                if self.controller.afplay_pid:
                    try:
                        # Check if process is still running
                        os.kill(self.controller.afplay_pid, 0)
                        time.sleep(0.5)
                    except OSError:
                        # Process ended naturally
                        self.root.after(0, self.playback_finished)
                        break
                else:
                    break
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=check_status, daemon=True)
        monitor_thread.start()
    
    def playback_finished(self):
        """Called when playback finishes naturally"""
        self.status_label.config(text="✅ Finished", fg="blue")
        self.play_pause_btn.config(text="🔄 Replay", command=self.restart_playback)
        self.progress.stop()
    
    def restart_playback(self):
        """Restart playback from beginning"""
        self.start_playback()
        self.play_pause_btn.config(text="⏸️ Pause", command=self.toggle_play_pause)
        self.progress.start(10)
    
    def run(self):
        """Run the GUI"""
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.stop_and_close)
        
        # Start GUI loop
        self.root.mainloop()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 tts_gui.py <audio_file> <filename>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    filename = sys.argv[2]
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        sys.exit(1)
    
    # Create and run GUI
    gui = TTSControlGUI(audio_file, filename)
    gui.run()

if __name__ == "__main__":
    main()