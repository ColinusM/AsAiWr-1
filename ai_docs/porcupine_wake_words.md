# Picovoice Porcupine Wake Word Detection Guide

## Setup and Configuration

### Installation and API Key Setup

```python
# Install Porcupine
# pip install pvporcupine

import pvporcupine
import sounddevice as sd
import numpy as np
import threading
import time
from typing import List, Callable, Optional

class WakeWordDetector:
    """Wake word detection using Picovoice Porcupine"""
    
    def __init__(self, access_key: str, 
                 keywords: List[str] = None,
                 sensitivities: List[float] = None):
        """
        Initialize wake word detector
        
        Args:
            access_key: Picovoice access key
            keywords: List of wake words (built-in or custom)
            sensitivities: Detection sensitivity for each keyword (0.0-1.0)
        """
        self.access_key = access_key
        self.keywords = keywords or ['hey computer']
        self.sensitivities = sensitivities or [0.5] * len(self.keywords)
        
        self.porcupine = None
        self.audio_stream = None
        self.is_listening = False
        self.wake_word_callback = None
        
    def initialize(self):
        """Initialize Porcupine with specified keywords"""
        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=self.keywords,
                sensitivities=self.sensitivities
            )
            
            print(f"Porcupine initialized with keywords: {self.keywords}")
            print(f"Sample rate: {self.porcupine.sample_rate}")
            print(f"Frame length: {self.porcupine.frame_length}")
            
        except Exception as e:
            if "invalid access key" in str(e).lower():
                raise ValueError("Invalid Picovoice access key")
            elif "invalid keyword" in str(e).lower():
                raise ValueError(f"Invalid keyword(s): {self.keywords}")
            else:
                raise e
```

### Built-in Wake Words

```python
# Available built-in wake words (no training required)
BUILTIN_KEYWORDS = [
    'alexa', 'americano', 'blueberry', 'bumblebee', 'computer',
    'grapefruit', 'grasshopper', 'hey google', 'hey siri', 'jarvis',
    'ok google', 'picovoice', 'porcupine', 'terminator'
]

class PredefinedWakeWords:
    """Helper for built-in wake word configurations"""
    
    @staticmethod
    def get_computer_variants():
        """Get computer-related wake words"""
        return {
            'computer': 0.5,
            'hey computer': 0.5,
            'porcupine': 0.7,  # Higher sensitivity for backup
        }
        
    @staticmethod  
    def get_assistant_variants():
        """Get AI assistant style wake words"""
        return {
            'jarvis': 0.6,
            'computer': 0.5,
            'hey computer': 0.4,
        }
        
    @staticmethod
    def create_detector_for_profile(profile: str, access_key: str):
        """Create detector with predefined profile"""
        if profile == 'computer':
            config = PredefinedWakeWords.get_computer_variants()
        elif profile == 'assistant':
            config = PredefinedWakeWords.get_assistant_variants()
        else:
            raise ValueError(f"Unknown profile: {profile}")
            
        keywords = list(config.keys())
        sensitivities = list(config.values())
        
        return WakeWordDetector(access_key, keywords, sensitivities)
```

### Audio Processing for Wake Word Detection

```python
class WakeWordAudioProcessor:
    """Handle audio processing specifically for wake word detection"""
    
    def __init__(self, detector: WakeWordDetector, device_id: Optional[int] = None):
        self.detector = detector
        self.device_id = device_id
        self.audio_thread = None
        self._stop_event = threading.Event()
        
    def audio_callback(self, indata, frames, time, status):
        """Process audio for wake word detection"""
        if status:
            print(f"Wake word audio status: {status}")
            
        if not self.detector.is_listening:
            return
            
        # Convert audio to format expected by Porcupine
        audio = indata[:, 0] if indata.ndim > 1 else indata
        
        # Ensure we have the right number of samples
        if len(audio) >= self.detector.porcupine.frame_length:
            # Convert to int16 format required by Porcupine
            pcm = (audio[:self.detector.porcupine.frame_length] * 32767).astype(np.int16)
            
            # Process audio frame
            keyword_index = self.detector.porcupine.process(pcm)
            
            if keyword_index >= 0:
                detected_keyword = self.detector.keywords[keyword_index]
                print(f"Wake word detected: {detected_keyword}")
                
                if self.detector.wake_word_callback:
                    # Run callback in separate thread to avoid blocking audio
                    callback_thread = threading.Thread(
                        target=self.detector.wake_word_callback,
                        args=(detected_keyword, keyword_index)
                    )
                    callback_thread.daemon = True
                    callback_thread.start()
                    
    def start_listening(self):
        """Start always-listening wake word detection"""
        if not self.detector.porcupine:
            raise RuntimeError("Porcupine not initialized")
            
        self.detector.is_listening = True
        self._stop_event.clear()
        
        # Create audio stream with Porcupine's requirements
        self.detector.audio_stream = sd.InputStream(
            device=self.device_id,
            channels=1,
            samplerate=self.detector.porcupine.sample_rate,
            blocksize=self.detector.porcupine.frame_length,
            callback=self.audio_callback,
            dtype=np.float32
        )
        
        self.detector.audio_stream.start()
        print("Wake word detection started...")
        
    def stop_listening(self):
        """Stop wake word detection"""
        self.detector.is_listening = False
        self._stop_event.set()
        
        if self.detector.audio_stream:
            self.detector.audio_stream.stop()
            self.detector.audio_stream.close()
            self.detector.audio_stream = None
            
        print("Wake word detection stopped")
```

### Integration with Main Application

```python
class WakeWordManager:
    """Manage wake word detection lifecycle"""
    
    def __init__(self, access_key: str, main_app_callback: Callable):
        self.access_key = access_key
        self.main_app_callback = main_app_callback
        self.detector = None
        self.processor = None
        
    def setup_wake_words(self, keywords: List[str] = None, 
                        sensitivities: List[float] = None):
        """Setup wake word detection"""
        try:
            # Create detector
            self.detector = WakeWordDetector(
                access_key=self.access_key,
                keywords=keywords or ['computer'],
                sensitivities=sensitivities or [0.5]
            )
            
            # Set callback to trigger main application
            self.detector.wake_word_callback = self._on_wake_word_detected
            
            # Initialize Porcupine
            self.detector.initialize()
            
            # Create audio processor
            self.processor = WakeWordAudioProcessor(self.detector)
            
            return True
            
        except Exception as e:
            print(f"Wake word setup failed: {e}")
            return False
            
    def _on_wake_word_detected(self, keyword: str, index: int):
        """Handle wake word detection"""
        print(f"Wake word '{keyword}' triggered main application")
        
        # Briefly pause wake word detection to avoid conflicts
        self.pause_detection()
        
        # Trigger main application (start recording/transcription)
        try:
            self.main_app_callback(activation_method='wake_word', keyword=keyword)
        finally:
            # Resume wake word detection after a delay
            threading.Timer(3.0, self.resume_detection).start()
            
    def start_detection(self):
        """Start wake word detection"""
        if self.processor:
            self.processor.start_listening()
            
    def pause_detection(self):
        """Temporarily pause wake word detection"""
        if self.detector:
            self.detector.is_listening = False
            
    def resume_detection(self):
        """Resume wake word detection"""
        if self.detector:
            self.detector.is_listening = True
            
    def stop_detection(self):
        """Stop wake word detection"""
        if self.processor:
            self.processor.stop_listening()
            
    def cleanup(self):
        """Cleanup resources"""
        self.stop_detection()
        if self.detector and self.detector.porcupine:
            self.detector.porcupine.delete()
```

### Configuration and Tuning

```python
class WakeWordConfig:
    """Configuration management for wake word detection"""
    
    def __init__(self):
        self.profiles = {
            'sensitive': {
                'keywords': ['computer'],
                'sensitivities': [0.3],  # Lower threshold = more sensitive
                'description': 'High sensitivity, may have false positives'
            },
            'balanced': {
                'keywords': ['computer', 'hey computer'],
                'sensitivities': [0.5, 0.5],
                'description': 'Balanced sensitivity and accuracy'
            },
            'strict': {
                'keywords': ['hey computer'],
                'sensitivities': [0.7],  # Higher threshold = less sensitive
                'description': 'Low sensitivity, fewer false positives'
            },
            'multi_word': {
                'keywords': ['computer', 'jarvis', 'hey computer'],
                'sensitivities': [0.5, 0.6, 0.4],
                'description': 'Multiple wake word options'
            }
        }
        
    def get_profile(self, profile_name: str) -> dict:
        """Get configuration for a specific profile"""
        if profile_name not in self.profiles:
            raise ValueError(f"Unknown profile: {profile_name}")
        return self.profiles[profile_name]
        
    def create_custom_profile(self, name: str, keywords: List[str], 
                            sensitivities: List[float], description: str = ""):
        """Create custom wake word profile"""
        if len(keywords) != len(sensitivities):
            raise ValueError("Keywords and sensitivities must have same length")
            
        self.profiles[name] = {
            'keywords': keywords,
            'sensitivities': sensitivities,
            'description': description
        }
        
    def benchmark_sensitivity(self, access_key: str, test_audio_file: str = None):
        """Benchmark different sensitivity settings"""
        if not test_audio_file:
            print("No test audio provided, using interactive testing")
            return self._interactive_sensitivity_test(access_key)
            
        # TODO: Implement audio file testing
        results = {}
        for profile_name, config in self.profiles.items():
            # Test each profile with recorded audio
            pass
            
        return results
        
    def _interactive_sensitivity_test(self, access_key: str):
        """Interactive sensitivity testing"""
        print("Interactive sensitivity testing")
        print("Say 'computer' multiple times for each sensitivity level")
        
        results = {}
        for sensitivity in [0.3, 0.5, 0.7]:
            print(f"\nTesting sensitivity: {sensitivity}")
            
            detector = WakeWordDetector(
                access_key=access_key,
                keywords=['computer'],
                sensitivities=[sensitivity]
            )
            detector.initialize()
            
            detections = []
            
            def callback(keyword, index):
                detections.append(time.time())
                print(f"  Detection #{len(detections)}")
                
            detector.wake_word_callback = callback
            
            processor = WakeWordAudioProcessor(detector)
            processor.start_listening()
            
            input("Press Enter when done testing this sensitivity...")
            processor.stop_listening()
            detector.porcupine.delete()
            
            results[sensitivity] = len(detections)
            
        return results
```

### Error Handling and Recovery

```python
class RobustWakeWordDetector:
    """Wake word detector with error handling and recovery"""
    
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.detector = None
        self.processor = None
        self.restart_attempts = 0
        self.max_restart_attempts = 3
        
    def start_with_recovery(self, keywords: List[str] = None):
        """Start wake word detection with automatic recovery"""
        while self.restart_attempts < self.max_restart_attempts:
            try:
                self._start_detection(keywords)
                self.restart_attempts = 0  # Reset on success
                return True
                
            except Exception as e:
                self.restart_attempts += 1
                wait_time = min(2 ** self.restart_attempts, 10)
                
                print(f"Wake word detection failed (attempt {self.restart_attempts}): {e}")
                
                if self.restart_attempts < self.max_restart_attempts:
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max restart attempts reached, wake word detection disabled")
                    return False
                    
        return False
        
    def _start_detection(self, keywords: List[str]):
        """Internal method to start detection"""
        # Cleanup any existing detector
        if self.detector:
            self.cleanup()
            
        # Create new detector
        manager = WakeWordManager(self.access_key, self._dummy_callback)
        if not manager.setup_wake_words(keywords):
            raise RuntimeError("Failed to setup wake word detection")
            
        self.detector = manager.detector
        self.processor = manager.processor
        
        # Start detection
        manager.start_detection()
        
    def _dummy_callback(self, **kwargs):
        """Placeholder callback for testing"""
        pass
        
    def cleanup(self):
        """Cleanup resources"""
        if self.processor:
            self.processor.stop_listening()
        if self.detector and self.detector.porcupine:
            self.detector.porcupine.delete()
```

### Performance Optimization

```python
class OptimizedWakeWordDetection:
    """Optimized wake word detection for minimal resource usage"""
    
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.low_power_mode = False
        
    def enable_low_power_mode(self):
        """Enable low power mode for battery conservation"""
        self.low_power_mode = True
        
    def create_optimized_detector(self, keywords: List[str]):
        """Create detector optimized for performance"""
        # Use single keyword for better performance
        if len(keywords) > 1:
            print("Multiple keywords may impact performance, consider using single keyword")
            
        # Adjust sensitivity for fewer false positives in low power mode
        if self.low_power_mode:
            sensitivities = [0.7] * len(keywords)  # Less sensitive
        else:
            sensitivities = [0.5] * len(keywords)  # Balanced
            
        return WakeWordDetector(
            access_key=self.access_key,
            keywords=keywords,
            sensitivities=sensitivities
        )
        
    def monitor_cpu_usage(self):
        """Monitor CPU usage of wake word detection"""
        import psutil
        
        process = psutil.Process()
        cpu_usage = process.cpu_percent(interval=1.0)
        
        if cpu_usage > 10.0:  # High CPU usage threshold
            print(f"High CPU usage detected: {cpu_usage}%")
            print("Consider reducing wake word sensitivity or using fewer keywords")
            
        return cpu_usage
```

## Key Implementation Notes

1. **Access Key**: Requires valid Picovoice access key for operation
2. **Always Listening**: Runs in separate thread to avoid blocking main application  
3. **Resource Management**: Properly cleanup Porcupine resources to prevent memory leaks
4. **Audio Format**: Requires 16-bit PCM audio at Porcupine's sample rate
5. **Integration**: Coordinate with main STT application to avoid audio conflicts
6. **Sensitivity Tuning**: Balance false positives vs missed detections based on environment
7. **Error Recovery**: Handle microphone disconnection and permission changes gracefully