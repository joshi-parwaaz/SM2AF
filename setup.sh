#!/bin/bash

# Setup script for installing FluidSynth and SoundFont files for better audio quality

# Detect OS
OS="$(uname)"
echo "Detected OS: $OS"

# Function to download and install SoundFont
download_soundfont() {
  mkdir -p soundfonts
  echo "Downloading SoundFont file..."
  
  # Try curl first
  if command -v curl &> /dev/null; then
    curl -L "https://archive.org/download/FluidR3GM/FluidR3GM.sf2" -o soundfonts/FluidR3_GM.sf2
  # Fall back to wget
  elif command -v wget &> /dev/null; then
    wget -O soundfonts/FluidR3_GM.sf2 "https://archive.org/download/FluidR3GM/FluidR3GM.sf2"
  else
    echo "Error: Neither curl nor wget are installed. Cannot download SoundFont."
    return 1
  fi
  
  # Check if download was successful
  if [ -f soundfonts/FluidR3_GM.sf2 ] && [ -s soundfonts/FluidR3_GM.sf2 ]; then
    echo "SoundFont successfully downloaded to soundfonts/FluidR3_GM.sf2"
    return 0
  else
    echo "SoundFont download failed or file is empty."
    return 1
  fi
}

# Install FluidSynth and SoundFont based on the OS
case $OS in
  Darwin) # macOS
    echo "Installing FluidSynth for macOS using Homebrew..."
    if ! command -v brew &> /dev/null; then
      echo "Homebrew not found. Please install Homebrew first: https://brew.sh/"
      exit 1
    fi
    
    brew install fluid-synth
    
    # Create directory for SoundFont
    mkdir -p /usr/local/share/sounds/sf2/
    
    # Download SoundFont if not exists
    if [ ! -f /usr/local/share/sounds/sf2/FluidR3_GM.sf2 ]; then
      download_soundfont
      # Copy to system location if download was successful
      if [ $? -eq 0 ]; then
        cp soundfonts/FluidR3_GM.sf2 /usr/local/share/sounds/sf2/
      fi
    else
      echo "SoundFont already exists at /usr/local/share/sounds/sf2/FluidR3_GM.sf2"
    fi
    ;;
    
  Linux)
    echo "Installing FluidSynth for Linux..."
    # Detect package manager
    if command -v apt &> /dev/null; then
      sudo apt update
      sudo apt install -y fluidsynth
    elif command -v dnf &> /dev/null; then
      sudo dnf install -y fluidsynth
    elif command -v pacman &> /dev/null; then
      sudo pacman -S fluidsynth
    else
      echo "Unsupported Linux distribution. Please install FluidSynth manually."
    fi
    
    # Create directory for SoundFont
    sudo mkdir -p /usr/share/sounds/sf2/
    
    # Download SoundFont if not exists
    if [ ! -f /usr/share/sounds/sf2/FluidR3_GM.sf2 ]; then
      download_soundfont
      # Copy to system location if download was successful
      if [ $? -eq 0 ]; then
        sudo cp soundfonts/FluidR3_GM.sf2 /usr/share/sounds/sf2/
      fi
    else
      echo "SoundFont already exists at /usr/share/sounds/sf2/FluidR3_GM.sf2"
    fi
    ;;
    
  MINGW*|MSYS*|CYGWIN*) # Windows
    echo "On Windows, please install FluidSynth manually:"
    echo "1. Download from https://github.com/FluidSynth/fluidsynth/releases"
    echo "2. Download a SoundFont file from https://archive.org/download/FluidR3GM/FluidR3GM.sf2"
    echo "3. Place the SoundFont file in a folder named 'soundfonts' in the application directory"
    
    # Still try to download the SoundFont
    download_soundfont
    ;;
    
  *)
    echo "Unsupported operating system: $OS"
    echo "Please install FluidSynth manually and download a SoundFont file."
    
    # Still try to download the SoundFont
    download_soundfont
    ;;
esac

# Python dependencies
echo "Installing required Python packages..."
pip install -r requirements.txt

echo "Setup complete!"
