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
from midi2audio import FluidSynth

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
        os.path.join(os.path.expanduser("~"), "soundfonts", "FluidR3_GM.sf2"),
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
        # Use -ni (no-interactive) and -version, but send quit command to exit gracefully
        process = subprocess.Popen(
            ["fluidsynth", "-ni", "-version"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Send quit command and close stdin to make fluidsynth exit
        stdout, stderr = process.communicate(input="quit\n", timeout=10)
        
        if "FluidSynth runtime version" in stdout or "FluidSynth runtime version" in stderr:
            version_line = next((line for line in (stdout + stderr).split('\n') 
                               if "FluidSynth runtime version" in line), "")
            print(f"FluidSynth is installed: {version_line.strip()}")
            return True
        else:
            print("FluidSynth found but version info not detected")
            return False
            
    except subprocess.TimeoutExpired:
        print("FluidSynth check timed out")
        if 'process' in locals():
            process.kill()
        return False
    except FileNotFoundError:
        print("FluidSynth not found in PATH")
        print("Ensure FluidSynth is installed at C:\\ProgramData\\chocolatey\\bin\\fluidsynth.exe.")
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

    # Debug: print all checked paths
    for path in SOUNDFONT_PATHS[system]:
        print(f"Checking SoundFont at: {path}")
        if os.path.exists(path):
            print(f"Found SoundFont at: {path}")
            return path

    # Also check local project folder (relative to script)
    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soundfonts")
    local_path = os.path.join(local_dir, "FluidR3_GM.sf2")
    print(f"Checking local project SoundFont at: {local_path}")
    if os.path.exists(local_path):
        print(f"Found SoundFont at: {local_path}")
        return local_path

    raise FileNotFoundError("SoundFont not found. Please run the installation script or place FluidR3_GM.sf2 manually.")



def midi_to_mp3(midi_path, mp3_path):
    """Convert MIDI to MP3 using midi2audio and pydub."""
    soundfont_path = get_soundfont_path()
    wav_path = midi_path.replace('.mid', '.wav')
    fs = FluidSynth(soundfont_path)
    fs.midi_to_audio(midi_path, wav_path)
    sound = AudioSegment.from_wav(wav_path)
    sound.export(mp3_path, format="mp3")
    os.remove(wav_path)

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