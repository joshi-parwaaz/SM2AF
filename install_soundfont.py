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

# URLs for SoundFont files
SOUNDFONT_URLS = [
    "https://musical-artifacts.com/artifacts/1229/FluidR3_GM.sf2",
    "https://archive.org/download/FluidR3GM/FluidR3GM.sf2",
]

# Paths to check for existing SoundFonts
SOUNDFONT_PATHS = {
    "linux": [
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/local/share/sounds/sf2/FluidR3_GM.sf2",
    ],
    "darwin": [  # macOS
        "/usr/local/share/sounds/sf2/FluidR3_GM.sf2",
        "/opt/homebrew/share/sounds/sf2/FluidR3_GM.sf2",
    ],
    "win32": [
        r"C:\soundfonts\FluidR3_GM.sf2",
        os.path.join(os.path.expanduser("~"), "soundfonts", "FluidR3_GM.sf2"),
    ],
}

# Installation directories
INSTALL_PATHS = {
    "linux": "/usr/share/sounds/sf2/",
    "darwin": "/usr/local/share/sounds/sf2/",
    "win32": os.path.join(os.path.expanduser("~"), "soundfonts"),
}


def check_fluidsynth():
    """Check if FluidSynth is installed."""
    try:
        result = subprocess.run(
            ["fluidsynth", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            print(f"FluidSynth is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("FluidSynth is not installed.")
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
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                urllib.request.urlretrieve(url, tmp_file.name)
                # Check if the file size is reasonable (a valid SoundFont is typically several MB)
                if os.path.getsize(tmp_file.name) > 100000:  # Larger than 100KB
                    return tmp_file.name
                else:
                    print(f"Downloaded file is too small, might be invalid.")
                    os.unlink(tmp_file.name)
        except Exception as e:
            print(f"Error downloading from {url}: {e}")

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

    # Create a local soundfonts directory in the project if we don't have permissions
    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soundfonts")
    
    try:
        # Try to install to system directory first
        system_dir = INSTALL_PATHS[system]
        os.makedirs(system_dir, exist_ok=True)
        system_path = os.path.join(system_dir, "FluidR3_GM.sf2")
        shutil.copy(sf_file, system_path)
        print(f"SoundFont installed to: {system_path}")
        return True
    except (PermissionError, OSError) as e:
        print(f"Could not install to system directory: {e}")
        
        # Fall back to local directory
        try:
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, "FluidR3_GM.sf2")
            shutil.copy(sf_file, local_path)
            print(f"SoundFont installed to project directory: {local_path}")
            return True
        except Exception as e:
            print(f"Could not install to local directory: {e}")
            return False


def main():
    """Main function."""
    print("Checking for FluidSynth installation...")
    check_fluidsynth()

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
    
    # Clean up temp file
    os.unlink(downloaded_sf)
    
    if success:
        print("\nSoundFont installation complete!")
        return 0
    else:
        print("\nSoundFont installation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
