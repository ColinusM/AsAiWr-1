# macOS Audio Capture Implementation Guide

## sounddevice Library - Primary Choice

### Device Enumeration and Selection

```python
import sounddevice as sd
import numpy as np
from typing import List, Optional, Dict, Any

class AudioDevice:
    def __init__(self, device_info: Dict[str, Any], device_id: int):
        self.id = device_id
        self.name = device_info['name']
        self.channels = device_info['max_input_channels']
        self.sample_rate = int(device_info['default_samplerate'])
        self.is_default = device_id == sd.default.device[0]  # Input device
        self.hostapi = device_info['hostapi']
        
    def __str__(self):
        default_marker = " (Default)" if self.is_default else ""
        return f"{self.name} - {self.channels} channels{default_marker}"

class AudioCapture:
    def __init__(self):
        self.current_device = None
        self.stream = None
        
    def list_devices(self) -> List[AudioDevice]:
        """List all available input devices"""
        devices = []
        device_list = sd.query_devices()
        
        for i, device_info in enumerate(device_list):
            # Only include input devices
            if device_info['max_input_channels'] > 0:
                devices.append(AudioDevice(device_info, i))
                
        return devices
        
    def find_device_by_name(self, name_pattern: str) -> Optional[AudioDevice]:
        """Find device by name pattern (case-insensitive)"""
        devices = self.list_devices()
        for device in devices:
            if name_pattern.lower() in device.name.lower():
                return device
        return None
        
    def get_default_device(self) -> AudioDevice:
        """Get the system default input device"""
        default_id = sd.default.device[0]
        device_info = sd.query_devices(default_id)
        return AudioDevice(device_info, default_id)
```

### Apollo Twin and Professional Audio Interface Support

```python
class ProfessionalAudioSupport:
    """Support for professional audio interfaces like Apollo Twin"""
    
    KNOWN_INTERFACES = {
        'apollo': ['apollo', 'universal audio', 'uad'],
        'focusrite': ['focusrite', 'scarlett', 'clarett'],
        'rme': ['rme', 'fireface', 'babyface'],
        'motu': ['motu', 'ultralite', 'traveler'],
        'apogee': ['apogee', 'ensemble', 'duet']
    }
    
    def detect_professional_interfaces(self) -> Dict[str, List[AudioDevice]]:
        """Detect and categorize professional audio interfaces"""
        capture = AudioCapture()
        all_devices = capture.list_devices()
        
        categorized = {}
        for category, patterns in self.KNOWN_INTERFACES.items():
            categorized[category] = []
            for device in all_devices:
                if any(pattern in device.name.lower() for pattern in patterns):
                    categorized[category].append(device)
                    
        return categorized
        
    def get_optimal_settings_for_device(self, device: AudioDevice) -> Dict[str, Any]:
        """Get optimal audio settings for specific professional interfaces"""
        device_name = device.name.lower()
        
        # Apollo Twin specific optimizations
        if 'apollo' in device_name:
            return {
                'sample_rate': 48000,  # Apollo Twin native rate
                'channels': 1,
                'blocksize': 256,      # Low latency
                'dtype': np.float32
            }
            
        # Focusrite Scarlett series
        elif 'scarlett' in device_name or 'focusrite' in device_name:
            return {
                'sample_rate': 44100,
                'channels': 1,
                'blocksize': 512,
                'dtype': np.float32
            }
            
        # Default professional settings
        else:
            return {
                'sample_rate': 44100,
                'channels': 1,
                'blocksize': 1024,
                'dtype': np.float32
            }
```

### Real-time Audio Streaming

```python
import queue
import threading
import time

class RealTimeAudioStream:
    def __init__(self, device_id: Optional[int] = None, 
                 sample_rate: int = 16000, channels: int = 1,
                 blocksize: int = 1024):
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        
        self.audio_queue = queue.Queue(maxsize=50)  # Prevent memory buildup
        self.stream = None
        self.is_recording = False
        
    def audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
            
        if self.is_recording:
            try:
                # Convert to format suitable for AssemblyAI
                audio_data = indata[:, 0] if indata.shape[1] > 1 else indata.flatten()
                
                # Resample if needed (AssemblyAI wants 16kHz)
                if self.sample_rate != 16000:
                    audio_data = self._resample_audio(audio_data, self.sample_rate, 16000)
                
                self.audio_queue.put(audio_data.copy(), block=False)
                
            except queue.Full:
                # Drop frames if queue is full to prevent blocking
                print("Audio queue full, dropping frames")
                
    def _resample_audio(self, audio_data, orig_sr, target_sr):
        """Simple resampling for real-time processing"""
        if orig_sr == target_sr:
            return audio_data
            
        # Use scipy for real-time resampling if available
        try:
            from scipy import signal
            num_samples = int(len(audio_data) * target_sr / orig_sr)
            return signal.resample(audio_data, num_samples)
        except ImportError:
            # Fallback: simple decimation/interpolation
            ratio = target_sr / orig_sr
            indices = np.arange(0, len(audio_data), 1/ratio).astype(int)
            return audio_data[indices]
            
    def start_stream(self):
        """Start the audio stream"""
        try:
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.blocksize,
                callback=self.audio_callback,
                dtype=np.float32
            )
            self.stream.start()
            print(f"Audio stream started on device {self.device_id}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start audio stream: {e}")
            
    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Get next audio chunk from queue"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def stop_stream(self):
        """Stop and cleanup audio stream"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Clear any remaining audio data
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
```

### Permission Handling for macOS

```python
import subprocess
import os
from typing import Tuple

class MacOSAudioPermissions:
    """Handle macOS audio permissions and setup"""
    
    def check_microphone_permission(self) -> bool:
        """Check if app has microphone permission"""
        try:
            # Try to create a short audio stream
            test_stream = sd.InputStream(
                samplerate=16000, 
                channels=1, 
                blocksize=256
            )
            test_stream.start()
            time.sleep(0.1)  # Brief test
            test_stream.stop()
            test_stream.close()
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            if "device unavailable" in error_msg or "permission" in error_msg:
                return False
            # Other errors might not be permission-related
            raise e
            
    def request_microphone_permission(self):
        """Guide user to enable microphone permission"""
        print("Microphone access required!")
        print("Please enable microphone access:")
        print("1. Go to System Preferences → Security & Privacy → Privacy")
        print("2. Select 'Microphone' from the left sidebar")
        print("3. Check the box next to your Python interpreter or Terminal")
        
        # Open system preferences
        try:
            subprocess.run([
                "open", 
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
            ])
        except:
            subprocess.run(["open", "/System/Library/PreferencePanes/Security.prefPane"])
            
    def get_system_audio_info(self) -> Dict[str, Any]:
        """Get system audio configuration info"""
        try:
            # Get system version for compatibility checks
            version_output = subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()
            major_version = int(version_output.split('.')[0])
            
            # Get audio device info from system_profiler
            audio_output = subprocess.check_output([
                'system_profiler', 'SPAudioDataType', '-json'
            ]).decode()
            
            return {
                'macos_version': version_output,
                'major_version': major_version,
                'audio_devices': audio_output,
                'sequoia_or_later': major_version >= 15
            }
            
        except Exception as e:
            print(f"Could not get system audio info: {e}")
            return {}
            
    def handle_sequoia_permissions(self) -> bool:
        """Handle enhanced permissions in macOS Sequoia"""
        system_info = self.get_system_audio_info()
        
        if system_info.get('sequoia_or_later', False):
            print("macOS Sequoia detected - enhanced privacy controls active")
            
            # Check for monthly permission reauthorization requirements
            if not self.check_microphone_permission():
                print("Enhanced permission check required for Sequoia")
                self.request_microphone_permission()
                return False
                
        return True
```

### Audio Device Configuration UI

```python
import tkinter as tk
from tkinter import ttk

class AudioDeviceSelector:
    """GUI for selecting audio input device"""
    
    def __init__(self, parent=None, callback=None):
        self.parent = parent
        self.callback = callback
        self.selected_device = None
        
    def create_device_menu(self) -> tk.Menu:
        """Create menu for device selection"""
        menu = tk.Menu(self.parent, tearoff=0)
        
        capture = AudioCapture()
        devices = capture.list_devices()
        
        for device in devices:
            menu.add_command(
                label=str(device),
                command=lambda d=device: self.select_device(d)
            )
            
        return menu
        
    def select_device(self, device: AudioDevice):
        """Handle device selection"""
        self.selected_device = device
        if self.callback:
            self.callback(device)
            
    def show_device_info(self, device: AudioDevice):
        """Show detailed device information"""
        info_window = tk.Toplevel(self.parent)
        info_window.title(f"Device Info: {device.name}")
        
        info_text = f"""
Device: {device.name}
ID: {device.id}
Channels: {device.channels}
Sample Rate: {device.sample_rate} Hz
Default: {'Yes' if device.is_default else 'No'}
Host API: {device.hostapi}
        """
        
        label = tk.Label(info_window, text=info_text, justify=tk.LEFT)
        label.pack(padx=20, pady=20)
```

### Performance Optimization

```python
class OptimizedAudioCapture:
    """Optimized audio capture for minimal latency"""
    
    def __init__(self, target_latency_ms: int = 50):
        self.target_latency = target_latency_ms / 1000.0  # Convert to seconds
        self.optimal_settings = self._calculate_optimal_settings()
        
    def _calculate_optimal_settings(self) -> Dict[str, Any]:
        """Calculate optimal settings for target latency"""
        sample_rate = 16000  # AssemblyAI requirement
        
        # Calculate blocksize for target latency
        # latency = blocksize / sample_rate
        blocksize = int(self.target_latency * sample_rate)
        
        # Ensure blocksize is power of 2 for efficiency
        blocksize = 2 ** int(np.log2(blocksize))
        blocksize = max(64, min(blocksize, 2048))  # Reasonable bounds
        
        return {
            'sample_rate': sample_rate,
            'blocksize': blocksize,
            'channels': 1,
            'dtype': np.float32,
            'latency': 'low'  # Request low latency from PortAudio
        }
        
    def create_optimized_stream(self, device_id: Optional[int] = None):
        """Create audio stream optimized for low latency"""
        settings = self.optimal_settings.copy()
        settings['device'] = device_id
        
        return sd.InputStream(**settings)
        
    def benchmark_device_latency(self, device_id: int) -> float:
        """Measure actual latency for a device"""
        test_duration = 1.0  # seconds
        latencies = []
        
        def callback(indata, frames, time, status):
            if status:
                return
            # Simple latency measurement using callback timing
            callback_time = time.inputBufferAdcTime
            current_time = time.currentTime
            latency = current_time - callback_time
            latencies.append(latency)
            
        settings = self.optimal_settings.copy()
        settings['device'] = device_id
        settings['callback'] = callback
        
        with sd.InputStream(**settings):
            time.sleep(test_duration)
            
        return np.mean(latencies) if latencies else float('inf')
```

## Key Implementation Notes

1. **Device Compatibility**: Test with both built-in and professional audio interfaces
2. **Permission Handling**: Always check and request microphone permissions gracefully
3. **Format Conversion**: Convert audio to 16kHz mono for AssemblyAI compatibility
4. **Latency Optimization**: Use appropriate blocksize for target latency
5. **Error Recovery**: Handle device disconnection and reconnection gracefully
6. **macOS Sequoia**: Account for enhanced privacy controls in newer macOS versions