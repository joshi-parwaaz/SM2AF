import os
import subprocess
import uuid
import pygame
from music21 import converter, midi
import cv2
import numpy as np

# Path where files will be saved
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to capture an image from the webcam
def capture_sheet_music_image():
    """
    Capture a sheet music image using the webcam.
    The image will be saved with a unique name.
    """
    captured_image = f"captured_{uuid.uuid4().hex[:6]}.png"
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
            cv2.imwrite(os.path.join(UPLOAD_FOLDER, captured_image), frame)
            print(f"✅ Image saved as {captured_image}")
            break
    cap.release()
    cv2.destroyAllWindows()
    return os.path.join(UPLOAD_FOLDER, captured_image)

# Function to enhance and clean up the scanned image
def enhance_scanned_image(input_path, output_path="scanned_output.png"):
    """
    Clean up the image, enhance contrast, and apply adaptive thresholding.
    """
    img = cv2.imread(input_path)
    orig = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_cnt = approx
            break
    else:
        print("⚠️ Document edges not found, using original image.")
        doc_cnt = np.array([[[0,0]], [[img.shape[1],0]], [[img.shape[1], img.shape[0]]], [[0, img.shape[0]]]])

    def reorder(pts):
        pts = pts.reshape(4, 2)
        new_pts = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        new_pts[0] = pts[np.argmin(s)]
        new_pts[2] = pts[np.argmax(s)]
        new_pts[1] = pts[np.argmin(diff)]
        new_pts[3] = pts[np.argmax(diff)]
        return new_pts

    pts1 = reorder(doc_cnt)
    (tl, tr, br, bl) = pts1
    width = max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))
    height = max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))

    pts2 = np.array([[0,0], [width-1,0], [width-1,height-1], [0,height-1]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    scanned = cv2.warpPerspective(orig, matrix, (int(width), int(height)))

    scanned_gray = cv2.cvtColor(scanned, cv2.COLOR_BGR2GRAY)
    scanned_clean = cv2.adaptiveThreshold(scanned_gray, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 10)

    cv2.imwrite(output_path, scanned_clean)
    print(f"✅ Scanned image saved as {output_path}")
    return output_path

# Function to run OMR (Optical Music Recognition) with oemer
def run_omr(image_path, output_xml_path="output.musicxml"):
    """
    Use oemer to convert the scanned image to MusicXML.
    """
    command = f'oemer "{image_path}" -o {output_xml_path}'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ MusicXML generated: {output_xml_path}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ OMR failed: {e}")
        return None
    return output_xml_path

# Function to convert MusicXML to MIDI and play it
def convert_and_play_music(musicxml_file, midi_file="output.mid"):
    """
    Convert MusicXML to MIDI using music21 and play the MIDI file.
    """
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

# Main function to process the sheet music and generate audio
def process_and_play_sheet_music(image_path):
    """
    Complete flow: Capture image, preprocess, OMR, convert to MIDI, and play.
    """
    # Step 1: Enhance and clean the image
    enhanced_image_path = enhance_scanned_image(image_path)

    # Step 2: Run OMR to generate MusicXML
    musicxml_path = run_omr(enhanced_image_path)
    if not musicxml_path:
        return "Error during OMR processing."

    # Step 3: Convert MusicXML to MIDI
    convert_and_play_music(musicxml_path)

# If running as a standalone script
if __name__ == "__main__":
    # Capture and process an image (this can be skipped in a web app)
    image_path = capture_sheet_music_image()  # In a web app, this would come as a file upload
    process_and_play_sheet_music(image_path)
