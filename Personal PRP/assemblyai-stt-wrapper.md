# AssemblyAI Speech-to-Text Wrapper (SuperWhisper Alternative)

name: "AssemblyAI STT Wrapper - macOS Voice Input Application"
description: |
  A standalone macOS application that provides real-time speech-to-text transcription using AssemblyAI's streaming API, 
  with both manual hotkey activation and wake word detection, populating transcribed text directly into active applications.

## Goal

Build a production-ready macOS application that serves as a SuperWhisper alternative, providing seamless voice-to-text input across all applications using AssemblyAI's real-time streaming API.

### Feature Goal
Create a standalone macOS app (.app bundle) that users can launch and use immediately without developer registration or App Store deployment.

### Deliverable
- Packaged macOS application using PyInstaller
- Draggable popup interface similar to SuperWhisper
- Dual activation methods: Option+Space hotkey toggle and wake word detection
- Real-time streaming transcription with AssemblyAI
- Smart text insertion into active applications
- Audio device selection with Apollo Twin support

### Success Definition
- [ ] App launches and runs without Python installation required
- [ ] Successfully transcribes speech in real-time using AssemblyAI streaming API
- [ ] Hotkey activation works system-wide (Option+Space toggle)
- [ ] Wake word detection functions with configurable phrases
- [ ] Text populates correctly in various applications (TextEdit, Mail, VS Code, etc.)
- [ ] External audio devices (Apollo Twin) are selectable and functional
- [ ] Visual feedback popup matches SuperWhisper design reference

## Why

- **User Impact**: Enables hands-free text input across all macOS applications
- **Business Value**: Provides professional-grade STT alternative to SuperWhisper
- **Integration**: Seamlessly works with existing workflows and applications
- **Accessibility**: Improves productivity for users who prefer voice input

## What

### User-Visible Behavior
1. **Manual Activation**: Press Option+Space to start recording, press again to stop and transcribe
2. **Voice Activation**: Say wake word (e.g., "Hey Computer") to activate
3. **Visual Feedback**: Draggable popup window appears during recording
4. **Text Insertion**: Transcribed text automatically appears in active text field
5. **Device Selection**: Menu to choose microphone (built-in, Apollo Twin, etc.)

### Technical Requirements
- Real-time streaming STT using AssemblyAI API (API key: a1acc40bebd044b888d821c9de6c3d69)
- macOS Sequoia 15.5 compatibility
- PyInstaller packaged executable
- Global system hotkey handling
- Audio device enumeration and selection
- Cross-application text insertion
- Wake word detection with Picovoice Porcupine

### Success Criteria
- [ ] Sub-3 second latency from speech end to text insertion
- [ ] 95%+ transcription accuracy for clear speech
- [ ] Works across 10+ different applications
- [ ] Handles both built-in and external audio devices
- [ ] Startup time under 5 seconds

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- url: https://github.com/assemblyai/assemblyai-python-sdk/blob/master/README.md#_snippet_30
  why: Real-time streaming implementation with event handlers and microphone stream

- url: https://github.com/assemblyai/assemblyai-python-sdk/blob/master/README.md#_snippet_31  
  why: File streaming and audio format requirements

- docfile: PRPs/ai_docs/assemblyai_streaming_api.md
  why: Complete streaming API reference with WebSocket implementation details

- url: https://docs.assemblyai.com/docs/voice-agents/livekit-intro-guide
  why: Voice agent implementation patterns and best practices

- docfile: PRPs/ai_docs/macos_audio_capture.md
  why: sounddevice library implementation, device selection, and permission handling

- docfile: PRPs/ai_docs/porcupine_wake_words.md
  why: Wake word detection setup and configuration

- docfile: PRPs/ai_docs/macos_text_insertion.md
  why: PyAutoGUI and accessibility API usage for cross-app text insertion

- docfile: PRPs/ai_docs/pyinstaller_macos.md
  why: App packaging, code signing, and distribution setup
```

### Current Codebase Tree
```bash
# Starting point - no existing codebase
assemblyai-stt-wrapper/
├── README.md
├── requirements.txt
└── src/
    └── main.py
```

### Desired Codebase Tree with Files to be Added

```bash
assemblyai-stt-wrapper/
├── README.md
├── requirements.txt
├── setup.py
├── build_app.sh
├── src/
│   ├── main.py                    # Application entry point and GUI
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── capture.py             # Audio device management and capture
│   │   └── stream_handler.py      # AssemblyAI streaming integration
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── popup_window.py        # Draggable recording popup
│   │   └── settings_menu.py       # Audio device selection menu
│   ├── input/
│   │   ├── __init__.py
│   │   ├── hotkey_handler.py      # Global hotkey management
│   │   ├── wake_word.py           # Porcupine wake word detection
│   │   └── text_inserter.py       # Cross-application text insertion
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration management
│   └── utils/
│       ├── __init__.py
│       ├── permissions.py         # macOS permission handling
│       └── error_handler.py       # Error messaging and logging
├── assets/
│   ├── icons/
│   │   ├── microphone.png
│   │   └── app_icon.icns
│   └── sounds/
│       └── activation_chime.wav
├── tests/
│   ├── test_audio_capture.py
│   ├── test_streaming.py
│   └── test_text_insertion.py
└── dist/                          # PyInstaller output
    └── AssemblyAI-STT.app
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: AssemblyAI Streaming Requirements
# - Real-time API requires WebSocket connection
# - Audio must be PCM16, single channel, 16kHz sample rate
# - formatted_finals=True for proper punctuation
# - Handle connection drops and reconnection

# CRITICAL: macOS Audio Permissions
# - Requires microphone permission in System Settings
# - sounddevice may fail silently without permissions
# - Test with try/catch and guide users to settings

# CRITICAL: Global Hotkey Limitations
# - pynput works but may require accessibility permissions
# - Some apps may consume hotkeys before our handler
# - Option+Space conflicts with Spotlight - use Cmd+Shift+Space instead

# CRITICAL: PyInstaller macOS Packaging
# - Must include all audio libraries and dependencies
# - Code signing required for Gatekeeper (use ad-hoc for development)
# - App bundle structure must be correct for permissions

# CRITICAL: Wake Word Detection
# - Picovoice Porcupine requires valid access key
# - Run in separate thread to avoid blocking main audio stream
# - Must handle both wake word and regular transcription streams

# CRITICAL: Text Insertion Reliability
# - pyautogui requires accessibility permissions
# - Clipboard method most reliable across apps
# - Some apps may have paste restrictions
```

## Implementation Blueprint

### Data Models and Structure

```python
# Core data models for type safety and consistency

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Callable

class AppState(Enum):
    IDLE = "idle"
    LISTENING = "listening" 
    PROCESSING = "processing"
    ERROR = "error"

class ActivationMethod(Enum):
    HOTKEY = "hotkey"
    WAKE_WORD = "wake_word"

@dataclass
class AudioDevice:
    id: int
    name: str
    channels: int
    sample_rate: int
    is_default: bool

@dataclass
class TranscriptionResult:
    text: str
    confidence: float
    is_final: bool
    timestamp: float

@dataclass
class AppConfig:
    assemblyai_api_key: str
    wake_word_access_key: str
    audio_device_id: Optional[int]
    hotkey_combination: str
    wake_words: List[str]
    popup_position: tuple[int, int]
    
class AudioStreamCallback:
    def __init__(self, on_data: Callable, on_error: Callable):
        self.on_data = on_data
        self.on_error = on_error
```

### List of Tasks to be Completed

```yaml
Task 1:
CREATE src/config/settings.py:
  - IMPLEMENT AppConfig dataclass with validation
  - ADD API key management with environment variables
  - INCLUDE default configuration values
  - HANDLE configuration file save/load

Task 2:
CREATE src/utils/permissions.py:
  - IMPLEMENT microphone permission checking
  - ADD accessibility permission validation
  - CREATE permission request guidance functions
  - HANDLE macOS Sequoia specific requirements

Task 3:
CREATE src/audio/capture.py:
  - IMPLEMENT AudioDevice enumeration using sounddevice
  - ADD device selection and validation
  - CREATE audio stream management with proper error handling
  - SUPPORT external devices like Apollo Twin

Task 4:
CREATE src/audio/stream_handler.py:
  - IMPLEMENT AssemblyAI StreamingClient integration
  - ADD WebSocket connection management with reconnection
  - CREATE event handlers for Begin, Turn, Termination, Error
  - HANDLE audio format conversion (PCM16, 16kHz, mono)

Task 5:
CREATE src/input/wake_word.py:
  - IMPLEMENT Picovoice Porcupine integration
  - ADD configurable wake word detection
  - CREATE separate thread for always-listening
  - HANDLE wake word activation callbacks

Task 6:
CREATE src/input/hotkey_handler.py:
  - IMPLEMENT global hotkey using pynput
  - ADD Cmd+Shift+Space toggle functionality
  - CREATE hotkey registration and cleanup
  - HANDLE permission requirements

Task 7:
CREATE src/input/text_inserter.py:
  - IMPLEMENT cross-application text insertion
  - ADD clipboard-based text insertion method
  - CREATE app-specific behavior handling
  - HANDLE text formatting and cursor positioning

Task 8:
CREATE src/ui/popup_window.py:
  - IMPLEMENT draggable popup using tkinter
  - ADD SuperWhisper-style interface design
  - CREATE recording indicator and status display
  - HANDLE window positioning and persistence

Task 9:
CREATE src/ui/settings_menu.py:
  - IMPLEMENT audio device selection menu
  - ADD wake word configuration interface
  - CREATE hotkey customization options
  - HANDLE settings persistence

Task 10:
CREATE src/main.py:
  - IMPLEMENT application startup and initialization
  - ADD state management and coordination
  - CREATE error handling and user feedback
  - INTEGRATE all components into main application loop

Task 11:
CREATE build_app.sh:
  - IMPLEMENT PyInstaller packaging script
  - ADD asset bundling and icon setup
  - CREATE app bundle structure
  - HANDLE code signing for distribution
```

### Per Task Pseudocode

```python
# Task 4: AssemblyAI Streaming Integration
import assemblyai as aai
from assemblyai.streaming.v3 import StreamingClient, StreamingEvents

class AssemblyAIStreamHandler:
    def __init__(self, api_key: str, on_transcript: Callable):
        self.client = StreamingClient(
            StreamingClientOptions(api_key=api_key)
        )
        self.on_transcript = on_transcript
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        # PATTERN: Event-driven architecture for real-time responses
        self.client.on(StreamingEvents.Turn, self._on_turn)
        self.client.on(StreamingEvents.Error, self._on_error)
        
    def _on_turn(self, event: TurnEvent):
        # CRITICAL: Only process final transcripts for text insertion
        if event.message_type == "FinalTranscript":
            self.on_transcript(TranscriptionResult(
                text=event.transcript,
                confidence=event.confidence,
                is_final=True,
                timestamp=time.time()
            ))
    
    def start_stream(self, audio_stream):
        # GOTCHA: Must handle connection failures gracefully
        try:
            self.client.connect(StreamingParameters(
                sample_rate=16_000,
                formatted_finals=True  # Essential for proper punctuation
            ))
            self.client.stream(audio_stream)
        except Exception as e:
            self._handle_connection_error(e)

# Task 6: Global Hotkey Implementation  
from pynput import keyboard
import threading

class HotkeyHandler:
    def __init__(self, combination: str, callback: Callable):
        self.combination = self._parse_combination(combination)
        self.callback = callback
        self.is_pressed = False
        
    def _parse_combination(self, combo: str):
        # PATTERN: Parse "Cmd+Shift+Space" into key set
        parts = combo.split('+')
        keys = set()
        for part in parts:
            if part == "Cmd":
                keys.add(keyboard.Key.cmd)
            elif part == "Shift": 
                keys.add(keyboard.Key.shift)
            elif part == "Space":
                keys.add(keyboard.Key.space)
        return keys
        
    def start_listening(self):
        # CRITICAL: Run in separate thread to avoid blocking
        listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        listener.start()
        return listener

# Task 7: Text Insertion Implementation
import pyautogui
import pyperclip
import time

class TextInserter:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def insert_text(self, text: str, append: bool = True):
        # PATTERN: Clipboard method most reliable across apps
        original_clipboard = pyperclip.paste()
        
        try:
            # Set new text to clipboard
            pyperclip.copy(text)
            
            # Insert via paste command
            if not append:
                pyautogui.hotkey('cmd', 'a')  # Select all first
                time.sleep(0.1)
            
            pyautogui.hotkey('cmd', 'v')  # Paste
            
        finally:
            # CRITICAL: Restore original clipboard after delay
            time.sleep(0.5)
            pyperclip.copy(original_clipboard)
```

### Integration Points

```yaml
DEPENDENCIES:
  - requirements.txt: "assemblyai>=0.30.0, sounddevice>=0.4.6, pynput>=1.7.6, pyautogui>=0.9.54, pyperclip>=1.8.2, pvporcupine>=3.0.0"

CONFIG:
  - environment: "ASSEMBLYAI_API_KEY=a1acc40bebd044b888d821c9de6c3d69"
  - environment: "PICOVOICE_ACCESS_KEY=your_porcupine_key"
  - config_file: "~/.assemblyai-stt/config.json"

PERMISSIONS:
  - microphone: "Required for audio capture"
  - accessibility: "Required for global hotkeys and text insertion"
  - network: "Required for AssemblyAI API calls"

AUDIO_FORMATS:
  - input: "Any format supported by sounddevice"
  - processing: "PCM16, 16kHz, mono for AssemblyAI"
  - conversion: "Automatic format conversion in stream handler"
```

## Validation Loop

### Level 1: Syntax & Style

```bash
# Run these FIRST - fix any errors before proceeding
python -m flake8 src/ --max-line-length=88
python -m black src/ --check
python -m mypy src/ --strict

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests

```python
# CREATE test_audio_capture.py
def test_device_enumeration():
    """Test audio device listing works"""
    capture = AudioCapture()
    devices = capture.list_devices()
    assert len(devices) > 0
    assert any(d.is_default for d in devices)

def test_apollo_twin_detection():
    """Test Apollo Twin device detection"""
    capture = AudioCapture()
    apollo_device = capture.find_device("apollo")
    # Should find device or return None gracefully

def test_permission_checking():
    """Test microphone permission validation"""
    from src.utils.permissions import check_microphone_permission
    result = check_microphone_permission()
    assert isinstance(result, bool)

# CREATE test_streaming.py  
def test_assemblyai_connection():
    """Test AssemblyAI streaming connection"""
    handler = AssemblyAIStreamHandler(api_key="test_key")
    # Should handle invalid API key gracefully
    
def test_audio_format_conversion():
    """Test audio format conversion for AssemblyAI"""
    # Test conversion from various input formats to PCM16

# CREATE test_text_insertion.py
def test_text_insertion():
    """Test text insertion into test application"""
    inserter = TextInserter()
    test_text = "Hello, world!"
    # Test insertion without breaking existing text
```

```bash
# Run and iterate until passing:
python -m pytest tests/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test

```bash
# Test complete workflow
python src/main.py --test-mode

# Manual testing checklist:
# 1. Launch app - should show system tray icon
# 2. Press Cmd+Shift+Space - popup should appear
# 3. Speak "Hello world" - should transcribe and insert
# 4. Say wake word - should activate without hotkey
# 5. Test with TextEdit, Mail, VS Code applications
# 6. Test Apollo Twin device selection
# 7. Test error handling with no internet
```

### Level 4: Deployment & Creative Validation

```bash
# Build standalone app
./build_app.sh

# Test packaged app
open dist/AssemblyAI-STT.app

# Performance validation
# - Measure startup time (should be < 5 seconds)
# - Measure transcription latency (should be < 3 seconds)
# - Test memory usage during extended sessions
# - Validate audio quality with different devices

# User experience validation
# - Test with various accents and speaking speeds
# - Validate across different macOS applications
# - Check behavior during system sleep/wake
# - Test graceful handling of API rate limits
```

## Final Validation Checklist

- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] No linting errors: `python -m flake8 src/`
- [ ] No type errors: `python -m mypy src/ --strict`
- [ ] Manual test successful: App launches and transcribes speech
- [ ] Error cases handled gracefully: No internet, no permissions
- [ ] Logs are informative but not verbose
- [ ] PyInstaller build completes without errors
- [ ] App works on fresh macOS system without Python
- [ ] Performance meets requirements (< 3s latency, < 5s startup)

## Anti-Patterns to Avoid

- ❌ Don't create audio processing loops that block the main thread
- ❌ Don't skip permission checks - handle gracefully with user guidance
- ❌ Don't ignore AssemblyAI connection errors - implement retry logic
- ❌ Don't hardcode API keys - use environment variables
- ❌ Don't assume clipboard access - some apps restrict pasting
- ❌ Don't skip audio format validation - AssemblyAI requires specific formats
- ❌ Don't create memory leaks in continuous audio streams
- ❌ Don't ignore macOS Sequoia security restrictions