#!/usr/bin/env python3
"""
Setup script for SpeechHook Voice Agent Demo
Helps install system dependencies for audio processing
"""

import subprocess
import sys
import platform
import os


def run_command(command, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def install_system_dependencies():
    """Install system-level audio dependencies"""
    system = platform.system().lower()
    
    print(f"🔧 Detected system: {system}")
    
    if system == "darwin":  # macOS
        print("🍎 Setting up macOS audio dependencies...")
        
        # Check if Homebrew is installed
        if run_command("which brew", check=False):
            print("✅ Homebrew found")
            # Install PortAudio (required for PyAudio)
            if run_command("brew install portaudio"):
                print("✅ PortAudio installed")
            else:
                print("⚠️  PortAudio installation failed - PyAudio might not work")
        else:
            print("⚠️  Homebrew not found. Please install from https://brew.sh/")
            print("   Then run: brew install portaudio")
            
    elif system == "linux":
        print("🐧 Setting up Linux audio dependencies...")
        
        # Try to detect package manager
        if run_command("which apt-get", check=False):
            print("📦 Using apt package manager")
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y portaudio19-dev python3-pyaudio",
                "sudo apt-get install -y alsa-utils pulseaudio"
            ]
        elif run_command("which yum", check=False):
            print("📦 Using yum package manager")
            commands = [
                "sudo yum install -y portaudio-devel",
                "sudo yum install -y alsa-lib-devel pulseaudio"
            ]
        elif run_command("which pacman", check=False):
            print("📦 Using pacman package manager")
            commands = [
                "sudo pacman -S portaudio",
                "sudo pacman -S alsa-utils pulseaudio"
            ]
        else:
            print("⚠️  Unknown package manager. Please manually install:")
            print("   - portaudio development libraries")
            print("   - ALSA utilities")
            print("   - PulseAudio")
            return
        
        for cmd in commands:
            print(f"🔄 Running: {cmd}")
            if not run_command(cmd):
                print(f"⚠️  Command failed: {cmd}")
                
    elif system == "windows":
        print("🪟 Windows detected")
        print("✅ PyAudio should work out of the box on Windows")
        print("💡 If you encounter issues, install Visual C++ Build Tools")
        
    else:
        print(f"❓ Unsupported system: {system}")


def install_python_dependencies():
    """Install Python dependencies"""
    print("🐍 Installing Python dependencies...")
    
    # Upgrade pip first
    if run_command(f"{sys.executable} -m pip install --upgrade pip"):
        print("✅ pip upgraded")
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        if run_command(f"{sys.executable} -m pip install -r requirements.txt"):
            print("✅ Requirements installed")
        else:
            print("❌ Failed to install requirements")
            return False
    else:
        print("⚠️  requirements.txt not found")
        
    return True


def test_audio_setup():
    """Test if audio setup is working"""
    print("🧪 Testing audio setup...")
    
    try:
        import pyaudio
        print("✅ PyAudio imported successfully")
        
        # Test PyAudio initialization
        p = pyaudio.PyAudio()
        
        # List audio devices
        print("🎤 Available audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  📺 Input: {info['name']}")
            if info['maxOutputChannels'] > 0:
                print(f"  🔊 Output: {info['name']}")
        
        p.terminate()
        
    except ImportError:
        print("❌ PyAudio not available")
        return False
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return False
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition imported successfully")
    except ImportError:
        print("❌ SpeechRecognition not available")
        return False
    
    try:
        import pyttsx3
        print("✅ pyttsx3 imported successfully")
        
        # Test TTS initialization
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"🗣️  Available TTS voices: {len(voices) if voices else 0}")
        
    except ImportError:
        print("❌ pyttsx3 not available")
        return False
    except Exception as e:
        print(f"⚠️  TTS test warning: {e}")
    
    print("✅ All audio components working!")
    return True


def main():
    """Main setup function"""
    print("🎙️ SpeechHook Voice Agent Demo Setup")
    print("=" * 50)
    
    print("This script will help you set up the voice agent demo dependencies.")
    print("You may be prompted for your password for system-level installations.\n")
    
    # Install system dependencies
    install_system_dependencies()
    print()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed during Python dependency installation")
        return 1
    print()
    
    # Test setup
    if test_audio_setup():
        print("\n🎉 Setup complete! You can now run:")
        print("   python voice_agent_demo.py")
    else:
        print("\n❌ Setup incomplete. Please check error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
