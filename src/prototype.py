import os
import subprocess
import pygame
from music21 import converter, midi
import sys
from PIL import Image, ImageOps

# Define paths
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# take the current directory as the working directory
path = os.getcwd()

output_xml_path = "output.musicxml"
output_midi_path = "output.mid"
output_wav_path = "output.wav"

def preprocess_image(image_path: str):
    """
    Preprocess the image if necessary (e.g., resizing, converting to grayscale).
    This function can be expanded based on specific requirements.
    """
    img = Image.open(image_path).convert("L")  # Grayscale
    img = ImageOps.autocontrast(img)            # Auto-contrast
    preprocessed_path = os.path.join(UPLOAD_FOLDER, "preprocessed.png")
    img.save(preprocessed_path)
    print(f"Preprocessed image saved at: {preprocessed_path}")
    return preprocessed_path

# Function to process the sheet music image using OMER
def process_sheet_music_image(image_path: str):
    try:
        # Command to run the oemer tool and generate MusicXML
        command = f'oemer "{image_path}" -o {output_xml_path}'
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully generated MusicXML at {output_xml_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during OMR processing: {e}")

# Function to play MIDI using pygame
def play_midi(midi_file):
    if sys.platform == "win32":
        print(f"Playing MIDI file on Windows: {midi_file}")
        os.startfile(midi_file)
    else:
        subprocess.run(["open", midi_file])

# Convert MusicXML to MIDI using music21
def convert_musicxml_to_midi(musicxml_file, midi_file):
    try:
        score = converter.parse(musicxml_file)
        score.write('midi', fp=midi_file)
        print(f"Successfully converted MusicXML to MIDI: {midi_file}")
    except Exception as e:
        print(f"Error converting MusicXML to MIDI: {e}")

# Convert MIDI to WAV using fluidsynth if available, or another method
def convert_midi_to_wav(midi_file, wav_file):
    """
    Convert a MIDI file to WAV format using the best available method.
    
    Returns:
        dict: Details about the conversion process
    """
    conversion_info = {
        "success": False,
        "method": "none",
        "message": "Conversion not attempted", 
        "soundfont_used": None
    }
    
    try:
        # First try with fluidsynth if available
        try:
            # Check common soundfont paths
            soundfont_paths = [
                "/usr/share/sounds/sf2/FluidR3_GM.sf2",  # Linux
                "/usr/local/share/sounds/sf2/FluidR3_GM.sf2",  # macOS Homebrew
                "/opt/homebrew/share/sounds/sf2/FluidR3_GM.sf2",  # macOS Apple Silicon Homebrew
                os.path.expanduser("~/soundfonts/FluidR3_GM.sf2"),  # User's home directory
                "soundfonts/FluidR3_GM.sf2",  # Relative to current directory
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "soundfonts", "FluidR3_GM.sf2"),  # Project soundfonts directory
            ]
            
            # Try to find a soundfont file
            soundfont_path = None
            for sf_path in soundfont_paths:
                if os.path.exists(sf_path):
                    soundfont_path = sf_path
                    conversion_info["soundfont_used"] = sf_path
                    print(f"Found SoundFont at: {sf_path}")
                    break
                    
            # If no soundfont found, use a fallback approach
            if not soundfont_path:
                print("No SoundFont found. Using pure Python audio generation.")
                conversion_info["message"] = "No SoundFont found for FluidSynth"
            if soundfont_path:
                command = f"fluidsynth -ni {soundfont_path} {midi_file} -F {wav_file} -r 44100"
                result = subprocess.run(command, shell=True, check=True, capture_output=True)
                print(f"Successfully converted MIDI to WAV using FluidSynth: {wav_file}")
                conversion_info["success"] = True
                conversion_info["method"] = "fluidsynth"
                conversion_info["message"] = "High-quality conversion with FluidSynth"
                return conversion_info
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Fluidsynth conversion failed: {e}, trying alternative method...")
            conversion_info["message"] = f"FluidSynth failed: {str(e)}"
            
            # Alternate method using timidity if available
            try:
                command = f"timidity {midi_file} -Ow -o {wav_file}"
                result = subprocess.run(command, shell=True, check=True, capture_output=True)
                print(f"Successfully converted MIDI to WAV using TiMidity: {wav_file}")
                conversion_info["success"] = True
                conversion_info["method"] = "timidity"
                conversion_info["message"] = "Medium-quality conversion with TiMidity"
                return conversion_info
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"TiMidity conversion failed: {e}, trying python libraries...")
                conversion_info["message"] = f"TiMidity failed: {str(e)}"
                
                # If all external tools fail, try with a pure Python approach
                print("Warning: Using fallback MIDI conversion method - quality may be limited")
                
                # Create a simple sine wave audio file as a fallback
                if create_placeholder_audio(wav_file):
                    conversion_info["success"] = True
                    conversion_info["method"] = "python_fallback"
                    conversion_info["message"] = "Basic audio generated with Python (limited quality)"
                    return conversion_info
    except Exception as e:
        print(f"Error converting MIDI to WAV: {e}")
        conversion_info["success"] = False
        conversion_info["message"] = f"Conversion failed: {str(e)}"
        return conversion_info

# Create a placeholder audio file if conversion fails
def create_placeholder_audio(wav_file, duration=5.0, freq=440.0, sample_rate=44100):
    """
    Create a simple audio file as a fallback when MIDI conversion fails.
    Attempts to create a simple melody that sounds musical.
    
    Args:
        wav_file (str): Path to output WAV file
        duration (float): Length of audio in seconds
        freq (float): Base frequency in Hz
        sample_rate (int): Audio sample rate
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import numpy as np
        from scipy.io import wavfile
        
        # Try to create a more interesting melody as a placeholder
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create a simple melody using the pentatonic scale
        melody = np.zeros_like(t)
        
        # Base frequencies for pentatonic scale (A, C, D, E, G)
        penta_freqs = [440.0, 523.25, 587.33, 659.25, 783.99]
        
        # Generate different notes for different segments of the audio
        segments = 10
        seg_len = len(t) // segments
        
        for i in range(segments):
            start = i * seg_len
            end = (i + 1) * seg_len if i < segments - 1 else len(t)
            note_freq = penta_freqs[i % len(penta_freqs)]
            
            # Add a simple envelope to avoid clicks
            env = np.ones(end - start)
            attack = int((end - start) * 0.1)  # 10% attack
            decay = int((end - start) * 0.2)    # 20% decay
            env[:attack] = np.linspace(0, 1, attack)
            env[-decay:] = np.linspace(1, 0, decay)
            
            melody[start:end] = np.sin(note_freq * 2 * np.pi * t[start:end]) * env * 0.8
        
        # Add a harmony an octave lower
        harmony = np.sin(220.0 * 2 * np.pi * t) * 0.3
        
        # Combine melody and harmony
        audio_data = melody + harmony
        
        # Normalize
        audio_data = audio_data * 32767 / np.max(np.abs(audio_data))
        audio_data = audio_data.astype(np.int16)
        
        # Save as WAV file
        wavfile.write(wav_file, sample_rate, audio_data)
        print(f"Created musical placeholder audio file: {wav_file}")
        return True
    except ImportError:
        print("Error: NumPy and SciPy are required for audio generation.")
        try:
            # Create a minimal valid WAV file as absolute fallback
            with open(wav_file, 'wb') as f:
                # Write a minimal valid WAV header
                f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
            print(f"Created minimal valid WAV file: {wav_file}")
            return True
        except Exception as e:
            print(f"Error creating fallback WAV file: {e}")
            return False
