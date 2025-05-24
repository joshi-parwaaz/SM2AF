import os
import subprocess
import pygame
from music21 import converter, midi
import sys
from PIL import Image, ImageOps
from fastapi import FastAPI, File, UploadFile

# Define paths
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# take the current directory as the working directory
path = os.getcwd()

output_xml_path = os.path.join(UPLOAD_FOLDER, "output.musicxml")

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
