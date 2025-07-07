#!/usr/bin/env python3
"""
Simple SpeechHook usage example
"""

from src.speechhook import create_telephony_hook

def voice_agent_example():
    """Example of how to use SpeechHook in a voice agent"""
    
    # Create detector for telephony audio
    hook = create_telephony_hook()
    
    # Simulate voice agent state
    tts_is_playing = True
    
    print("🤖 AI: Starting to speak...")
    print("👂 Monitoring for user interruption...")
    
    # Simulate audio stream chunks
    audio_chunks = [
        bytes([10, 12, 8, 15] * 80),      # Background noise
        bytes([12, 15, 10, 18] * 80),     # Still quiet  
        bytes([45, 60, 55, 70] * 80),     # User starts speaking
        bytes([50, 65, 60, 75] * 80),     # Continued speech
        bytes([55, 70, 65, 80] * 80),     # More speech
        bytes([10, 12, 8, 15] * 80),      # Back to quiet
    ]
    
    for i, chunk in enumerate(audio_chunks):
        if tts_is_playing:
            onset_detected = hook.process_audio(chunk)
            
            if onset_detected:
                print(f"🎙️ Chunk {i}: USER INTERRUPTED!")
                print("🛑 Stopping TTS immediately...")
                print("👂 Switching to listening mode...")
                tts_is_playing = False
            else:
                print(f"🔇 Chunk {i}: No interruption, continuing TTS...")
        else:
            print(f"👂 Chunk {i}: Listening to user...")

if __name__ == "__main__":
    voice_agent_example()
