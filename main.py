from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.prototype import *
import os
import base64

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
    Endpoint to process a sheet music image and return the MusicXML, MIDI, and WAV data.
    Endpoint to process a sheet music image and return the MIDI file.
    """
    from fastapi.responses import JSONResponse
    import base64
    
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
    output_wav_path = "output.wav"

    # Check if the MusicXML file was created successfully
    if os.path.exists(output_xml_path):
        convert_musicxml_to_midi(output_xml_path, output_midi_path)
        
        # Convert MIDI to WAV for browser compatibility
        if os.path.exists(output_midi_path):
            conversion_info = convert_midi_to_wav(output_midi_path, output_wav_path)
            
            # Read the MIDI and WAV files and encode them in base64
            with open(output_midi_path, "rb") as midi_file:
                midi_data = midi_file.read()
                midi_base64 = base64.b64encode(midi_data).decode("utf-8")
            
            # If WAV conversion was successful, include it in the response
            wav_base64 = None
            if os.path.exists(output_wav_path) and conversion_info["success"]:
                with open(output_wav_path, "rb") as wav_file:
                    wav_data = wav_file.read()
                    wav_base64 = base64.b64encode(wav_data).decode("utf-8")
                
            return {
                "message": "Audio generation successful", 
                "musicxml_path": output_xml_path,
                "midi_data": midi_base64,
                "wav_data": wav_base64,
                "conversion_details": {
                    "success": conversion_info["success"],
                    "method": conversion_info["method"],
                    "message": conversion_info["message"],
                    "soundfont": conversion_info.get("soundfont_used")
                }
            }
        else:
            return {"error": "MIDI generation failed"}
        
        # Return the MIDI file directly
        return FileResponse(
            path=output_midi_path,
            media_type='audio/midi',
            filename='output.mid'
        )
    else:
        return {"error": "MusicXML generation failed"}


if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Starting FastAPI server on http://127.0.0.1:8000/")