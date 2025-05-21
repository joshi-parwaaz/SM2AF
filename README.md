# Sheet Music to Audio (SM2AF)

This project provides a prototype to convert sheet music images into playable audio. It leverages **Optical Music Recognition (OMR)** to extract musical notes from images and synthesizes audio via MIDI playback.

---

## 📌 **Features**

- 🎼 Converts sheet music images into **MusicXML**
- 🎹 Generates **MIDI** files from **MusicXML**
- 🔊 Plays **MIDI** audio using **pygame**
- 🧩 Built using open-source tools: **Oemer**, **music21**, **pygame**, **OpenCV**

---

## 📂 **Directory Structure**

SM2AF/
│
├── sheet_music_processor.py # Main script with functions for image capture, OMR, MusicXML conversion, and MIDI playback
├── cam.py # Script for capturing sheet music from the webcam
├── scanner.py # Script for enhancing and cleaning the scanned image
├── uploads/ # Folder for uploaded sheet music images and processed files
├── requirements.txt # Project dependencies
└── README.md # This file

pgsql
Copy
Edit

- **`sheet_music_processor.py`**: This file encapsulates all major functionalities, including image capture, Optical Music Recognition (OMR), MusicXML to MIDI conversion, and MIDI playback. It should be used as the central script for web app integration.
- **`cam.py`**: Contains the logic for capturing sheet music images from a webcam.
- **`scanner.py`**: Used for enhancing and cleaning the scanned sheet music image.
- **`uploads/`**: Directory for saving the uploaded sheet music images and processed files.
- **`requirements.txt`**: Contains all the project dependencies.
- **`README.md`**: This file.

---

## 🛠️ **Setup Instructions**

### 1. **Create Virtual Environment** (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate    # On Windows
source venv/bin/activate # On Mac/Linux
2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
🚀 How to Use
1. Capture or Upload Sheet Music Image
You can either capture an image from your webcam or upload your own image.

For the web app team: Handle the image upload as per your web app’s file input mechanism.

For local testing: Use sheet_music_processor.py to capture an image from the webcam. Run:

bash
Copy
Edit
python sheet_music_processor.py
This will prompt you to press the SPACE key to capture the image or ESC to cancel. The captured image will be saved in the uploads/ folder.

2. Process the Image and Play the Audio
Once the image is captured or uploaded, the script will automatically:

Enhance the image by cleaning up the scan.

Use OMR (Oemer) to convert the image to MusicXML.

Convert the MusicXML file to MIDI using music21.

Play the resulting MIDI audio using pygame.

🧪 Tested On
Python: 3.10

Operating System: Windows 10

Environment: CPU-only (GPU not required)

✅ Next Steps
Integrate a user interface for drag-and-drop image input.

Add playback controls (pause, stop, volume control, etc.).

Improve visual feedback with note highlighting on the sheet music.

Package as a desktop or web application.

🙏 Acknowledgements
Oemer: Optical Music Recognition tool for converting sheet music images to MusicXML.

music21: For converting MusicXML to MIDI and for music analysis.

pygame: For playing MIDI files.

OpenCV: For image processing and webcam capture.

👨‍💻 Author
Developed by Parwaaz Joshi for academic/research demonstration.

✅ Requirements File (requirements.txt)
Ensure that the requirements.txt file contains the following dependencies for the project:

nginx
Copy
Edit
oemer
music21
pygame
opencv-python
numpy
✅ Additional Information
If you'd like to include a .gitignore or licensing template, feel free to request it!

Web App Integration Note:
The sheet_music_processor.py file is the main script that encapsulates all key functionalities. It should be used as the foundation for integration into the web app. The other scripts (cam.py, scanner.py) focus on specific features and can be used individually if needed.

markdown
Copy
Edit

### Changes Made:
1. **Main Integration Script (`sheet_music_processor.py`)**: Clearly emphasized that this is the core script for integration, handling all the major functionality.
2. **Directory Structure**: Included the files and added `uploads/` as a folder to save images and processed files.
3. **Instructions**: Detailed steps on how to capture or upload images, process them, and play the audio.
4. **Web Integration**: Specified that the web team should use `sheet_music_processor.py` for core integration.
   
This markdown version should be ready for your GitHub upload, and it provides clear instructions for both local usage and the web integration process.



