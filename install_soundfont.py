#!/usr/bin/env python3

"""
Helper script to automatically download and configure SoundFonts for better audio quality.
This script will download a SoundFont file and place it in the appropriate location
based on the operating system.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import urllib.request
import tempfile
from pydub import AudioSegment

# URLs for SoundFont files
SOUNDFONT_URLS = [
    "https://ftp.osuosl.org/pub/musescore/soundfont/FluidR3_GM/FluidR3_GM2-2.sf2",
    "http://www.schristiancollins.com/soundfonts/FluidR3_GM.sf2",
]

SOUNDFONT_PATHS = {
    "linux": [
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/local/share/sounds/sf2/FluidR3_GM.sf2",
    ],
    "darwin": [
        "/usr/local/share/sounds/sf2/FluidR3_GM.sf2",
        "/opt/homebrew/share/sounds/sf2/FluidR3_GM.sf2",
    ],
"win32": [
        r"C:\soundfonts\FluidR3_GM.sf2",
        os.path.join(os.getenv("APPDATA"), "soundfonts", "FluidR3_GM.sf2"),
        r"C:\Users\varun\Downloads\SM2AF\soundfonts\FluidR3_GM.sf2",
    ],
}

INSTALL_PATHS = {
    "linux": "/usr/share/sounds/sf2/",
    "darwin": "/usr/local/share/sounds/sf2/",
    "win32": os.path.join(os.path.expanduser("~"), "soundfonts"),
}

def check_fluidsynth():
    """Check if FluidSynth is installed."""
    try:
        # Use a simple command that doesn't try to load default soundfonts
        process = subprocess.Popen(
            ["fluidsynth", "-version"],  # Changed to -version instead of -ni -version
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        stdout, stderr = process.communicate(timeout=10)
        combined_output = stdout + stderr
        
        if "FluidSynth runtime version" in combined_output:
            version_line = next((line for line in combined_output.split('\n') 
                               if "FluidSynth runtime version" in line), "")
            print(f"FluidSynth is installed: {version_line.strip()}")
            return True
        else:
            print("FluidSynth found but version info not detected")
            print(f"Output: {combined_output}")
            return False
            
    except subprocess.TimeoutExpired:
        print("FluidSynth check timed out")
        if 'process' in locals():
            process.kill()
        return False
    except FileNotFoundError:
        print("FluidSynth not found in PATH")
        print("Ensure FluidSynth is installed and accessible.")
        print("Current PATH:", os.environ.get("PATH"))
        return False
    except Exception as e:
        print(f"FluidSynth check failed: {str(e)}")
        return False

def check_existing_soundfont():
    """Check if a SoundFont file already exists."""
    system = platform.system().lower()
    if system == "windows":
        system = "win32"
    elif system == "darwin" or "darwin" in system:
        system = "darwin"
    else:
        system = "linux"

    if system not in SOUNDFONT_PATHS:
        print(f"Unsupported system: {system}")
        return None

    for path in SOUNDFONT_PATHS[system]:
        if os.path.exists(path):
            print(f"SoundFont found at: {path}")
            return path

    print("No existing SoundFont found.")
    return None

def download_soundfont():
    """Download a SoundFont file."""
    for url in SOUNDFONT_URLS:
        print(f"Trying to download SoundFont from: {url}")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sf2") as tmp_file:
                urllib.request.urlretrieve(url, tmp_file.name)
                if os.path.getsize(tmp_file.name) > 100000:  # Larger than 100KB
                    print(f"Successfully downloaded SoundFont to {tmp_file.name}")
                    return tmp_file.name
                else:
                    print(f"Downloaded file from {url} is too small, might be invalid.")
                    os.unlink(tmp_file.name)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error downloading from {url}: {e.code} {e.reason}")
        except Exception as e:
            print(f"Error downloading from {url}: {str(e)}")

    print("All download attempts failed. Please download FluidR3_GM.sf2 manually from https://ftp.osuosl.org/pub/musescore/soundfont/FluidR3_GM/ or http://www.schristiancollins.com/generaluser.php and place it in one of the following paths:")
    for system, paths in SOUNDFONT_PATHS.items():
        for path in paths:
            print(f"  - {path}")
    return None

def install_soundfont(sf_file):
    """Install the SoundFont file to the appropriate location."""
    system = platform.system().lower()
    if system == "windows":
        system = "win32"
    elif system == "darwin" or "darwin" in system:
        system = "darwin"
    else:
        system = "linux"

    if system not in INSTALL_PATHS:
        print(f"Unsupported system: {system}")
        return False

    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soundfonts")
    
    try:
        system_dir = INSTALL_PATHS[system]
        os.makedirs(system_dir, exist_ok=True)
        system_path = os.path.join(system_dir, "FluidR3_GM.sf2")
        shutil.copy(sf_file, system_path)
        print(f"SoundFont installed to: {system_path}")
        return True
    except (PermissionError, OSError) as e:
        print(f"Could not install to system directory: {e}")
        try:
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, "FluidR3_GM.sf2")
            shutil.copy(sf_file, local_path)
            print(f"SoundFont installed to project directory: {local_path}")
            return True
        except Exception as e:
            print(f"Could not install to local directory: {e}")
            return False

def get_soundfont_path():
    """Dynamically locate the SoundFont file."""
    system = platform.system().lower()
    if system == "windows":
        system = "win32"
    elif system == "darwin":
        system = "darwin"
    else:
        system = "linux"

    if system not in SOUNDFONT_PATHS:
        raise ValueError(f"Unsupported system: {system}")

    for path in SOUNDFONT_PATHS[system]:
        print(f"Checking SoundFont at: {path}")
        if os.path.exists(path):
            path = path.replace('\\', '/')  # Convert backslashes to forward slashes
            print(f"Found SoundFont at: {path}")
            return path

    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soundfonts")
    local_path = os.path.join(local_dir, "FluidR3_GM.sf2")
    print(f"Checking local project SoundFont at: {local_path}")
    if os.path.exists(local_path):
        local_path = local_path.replace('\\', '/')  # Convert backslashes to forward slashes
        print(f"Found SoundFont at: {local_path}")
        return local_path

    raise FileNotFoundError("SoundFont not found. Please run the installation script or place FluidR3_GM.sf2 manually.")


def midi_to_mp3(midi_path, mp3_path):
    """Convert MIDI to MP3 using only FluidSynth subprocess and pydub."""
    try:
        soundfont_path = get_soundfont_path()
        print(f"Using SoundFont at: {soundfont_path}")
        
        # Create WAV file path
        wav_path = midi_path.replace('.mid', '.wav')
        
        # Use direct FluidSynth subprocess call - skip midi2audio entirely
        print("Converting MIDI to WAV using direct FluidSynth command...")
        
        fluidsynth_cmd = [
            "fluidsynth",
            "-ni",  # No interactive mode
            "-g", "0.5",  # Gain
            "-F", wav_path,  # Output WAV file
            soundfont_path,  # SoundFont file
            midi_path  # Input MIDI file
        ]
        
        print(f"Running FluidSynth command: {' '.join(fluidsynth_cmd)}")
        
        # Use Popen to better control the process
        process = subprocess.Popen(
            fluidsynth_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Send quit command and wait for completion
        try:
            stdout, stderr = process.communicate(input="quit\n", timeout=60)
        except subprocess.TimeoutExpired:
            print("FluidSynth process timed out, terminating...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            raise Exception("FluidSynth conversion timed out")
        
        # Check result
        if process.returncode not in [0, -15]:  # 0 = success, -15 = SIGTERM (normal when we send quit)
            print(f"FluidSynth stderr: {stderr}")
            print(f"FluidSynth stdout: {stdout}")
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
                raise Exception(f"FluidSynth failed with return code {process.returncode}")
        
        # Check if WAV file was created and has content
        if not os.path.exists(wav_path):
            raise Exception(f"WAV file was not created: {wav_path}")
            
        if os.path.getsize(wav_path) == 0:
            raise Exception(f"WAV file is empty: {wav_path}")
            
        print(f"WAV file created successfully: {wav_path} ({os.path.getsize(wav_path)} bytes)")
        
        # Convert WAV to MP3 using pydub
        print(f"Converting WAV to MP3: {wav_path} -> {mp3_path}")
        try:
            sound = AudioSegment.from_wav(wav_path)
            sound.export(mp3_path, format="mp3")
            print(f"Successfully converted WAV to MP3: {mp3_path}")
        except Exception as e:
            raise Exception(f"WAV to MP3 conversion failed: {str(e)}")
        
        # Clean up WAV file
        try:
            if os.path.exists(wav_path):
                os.remove(wav_path)
                print(f"Cleaned up temporary WAV file: {wav_path}")
        except Exception as e:
            print(f"Warning: Could not remove temporary WAV file {wav_path}: {e}")
        
        # Verify MP3 file was created
        if not os.path.exists(mp3_path):
            raise Exception(f"MP3 file was not created: {mp3_path}")
            
        if os.path.getsize(mp3_path) == 0:
            raise Exception(f"MP3 file is empty: {mp3_path}")
            
        print(f"MP3 conversion completed successfully: {mp3_path} ({os.path.getsize(mp3_path)} bytes)")
        
    except Exception as e:
        # Clean up any temporary files on error
        wav_path = midi_path.replace('.mid', '.wav')
        for temp_file in [wav_path]:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        raise Exception(f"MIDI to MP3 conversion failed: {str(e)}")


def test_midi_conversion():
    """Test function to verify MIDI to MP3 conversion works."""
    # This is a simple test function you can call to verify the conversion works
    import tempfile
    
    # Create a simple test MIDI file (you'd need to have a real MIDI file for testing)
    test_midi = "test.mid"  # Replace with path to a real MIDI file
    test_mp3 = "test_output.mp3"
    
    if os.path.exists(test_midi):
        try:
            midi_to_mp3(test_midi, test_mp3)
            print("Test conversion successful!")
            if os.path.exists(test_mp3):
                print(f"MP3 file created: {test_mp3}")
                # Clean up test file
                os.remove(test_mp3)
        except Exception as e:
            print(f"Test conversion failed: {e}")
    else:
        print(f"Test MIDI file not found: {test_midi}")


def main():
    """Main function."""
    print("Checking for FluidSynth installation...")
    if not check_fluidsynth():
        sys.exit(1)

    print("\nChecking for existing SoundFont...")
    existing_sf = check_existing_soundfont()
    
    if existing_sf:
        print("SoundFont already installed.")
        return 0
    
    print("\nDownloading SoundFont...")
    downloaded_sf = download_soundfont()
    
    if not downloaded_sf:
        print("Failed to download SoundFont.")
        return 1
    
    print("\nInstalling SoundFont...")
    success = install_soundfont(downloaded_sf)
    
    os.unlink(downloaded_sf)
    
    if success:
        print("\nSoundFont installation complete!")
        return 0
    else:
        print("\nSoundFont installation failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())