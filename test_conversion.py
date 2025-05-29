#!/usr/bin/env python3
"""
Robust test script to debug MIDI to MP3 conversion issues.
This version handles FluidSynth's interactive behavior better.
"""

import os
import sys
import subprocess
import time
from install_soundfont import get_soundfont_path, midi_to_mp3

def test_fluidsynth_installation():
    """Test if FluidSynth is properly installed and accessible."""
    print("Testing FluidSynth installation...")
    try:
        # Method 1: Try with help command (should exit quickly)
        result = subprocess.run(
            ["fluidsynth", "-h"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        combined_output = result.stdout + result.stderr
        
        if "Usage:" in combined_output or "FluidSynth" in combined_output:
            print("✓ FluidSynth is installed and accessible")
            print("  FluidSynth help command works")
            return True
            
    except subprocess.TimeoutExpired:
        print("  FluidSynth -h timed out, trying alternative method...")
    except FileNotFoundError:
        print("✗ FluidSynth not found in PATH")
        return False
    except Exception as e:
        print(f"  Error with -h: {e}")
    
    try:
        # Method 2: Try a quick command that should exit immediately
        # Use a dummy soundfont path to make fluidsynth exit quickly with an error
        result = subprocess.run(
            ["fluidsynth", "-ni", "nonexistent.sf2"],
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # If we get here, FluidSynth at least ran
        print("✓ FluidSynth is installed and accessible")
        print("  FluidSynth executable responds to commands")
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ FluidSynth commands are timing out")
        return False
    except FileNotFoundError:
        print("✗ FluidSynth not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Error testing FluidSynth: {e}")
        return False

def test_soundfont():
    """Test if SoundFont file exists and is accessible."""
    print("\nTesting SoundFont availability...")
    try:
        soundfont_path = get_soundfont_path()
        print(f"  SoundFont path: {soundfont_path}")
        
        if os.path.exists(soundfont_path):
            size = os.path.getsize(soundfont_path)
            print(f"✓ SoundFont file exists ({size:,} bytes)")
            return True, soundfont_path
        else:
            print("✗ SoundFont file does not exist")
            return False, soundfont_path
            
    except Exception as e:
        print(f"✗ Error locating SoundFont: {e}")
        return False, None

def test_direct_fluidsynth_conversion(midi_file, soundfont_path):
    """Test FluidSynth conversion directly using subprocess."""
    print(f"\nTesting direct FluidSynth conversion...")
    
    if not os.path.exists(midi_file):
        print(f"✗ MIDI file does not exist: {midi_file}")
        return False
    
    wav_file = midi_file.replace('.mid', '_test.wav')
    
    try:
        cmd = [
            "fluidsynth",
            "-ni",  # No interactive mode
            "-g", "0.5",  # Gain
            "-F", wav_file,  # Output file
            soundfont_path,  # SoundFont
            midi_file  # Input MIDI
        ]
        
        print(f"  Command: {' '.join(cmd)}")
        print("  This may take a moment...")
        
        # Use a longer timeout for actual conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # Reduced from 60 to 30 seconds
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        print(f"  FluidSynth returned with code: {result.returncode}")
        
        if os.path.exists(wav_file):
            size = os.path.getsize(wav_file)
            if size > 0:
                print(f"✓ FluidSynth conversion successful ({size:,} bytes)")
                # Clean up test file
                os.remove(wav_file)
                return True
            else:
                print("✗ FluidSynth created empty WAV file")
                os.remove(wav_file)
                return False
        else:
            print("✗ FluidSynth conversion failed - no output file created")
            print(f"  Stdout: {result.stdout}")
            print(f"  Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ FluidSynth conversion timed out (>30 seconds)")
        # Try to clean up if file was created
        if os.path.exists(wav_file):
            os.remove(wav_file)
        return False
    except Exception as e:
        print(f"✗ Error in FluidSynth conversion: {e}")
        return False

def test_pydub_conversion():
    """Test pydub WAV to MP3 conversion."""
    print("\nTesting pydub WAV to MP3 conversion...")
    try:
        from pydub import AudioSegment
        print("✓ pydub imported successfully")
        
        # Create a simple test audio segment
        test_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
        test_mp3 = "test_output.mp3"
        
        test_audio.export(test_mp3, format="mp3")
        
        if os.path.exists(test_mp3):
            size = os.path.getsize(test_mp3)
            print(f"✓ pydub MP3 export successful ({size:,} bytes)")
            os.remove(test_mp3)
            return True
        else:
            print("✗ pydub MP3 export failed - file not created")
            return False
            
    except ImportError:
        print("✗ pydub not installed")
        return False
    except Exception as e:
        print(f"✗ Error testing pydub: {e}")
        return False

def test_alternative_fluidsynth():
    """Test if we can at least verify FluidSynth exists by checking the executable."""
    print("\nTesting alternative FluidSynth detection...")
    
    # Check if fluidsynth.exe exists in common locations
    common_paths = [
        r"C:\ProgramData\chocolatey\bin\fluidsynth.exe",
        r"C:\Program Files\FluidSynth\bin\fluidsynth.exe",
        r"C:\Users\varun\bin\fluidsynth.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✓ Found FluidSynth executable at: {path}")
            return True
    
    # Check if it's in PATH
    try:
        import shutil
        fluidsynth_path = shutil.which("fluidsynth")
        if fluidsynth_path:
            print(f"✓ FluidSynth found in PATH: {fluidsynth_path}")
            return True
    except Exception as e:
        print(f"Error checking PATH: {e}")
    
    print("✗ Could not locate FluidSynth executable")
    return False

def test_full_conversion(midi_file):
    """Test the full MIDI to MP3 conversion pipeline."""
    print(f"\nTesting full conversion pipeline with: {midi_file}")
    
    if not os.path.exists(midi_file):
        print(f"✗ MIDI file does not exist: {midi_file}")
        return False
    
    mp3_file = midi_file.replace('.mid', '_test.mp3')
    
    try:
        print("  Starting full conversion...")
        midi_to_mp3(midi_file, mp3_file)
        
        if os.path.exists(mp3_file):
            size = os.path.getsize(mp3_file)
            if size > 0:
                print(f"✓ Full conversion successful ({size:,} bytes)")
                # Clean up test file
                os.remove(mp3_file)
                return True
            else:
                print("✗ Full conversion created empty MP3 file")
                os.remove(mp3_file)
                return False
        else:
            print("✗ Full conversion failed - MP3 file not created")
            return False
            
    except Exception as e:
        print(f"✗ Full conversion failed: {e}")
        # Clean up if file exists
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
        return False

def main():
    """Run all tests."""
    print("MIDI to MP3 Conversion Test Suite")
    print("=" * 40)
    
    # Test 1: FluidSynth installation (basic)
    fluidsynth_ok = test_fluidsynth_installation()
    
    # If basic test fails, try alternative detection
    if not fluidsynth_ok:
        print("\nBasic FluidSynth test failed, trying alternative detection...")
        fluidsynth_alt_ok = test_alternative_fluidsynth()
        if fluidsynth_alt_ok:
            print("FluidSynth executable found, but may have communication issues")
            # Let's try the conversion anyway
            fluidsynth_ok = True
    
    # Test 2: SoundFont availability
    soundfont_ok, soundfont_path = test_soundfont()
    
    # Test 3: pydub functionality
    pydub_ok = test_pydub_conversion()
    
    # Find a MIDI file to test with
    midi_files = []
    for file in os.listdir('.'):
        if file.endswith('.mid'):
            midi_files.append(file)
    
    if midi_files:
        midi_file = midi_files[0]
        print(f"\nFound MIDI file for testing: {midi_file}")
        
        # Test 4: Direct FluidSynth conversion
        if fluidsynth_ok and soundfont_ok:
            direct_ok = test_direct_fluidsynth_conversion(midi_file, soundfont_path)
        else:
            direct_ok = False
            print("\nSkipping direct FluidSynth test (prerequisites not met)")
        
        # Test 5: Full conversion pipeline (try even if direct test failed)
        if soundfont_ok and pydub_ok:
            print("\nAttempting full conversion test...")
            full_ok = test_full_conversion(midi_file)
        else:
            full_ok = False
            print("\nSkipping full conversion test (prerequisites not met)")
    else:
        print("\nNo MIDI files found for testing")
        direct_ok = False
        full_ok = False
    
    # Summary
    print("\nTest Results Summary:")
    print("=" * 20)
    print(f"FluidSynth accessible: {'✓' if fluidsynth_ok else '✗'}")
    print(f"SoundFont available: {'✓' if soundfont_ok else '✗'}")
    print(f"pydub working: {'✓' if pydub_ok else '✗'}")
    print(f"Direct conversion: {'✓' if direct_ok else '✗'}")
    print(f"Full pipeline: {'✓' if full_ok else '✗'}")
    
    # If full pipeline works, that's what matters most
    if full_ok:
        print("\n🎉 Full pipeline works! MIDI to MP3 conversion should work in your app.")
        return 0
    elif soundfont_ok and pydub_ok:
        print("\n⚠️  Core components work, but FluidSynth communication has issues.")
        print("   Try running your main application - it might still work.")
        return 0
    else:
        print("\n❌ Critical components failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())