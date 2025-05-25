import cv2
import uuid
import os
import subprocess
from music21 import converter
import pygame

# Define paths
captured_image = f"captured_{uuid.uuid4().hex[:6]}.png"
musicxml_output = "output.musicxml"
midi_output = "output.mid"

# Capture image from webcam
def capture_sheet_music_image():
    cap = cv2.VideoCapture(0)
    print("📷 Press SPACE to capture sheet music, or ESC to exit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Sheet Music Capture", frame)
        key = cv2.waitKey(1)
        if key % 256 == 27:  # ESC
            print("❌ Capture canceled.")
            break
        elif key % 256 == 32:  # SPACE
            cv2.imwrite(captured_image, frame)
            print(f"✅ Image saved as {captured_image}")
            break
    cap.release()
    cv2.destroyAllWindows()

# Process with OMR (oemer)
def run_omr(image_path):
    command = f'oemer "{image_path}" -o {musicxml_output}'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ MusicXML generated: {musicxml_output}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ OMR failed: {e}")

# Convert to MIDI and play
def convert_and_play_music(musicxml_file, midi_file):
    try:
        score = converter.parse(musicxml_file)
        score.write('midi', fp=midi_file)
        print(f"🎼 MIDI generated: {midi_file}")
        pygame.mixer.init()
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"⚠️ Error in MIDI playback: {e}")

# Main execution
if __name__ == "__main__":
    capture_sheet_music_image()
    if os.path.exists(captured_image):
        run_omr(captured_image)
        if os.path.exists(musicxml_output):
            convert_and_play_music(musicxml_output, midi_output)
