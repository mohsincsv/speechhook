# SpeechHook Usage Guide

## Vendor Integration Examples

### 🔹 Twilio Media Streams
```python
import websocket
import json
import base64
from speechhook import create_telephony_hook

hook = create_telephony_hook()

def on_message(ws, message):
    data = json.loads(message)
    
    if data.get('event') == 'media':
        audio_bytes = base64.b64decode(data['media']['payload'])
        
        if hook.process_audio(audio_bytes):
            print("🎙️ User interrupted - stopping TTS")
            ws.send(json.dumps({"event": "mark", "mark": {"name": "interrupt"}}))
```

### 🔹 AWS Connect
```python
import boto3
from speechhook import create_telephony_hook

hook = create_telephony_hook()

def process_connect_stream(audio_stream):
    for chunk in audio_stream:
        if hook.process_audio(chunk):
            # Stop current TTS playback
            stop_connect_tts()
            # Switch to listening mode
            start_connect_listening()
```

### 🔹 Vonage/Nexmo
```python
import nexmo
from speechhook import create_telephony_hook

hook = create_telephony_hook()

def handle_nexmo_audio(audio_data):
    if hook.process_audio(audio_data):
        # User barged in during TTS
        return {"action": "talk", "text": ""}  # Stop current speech
```

### 🔹 WebRTC (Browser)
```javascript
// JavaScript side
const mediaStream = await navigator.mediaDevices.getUserMedia({audio: true});
const recorder = new MediaRecorder(mediaStream);

recorder.ondataavailable = (event) => {
    // Send PCM data to Python backend via WebSocket
    websocket.send(event.data);
};
```

```python
# Python backend
from speechhook import create_hd_hook

hook = create_hd_hook(sample_rate=16000)

def handle_webrtc_audio(pcm_data):
    if hook.process_audio(pcm_data):
        return {"action": "interrupt_tts"}
```

### 🔹 Local Microphone (PyAudio)
```python
import pyaudio
from speechhook import create_hd_hook

# Setup microphone
p = pyaudio.PyAudio()
hook = create_hd_hook(sample_rate=16000)

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=320  # 20ms at 16kHz
)

try:
    while True:
        audio_data = stream.read(320)
        if hook.process_audio(audio_data):
            print("🎙️ Speech detected from microphone!")
finally:
    stream.close()
    p.terminate()
```

### 🔹 File Processing
```python
import wave
from speechhook import create_hd_hook

def process_audio_file(filename):
    hook = create_hd_hook()
    
    with wave.open(filename, 'rb') as wav:
        sample_rate = wav.getframerate()
        frame_size = int(sample_rate * 0.02)  # 20ms chunks
        
        while True:
            audio_data = wav.readframes(frame_size)
            if not audio_data:
                break
                
            if hook.process_audio(audio_data):
                timestamp = wav.tell() / sample_rate
                print(f"Speech onset at {timestamp:.2f}s")
```

## Audio Format Compatibility

### 🎵 Telephony (8kHz mu-law)
```python
from speechhook import create_telephony_hook

# Works with:
# - Twilio Media Streams
# - AWS Connect
# - Vonage/Nexmo
# - Traditional SIP providers
# - PBX systems

hook = create_telephony_hook()
```

### 🎵 High Definition (16kHz PCM16)
```python
from speechhook import create_hd_hook

# Works with:
# - WebRTC audio
# - Local microphones
# - VoIP applications
# - Video conferencing

hook = create_hd_hook(sample_rate=16000)
```

### 🎵 Broadcast Quality (22kHz+ PCM16)
```python
from speechhook import create_broadcast_hook

# Works with:
# - Podcast processing
# - Radio streams
# - Media file analysis
# - High-quality recordings

hook = create_broadcast_hook()  # 22.05kHz
```

### 🎵 Custom Configurations
```python
from speechhook import SpeechHook

# Ultra-low latency (10ms frames)
hook = SpeechHook(sample_rate=8000, encoding='mulaw')
hook.frame_size = int(8000 * 0.01)  # 10ms frames
hook.onset_frames = 2  # Faster detection

# High sensitivity for whispers
hook = SpeechHook(sample_rate=16000, encoding='pcm16')
hook.enter_threshold = 0.08  # Lower threshold
hook.onset_frames = 2  # Faster confirmation

# Noise-robust for noisy environments
hook = SpeechHook(sample_rate=8000, encoding='mulaw')
hook.enter_threshold = 0.25  # Higher threshold
hook.onset_frames = 5  # More confirmation frames
```

## Integration Patterns

### 🔄 Async Processing
```python
import asyncio
from speechhook import create_telephony_hook

async def voice_agent_loop():
    hook = create_telephony_hook()
    
    while True:
        # Concurrent audio processing
        audio_chunk = await get_audio_chunk()
        
        if hook.process_audio(audio_chunk):
            await handle_interruption()
        
        await asyncio.sleep(0.02)  # 20ms processing cycle
```

### 🔄 Event-Driven Architecture
```python
from speechhook import create_telephony_hook

class VoiceAgent:
    def __init__(self):
        self.hook = create_telephony_hook()
        self.callbacks = []
    
    def on_speech_onset(self, callback):
        self.callbacks.append(callback)
    
    def process_audio(self, chunk):
        if self.hook.process_audio(chunk):
            for callback in self.callbacks:
                callback()

# Usage
agent = VoiceAgent()
agent.on_speech_onset(lambda: print("🎙️ User speaking!"))
agent.on_speech_onset(stop_tts_playback)
agent.on_speech_onset(start_listening_mode)
```

### 🔄 State Machine Integration
```python
from enum import Enum
from speechhook import create_telephony_hook

class AgentState(Enum):
    LISTENING = "listening"
    THINKING = "thinking" 
    SPEAKING = "speaking"

class StatefulVoiceAgent:
    def __init__(self):
        self.hook = create_telephony_hook()
        self.state = AgentState.LISTENING
    
    def process_audio(self, chunk):
        if self.state == AgentState.SPEAKING:
            if self.hook.process_audio(chunk):
                self.transition_to(AgentState.LISTENING)
                return True
        return False
    
    def transition_to(self, new_state):
        print(f"State: {self.state.value} → {new_state.value}")
        self.state = new_state
```

## Performance Optimization

### ⚡ Batch Processing
```python
# Process multiple chunks efficiently
chunks = [chunk1, chunk2, chunk3, ...]
onsets = [hook.process_audio(chunk) for chunk in chunks]
```

### ⚡ Memory Management
```python
# Reset state periodically to prevent memory growth
if frame_count % 1000 == 0:
    hook.reset()
```

### ⚡ Threading
```python
import threading
import queue

audio_queue = queue.Queue()
hook = create_telephony_hook()

def audio_processor():
    while True:
        chunk = audio_queue.get()
        if hook.process_audio(chunk):
            handle_onset()

threading.Thread(target=audio_processor, daemon=True).start()
```

## Troubleshooting

### 🔧 No Speech Detected
```python
# Check if audio format matches
hook = create_telephony_hook()  # For mu-law
# or
hook = create_hd_hook()  # For PCM16

# Verify chunk size (should be 20ms worth)
chunk_size = int(sample_rate * 0.02 * bytes_per_sample)

# Check audio levels
import numpy as np
samples = np.frombuffer(chunk, dtype=np.int16)
print(f"Audio level: {np.max(np.abs(samples))}")
```

### 🔧 Too Many False Positives
```python
# Increase detection threshold
hook.enter_threshold = 0.25  # Higher threshold
hook.onset_frames = 4  # More confirmation needed
```

### 🔧 Too Slow Detection
```python
# Reduce detection latency
hook.onset_frames = 2  # Faster confirmation
hook.frame_size = int(sample_rate * 0.01)  # 10ms frames
```
