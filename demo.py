#!/usr/bin/env python3
"""
SpeechHook Demo - Simple examples and testing
"""

import base64
import json
from src.speechhook import create_telephony_hook, create_hd_hook, SpeechHook


def basic_demo():
    """Basic usage demo"""
    print("🎙️ SpeechHook Basic Demo")
    print("-" * 30)
    
    # Create detector for telephony streams
    hook = create_telephony_hook()
    
    # Simulate mu-law audio data (normally from WebSocket)
    test_audio = bytes([0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38] * 50)
    
    print(f"Processing {len(test_audio)} bytes of mu-law audio...")
    
    # Process audio - returns True on speech onset
    onset_detected = hook.process_audio(test_audio)
    
    print(f"Speech onset detected: {onset_detected}")
    
    # Process a few more chunks to see state changes
    for i in range(5):
        varied_audio = bytes([(i * 20 + j) % 256 for j in range(320)])  # 40ms worth
        onset = hook.process_audio(varied_audio)
        print(f"Chunk {i+1}: onset={onset}, speaking={hook.is_speaking}")


def vendor_integration_demo():
    """Show how to integrate with various vendors"""
    print("\n🌐 Multi-Vendor Integration Demo")
    print("-" * 30)
    
    # Works with any telephony provider
    hook = create_telephony_hook()
    
    # Simulate Twilio WebSocket message
    twilio_msg = {
        "event": "media",
        "streamSid": "MZ123456789",
        "media": {
            "track": "inbound",
            "chunk": "1", 
            "timestamp": "12345",
            "payload": base64.b64encode(bytes([0x7F, 0x80, 0x81] * 100)).decode()
        }
    }
    
    print("📞 Twilio integration:")
    if twilio_msg["event"] == "media":
        audio_data = base64.b64decode(twilio_msg["media"]["payload"])
        onset_detected = hook.process_audio(audio_data)
        print(f"  Processed chunk {twilio_msg['media']['chunk']}, onset: {onset_detected}")
    
    print("📞 AWS Connect integration:")
    # AWS Connect uses similar format
    aws_audio = bytes([0x80, 0x85, 0x90] * 100)
    onset = hook.process_audio(aws_audio)
    print(f"  Processed AWS audio chunk, onset: {onset}")
    
    print("📞 Vonage integration:")
    # Vonage also uses mu-law telephony
    vonage_audio = bytes([0x7F, 0x82, 0x88] * 100)
    onset = hook.process_audio(vonage_audio)
    print(f"  Processed Vonage audio chunk, onset: {onset}")
    
    print("🌐 WebRTC (browser) integration:")
    # Higher quality browser audio
    webrtc_hook = create_hd_hook(sample_rate=16000)
    webrtc_audio = bytes([0x10, 0x20] * 320)  # 16-bit samples
    onset = webrtc_hook.process_audio(webrtc_audio)
    print(f"  Processed WebRTC audio chunk, onset: {onset}")


def streaming_demo():
    """Simulate streaming audio processing"""
    print("\n🔄 Streaming Demo")
    print("-" * 30)
    
    hook = create_telephony_hook()
    
    # Simulate continuous audio stream
    for chunk_id in range(10):
        # Generate varying audio to potentially trigger onset
        if chunk_id < 3:
            # Quiet audio (background noise)
            audio = bytes([10, 12, 8, 15] * 80)
        elif chunk_id < 6:
            # Louder audio (potential speech)
            audio = bytes([50, 60, 45, 70, 55, 65] * 53)
        else:
            # Back to quiet
            audio = bytes([8, 10, 12, 9] * 80)
        
        onset = hook.process_audio(audio)
        
        status = "🎙️ ONSET!" if onset else "🔇 silent"
        speaking = "speaking" if hook.is_speaking else "silence"
        
        print(f"Chunk {chunk_id:2d}: {status} | State: {speaking}")


def performance_test():
    """Simple performance test"""
    print("\n⚡ Performance Test")
    print("-" * 30)
    
    import time
    
    hook = create_telephony_hook()
    test_audio = bytes([0x7F] * 320)  # 40ms of audio
    
    # Warm up
    for _ in range(10):
        hook.process_audio(test_audio)
    
    # Time processing
    start_time = time.time()
    iterations = 1000
    
    for _ in range(iterations):
        hook.process_audio(test_audio)
    
    end_time = time.time()
    avg_time_ms = (end_time - start_time) * 1000 / iterations
    
    print(f"Processed {iterations} chunks")
    print(f"Average processing time: {avg_time_ms:.2f} ms per 40ms chunk")
    print(f"Real-time factor: {40/avg_time_ms:.1f}x")


def interactive_test():
    """Interactive testing mode"""
    print("\n🖥️  Interactive Mode")
    print("-" * 30)
    print("Commands: test, reset, status, quit")
    
    hook = create_telephony_hook()
    
    while True:
        try:
            cmd = input("\nspeechhook> ").strip().lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'test':
                # Generate random test audio
                import random
                audio = bytes([random.randint(30, 100) for _ in range(320)])
                onset = hook.process_audio(audio)
                print(f"Result: onset={onset}, speaking={hook.is_speaking}")
            elif cmd == 'reset':
                hook.reset()
                print("Detector reset")
            elif cmd == 'status':
                print(f"Speaking: {hook.is_speaking}")
                print(f"Consecutive speech frames: {hook.consecutive_speech}")
                print(f"Noise history size: {len(hook.noise_history)}")
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    print("SpeechHook - Lean Speech Onset Detection")
    print("=" * 50)
    
    basic_demo()
    vendor_integration_demo() 
    streaming_demo()
    performance_test()
    
    # Uncomment for interactive mode
    # interactive_test()
    
    print("\n" + "=" * 50)
    print("Demo complete! 🎉")
