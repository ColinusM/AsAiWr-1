# AssemblyAI Streaming API Reference

## Real-Time Speech-to-Text Implementation

### Core Streaming Components

```python
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    TerminationEvent,
    TurnEvent,
)

# Essential event handlers for real-time processing
def on_begin(client, event: BeginEvent):
    """Connection established - store session ID for debugging"""
    print(f"Session started: {event.id}")

def on_turn(client, event: TurnEvent):
    """New transcript received - this is where you get text results"""
    # CRITICAL: Check message type for final transcripts
    if hasattr(event, 'message_type') and event.message_type == "FinalTranscript":
        # This is the final, formatted text ready for insertion
        formatted_text = event.transcript
        insert_text_to_active_app(formatted_text)
    else:
        # Partial transcript - good for real-time display
        partial_text = event.transcript

def on_terminated(client, event: TerminationEvent):
    """Session ended - cleanup resources"""
    print(f"Processed {event.audio_duration_seconds}s of audio")

def on_error(client, error: StreamingError):
    """Handle connection errors and API issues"""
    if "unauthorized" in str(error).lower():
        show_error("Invalid API key")
    elif "network" in str(error).lower():
        show_error("No internet connection")
    else:
        show_error(f"Transcription error: {error}")
```

### Streaming Client Setup

```python
class AssemblyAIStreamer:
    def __init__(self, api_key: str):
        self.client = StreamingClient(
            StreamingClientOptions(api_key=api_key)
        )
        self._setup_events()
        
    def _setup_events(self):
        """Register all event handlers"""
        self.client.on(StreamingEvents.Begin, on_begin)
        self.client.on(StreamingEvents.Turn, on_turn)
        self.client.on(StreamingEvents.Termination, on_terminated)
        self.client.on(StreamingEvents.Error, on_error)
        
    def start_transcription(self, audio_source):
        """Start streaming transcription"""
        # CRITICAL: These parameters are required for best results
        params = StreamingParameters(
            sample_rate=16_000,           # Must match your audio source
            formatted_finals=True,       # Enables punctuation and capitalization
            end_utterance_silence_threshold=1000  # Milliseconds of silence before finalizing
        )
        
        try:
            self.client.connect(params)
            self.client.stream(audio_source)
        except Exception as e:
            self.handle_connection_error(e)
            
    def stop_transcription(self):
        """Cleanly disconnect from streaming service"""
        if self.client:
            self.client.disconnect()
```

### Audio Source Integration

```python
# Using microphone stream (recommended for real-time)
def create_microphone_stream():
    """Create microphone stream compatible with AssemblyAI"""
    return aai.extras.MicrophoneStream(
        sample_rate=16_000,
        chunk_size=1024
    )

# Using custom audio source
import sounddevice as sd
import queue
import threading

class CustomAudioStream:
    def __init__(self, device_id=None, sample_rate=16_000):
        self.sample_rate = sample_rate
        self.device_id = device_id
        self.audio_queue = queue.Queue()
        
    def start_stream(self):
        """Start audio capture stream"""
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            # Convert to bytes for AssemblyAI
            audio_bytes = (indata * 32767).astype('int16').tobytes()
            self.audio_queue.put(audio_bytes)
            
        self.stream = sd.InputStream(
            device=self.device_id,
            channels=1,                    # CRITICAL: AssemblyAI requires mono
            samplerate=self.sample_rate,
            dtype='float32',
            callback=audio_callback
        )
        self.stream.start()
        
    def read(self):
        """Read audio data for streaming"""
        return self.audio_queue.get()
        
    def close(self):
        """Stop audio stream"""
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
```

### Error Handling and Reconnection

```python
class RobustStreamer:
    def __init__(self, api_key: str, max_retries: int = 3):
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_count = 0
        self.is_connected = False
        
    def connect_with_retry(self, audio_source):
        """Connect with automatic retry logic"""
        while self.retry_count < self.max_retries:
            try:
                self.client.connect(StreamingParameters(
                    sample_rate=16_000,
                    formatted_finals=True
                ))
                self.is_connected = True
                self.retry_count = 0  # Reset on successful connection
                break
                
            except Exception as e:
                self.retry_count += 1
                wait_time = min(2 ** self.retry_count, 10)  # Exponential backoff
                print(f"Connection failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
                
        if not self.is_connected:
            raise ConnectionError("Failed to connect after maximum retries")
            
    def handle_disconnect(self):
        """Handle unexpected disconnections"""
        self.is_connected = False
        # Attempt to reconnect automatically
        if self.retry_count < self.max_retries:
            self.connect_with_retry(self.audio_source)
```

### Performance Optimizations

```python
# Audio format conversion for optimal performance
def optimize_audio_for_assemblyai(audio_data, original_sample_rate):
    """Convert audio to AssemblyAI's preferred format"""
    import librosa
    
    # Resample to 16kHz if needed
    if original_sample_rate != 16_000:
        audio_data = librosa.resample(
            audio_data, 
            orig_sr=original_sample_rate, 
            target_sr=16_000
        )
    
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = librosa.to_mono(audio_data)
        
    # Convert to int16 format
    audio_int16 = (audio_data * 32767).astype('int16')
    
    return audio_int16.tobytes()

# Buffering for consistent streaming
class AudioBuffer:
    def __init__(self, chunk_size: int = 1024):
        self.chunk_size = chunk_size
        self.buffer = bytearray()
        
    def add_audio(self, audio_bytes: bytes):
        """Add audio data to buffer"""
        self.buffer.extend(audio_bytes)
        
    def get_chunks(self):
        """Get buffered chunks ready for streaming"""
        chunks = []
        while len(self.buffer) >= self.chunk_size:
            chunk = bytes(self.buffer[:self.chunk_size])
            chunks.append(chunk)
            self.buffer = self.buffer[self.chunk_size:]
        return chunks
```

### Command Word Detection

```python
def setup_command_detection(streamer):
    """Setup detection of command words like 'stop' within transcription"""
    
    def enhanced_turn_handler(client, event: TurnEvent):
        text = event.transcript.lower()
        
        # Check for stop commands
        stop_commands = ['stop', 'stop recording', 'end transcription']
        if any(cmd in text for cmd in stop_commands):
            # Remove the command from the text
            cleaned_text = text
            for cmd in stop_commands:
                cleaned_text = cleaned_text.replace(cmd, '').strip()
            
            if cleaned_text:  # Insert remaining text if any
                insert_text_to_active_app(cleaned_text)
                
            # Stop the transcription session
            client.disconnect()
            return
            
        # Normal text insertion
        if event.message_type == "FinalTranscript":
            insert_text_to_active_app(event.transcript)
    
    # Replace the default turn handler
    streamer.client.on(StreamingEvents.Turn, enhanced_turn_handler)
```

### Configuration Best Practices

```python
# Optimal configuration for different use cases
CONFIGS = {
    "high_accuracy": StreamingParameters(
        sample_rate=16_000,
        formatted_finals=True,
        end_utterance_silence_threshold=2000,  # Longer silence for complete thoughts
        disable_partial_transcripts=False      # Keep partial for UI feedback
    ),
    
    "low_latency": StreamingParameters(
        sample_rate=16_000,
        formatted_finals=True,
        end_utterance_silence_threshold=500,   # Shorter silence for quick response
        disable_partial_transcripts=True       # Skip partials for speed
    ),
    
    "voice_commands": StreamingParameters(
        sample_rate=16_000,
        formatted_finals=True,
        end_utterance_silence_threshold=1000,
        word_boost=["stop", "cancel", "delete", "undo"]  # Boost command recognition
    )
}
```

### Testing and Debugging

```python
# Debug mode for development
class DebugStreamer(AssemblyAIStreamer):
    def __init__(self, api_key: str, debug: bool = False):
        super().__init__(api_key)
        self.debug = debug
        
    def _setup_events(self):
        """Enhanced event handlers with debugging"""
        def debug_on_turn(client, event):
            if self.debug:
                print(f"Transcript: {event.transcript}")
                print(f"Confidence: {getattr(event, 'confidence', 'N/A')}")
                print(f"Message type: {getattr(event, 'message_type', 'N/A')}")
            on_turn(client, event)
            
        self.client.on(StreamingEvents.Turn, debug_on_turn)
        # ... other event handlers
        
    def test_connection(self):
        """Test API connection without streaming"""
        try:
            # Quick connection test
            test_client = StreamingClient(
                StreamingClientOptions(api_key=self.api_key)
            )
            test_client.connect(StreamingParameters(sample_rate=16_000))
            test_client.disconnect()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
```

## Key Implementation Notes

1. **Audio Format**: AssemblyAI requires PCM16, 16kHz, mono audio
2. **Event Handling**: Use FinalTranscript events for text insertion
3. **Error Recovery**: Implement reconnection logic for network issues
4. **Performance**: Buffer audio data for consistent streaming
5. **Commands**: Parse transcripts for control commands like "stop"
6. **Debugging**: Use debug mode during development and testing