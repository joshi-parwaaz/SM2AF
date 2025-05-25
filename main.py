from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.prototype import *
import os

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the OMR API!"}

@app.post("/process-sheet-music")
async def process_sheet_music(image: UploadFile = File(...)):
    """
    Endpoint to process a sheet music image and return the MusicXML path.
    """
    # Save the uploaded file temporarily
    temp_image_path = os.path.join(UPLOAD_FOLDER, "temp_upload.png")
    with open(temp_image_path, "wb") as buffer:
        content = await image.read()
        buffer.write(content)
    
    # Preprocess the image if necessary
    preprocessed_path = preprocess_image(temp_image_path)
    
    # Process sheet music image to generate MusicXML
    process_sheet_music_image(preprocessed_path)

    output_xml_path = "output.musicxml"
    output_midi_path = "output.mid"

    # Check if the MusicXML file was created successfully
    if os.path.exists(output_xml_path):
        convert_musicxml_to_midi(output_xml_path, output_midi_path)
        play_midi(output_midi_path)
        return {"message": "MusicXML generated successfully", "musicxml_path": output_xml_path}
    else:
        return {"error": "MusicXML generation failed"}


if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Starting FastAPI server on http://127.0.0.1:8000/")