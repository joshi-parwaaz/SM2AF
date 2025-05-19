📄 README.md
markdown
Copy
Edit
# Sheet Music to Audio (SM2AF)

This prototype converts an image of sheet music into playable audio. It performs **Optical Music Recognition (OMR)** to extract musical notes from an image and synthesizes audio using MIDI playback.

---

## 📌 Features

- 🎼 Converts sheet music images into MusicXML
- 🎹 Generates MIDI files from MusicXML
- 🔊 Plays MIDI audio using Python
- 🧩 Built using open-source tools: Oemer, music21, and pygame

---

## 📂 Directory Structure

SM2AF/
│
├── prototype.py # Main script to run the full pipeline
├── output.musicxml # Generated MusicXML file
├── output.mid # Generated MIDI file
├── input.png # Sheet music image
├── requirements.txt # Project dependencies
└── README.md # This file

yaml
Copy
Edit

---

## 🛠️ Setup Instructions

### 1. Create virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate    # On Windows
2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
🚀 How to Run
1. Add your sheet music image
Place it in the root directory and rename it to:

css
Copy
Edit
input.png
Or update the path in prototype.py.

2. Run the script
bash
Copy
Edit
python prototype.py
This will:

Generate output.musicxml from input.png

Convert it to output.mid

Play the resulting audio

🧪 Tested On
Python 3.10

Windows 10

CPU-only environment (GPU not required)

✅ Next Steps
Integrate a user interface for drag-and-drop image input

Add playback controls

Improve visual feedback with note highlighting

Package as a desktop or web app

🙏 Acknowledgements
Oemer

music21

pygame

👨‍💻 Author
Developed by Parwaaz Joshi for academic/research demonstration.

yaml
Copy
Edit

---

### ✅ Also create a `requirements.txt` file like this:

oemer
music21
pygame

vbnet
Copy
Edit

Let me know if you’d like a GitHub `.gitignore` or licensing template too!
