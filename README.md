# SpeechHook

Lean speech onset detection for voice agents. One class, one job: detect when users start speaking during TTS playback.

## Why SpeechHook?

Voice agents need to stop talking when users interrupt - just like humans do. SpeechHook detects speech onset in ~60ms so your AI can immediately stop TTS and start listening.

**Works with any audio source** - no vendor lock-in.

## Usage

```python
from speechhook import create_telephony_hook

# Create detector for telephony audio (8kHz mu-law)
hook = create_telephony_hook()

# Process audio chunks from any source
while True:
    audio_chunk = websocket.recv()  # Get audio data
    if hook.process_audio(audio_chunk):
        print("🎙️ User started speaking - stop TTS!")
        stop_tts_immediately()
        start_listening()
```

## Multi-Vendor Integration

```python
# Twilio WebSocket
from speechhook import create_telephony_hook
hook = create_telephony_hook()
# Process Twilio base64 audio: hook.process_audio(base64.b64decode(payload))

# AWS Connect
from speechhook import create_telephony_hook  
hook = create_telephony_hook()
# Process AWS audio stream: hook.process_audio(audio_chunk)

# Vonage/Nexmo
from speechhook import create_telephony_hook
hook = create_telephony_hook()
# Process Vonage audio: hook.process_audio(audio_data)

# WebRTC (browser)
from speechhook import create_hd_hook
hook = create_hd_hook(sample_rate=16000)
# Process WebRTC audio: hook.process_audio(pcm_data)

# Local microphone
from speechhook import create_hd_hook
hook = create_hd_hook(sample_rate=44100)
# Process mic audio: hook.process_audio(microphone_chunk)
```

## Features

- **Lean**: Single class, ~200 lines of code
- **Fast**: ~2ms processing time per 20ms audio chunk  
- **Adaptive**: Automatically adjusts to background noise
- **Vendor Agnostic**: Works with any audio source (Twilio, AWS, Vonage, WebRTC, etc.)
- **Multiple Formats**: Supports mu-law (telephony) and PCM16 (HD audio)
- **No Dependencies**: Just NumPy and SciPy

## How It Works

1. **Audio Preprocessing**: Pre-emphasis filter + windowing
2. **Feature Extraction**: Speech-band energy, spectral flux, zero-crossing rate
3. **Adaptive Thresholding**: Rolling median noise floor estimation
4. **State Machine**: Hysteresis logic prevents false positives

## API

### `SpeechHook(sample_rate=8000, encoding='mulaw')`

Main detection class.

**Methods:**
- `process_audio(audio_buffer: bytes) -> bool` - Returns True on speech onset
- `reset()` - Reset internal state

**Properties:**
- `is_speaking: bool` - Current speech state
- `consecutive_speech: int` - Frames of continuous speech

### Convenience Functions

- `create_telephony_hook()` - 8kHz mu-law for any telephony provider
- `create_hd_hook(sample_rate=16000)` - PCM16 for high-quality audio
- `create_broadcast_hook()` - 22kHz PCM16 for broadcast quality

## Demo

### Basic Demo
```bash
python demo.py
```
Runs basic demo, multi-vendor integration examples, streaming simulation, and performance test.

### Real Voice Agent Demo
```bash
# Install dependencies first
python setup_demo.py

# Run the voice agent
python voice_agent_demo.py
```

**Complete voice-to-voice pipeline:**
1. 🎤 **Listen**: Real-time microphone input
2. 📝 **Transcribe**: Speech-to-text (Google Speech API)
3. 🤖 **Think**: LLM processing (OpenAI GPT or simple responses)
4. 🗣️ **Speak**: Text-to-speech output
5. ⚡ **Interrupt**: SpeechHook detects user interruptions during TTS

**Features:**
- Real-time conversation with natural interruptions
- Works with or without OpenAI API key
- Cross-platform audio support (macOS, Linux, Windows)
- Automatic ambient noise adjustment

## Performance

- **Latency**: 40-60ms detection delay
- **CPU**: ~2ms processing per 20ms audio chunk
- **Memory**: <1MB per detector instance

## Real-World Impact

### Traditional Flow (Without SpeechHook)
```
User: "What's the weather?"
AI: "The weather today is sunny with a high of 75 degrees and..." [keeps talking]
User: "Wait, what about tomorrow?" [has to wait for AI to finish]
AI: "...partly cloudy tonight. What would you like to know?"
User: "What about tomorrow?" [finally gets to speak]
```

### With SpeechHook (Natural Interruption)
```
User: "What's the weather?"
AI: "The weather today is sunny with a high of 75 degrees and..." 
User: "Wait, what about tomorrow?" [SpeechHook detects speech onset]
AI: [STOPS immediately - <60ms latency]
AI: "What about tomorrow? Tomorrow will be..."
```

This natural conversation flow is what makes voice agents feel human-like rather than robotic.

## License

MIT
