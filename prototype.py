import os
import subprocess
import pygame
from music21 import converter, midi
import sys

# take the current directory as the working directory
path = os.getcwd()

# Path to the image you want to process
sheet_music_image_path = os.path.join(path, "input.png")
print(f"Processing sheet music image at: {sheet_music_image_path}")
output_xml_path = "output.musicxml"

# Function to process the sheet music image using OMER
def process_sheet_music_image(image_path):
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

# Main function
def main():
    # Process sheet music image to generate MusicXML
    # process_sheet_music_image(sheet_music_image_path)

    # Check if the MusicXML file was created successfully
    if os.path.exists(output_xml_path):
        # Convert the generated MusicXML to MIDI
        convert_musicxml_to_midi(output_xml_path, "output.mid")

        # Play the resulting MIDI file
        play_midi("output.mid")
    else:
        print(f"Error: {output_xml_path} was not created. Cannot continue.")

if __name__ == "__main__":
    main()
