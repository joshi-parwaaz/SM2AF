import logging
import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from src.prototype import preprocess_image, process_sheet_music_image, convert_musicxml_to_midi
from install_soundfont import midi_to_mp3, get_soundfont_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to the OMR API!"}

@app.get("/health")
def health_check():
    """Health check endpoint to verify system components."""
    try:
        # Check if SoundFont exists
        soundfont_path = get_soundfont_path()
        soundfont_exists = os.path.exists(soundfont_path)
        
        return {
            "status": "healthy",
            "soundfont_path": soundfont_path,
            "soundfont_exists": soundfont_exists,
            "upload_folder_exists": os.path.exists(UPLOAD_FOLDER)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/process-sheet-music")
async def process_sheet_music(image: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_upload_{unique_id}.png")
    output_xml_path = f"output_{unique_id}.musicxml"
    output_midi_path = f"output_{unique_id}.mid"
    output_mp3_path = f"output_{unique_id}.mp3"

    try:
        # Step 1: Save uploaded image
        logger.info(f"Saving uploaded image to {temp_image_path}")
        with open(temp_image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        logger.info("Image saved successfully")

        # Step 2: Preprocess image
        logger.info("Preprocessing image...")
        preprocessed_path = preprocess_image(temp_image_path)
        logger.info(f"Preprocessing completed: {preprocessed_path or temp_image_path}")

        # Step 3: Process sheet music image to generate MusicXML
        logger.info("Processing sheet music image to generate MusicXML...")
        try:
            process_sheet_music_image(preprocessed_path if preprocessed_path else temp_image_path)
        except Exception as e:
            logger.error(f"MusicXML generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process sheet music image: {str(e)}")

        # Step 3.1: Rename the generated MusicXML file to the unique name
        if os.path.exists("output.musicxml"):
            os.rename("output.musicxml", output_xml_path)
            logger.info(f"Renamed MusicXML to {output_xml_path}")
        else:
            logger.error("MusicXML output file not found")
            raise HTTPException(status_code=500, detail="Failed to generate MusicXML - output.musicxml not found")

        # Step 4: Convert MusicXML to MIDI
        logger.info("Converting MusicXML to MIDI...")
        try:
            convert_musicxml_to_midi(output_xml_path, output_midi_path)
        except Exception as e:
            logger.error(f"MIDI conversion failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to convert MusicXML to MIDI: {str(e)}")
        if not os.path.exists(output_midi_path):
            logger.error("MIDI output file not created")
            raise HTTPException(status_code=500, detail="Failed to generate MIDI - output file not created")
        logger.info("MIDI conversion successful")

        # Step 5: Convert MIDI to MP3
        logger.info("Converting MIDI to MP3...")
        try:
            # Check SoundFont before conversion
            soundfont_path = get_soundfont_path()
            logger.info(f"Using SoundFont: {soundfont_path}")
            
            if not os.path.exists(soundfont_path):
                raise FileNotFoundError(f"SoundFont not found at: {soundfont_path}")
            
            # Perform conversion
            midi_to_mp3(output_midi_path, output_mp3_path)
            
        except FileNotFoundError as e:
            logger.error(f"SoundFont not found: {str(e)}")
            raise HTTPException(status_code=500, detail=f"SoundFont not found during MP3 conversion: {str(e)}")
        except Exception as e:
            logger.error(f"MP3 conversion failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to convert MIDI to MP3: {str(e)}")
        
        if not os.path.exists(output_mp3_path):
            logger.error("MP3 output file not created")
            raise HTTPException(status_code=500, detail="Failed to generate MP3 - output file not created")
        
        logger.info("MP3 conversion successful")

        # Step 6: Read MP3 file and prepare response
        logger.info("Reading MP3 file for response...")
        with open(output_mp3_path, "rb") as f:
            mp3_content = f.read()

        # Verify MP3 content
        if len(mp3_content) == 0:
            logger.error("Generated MP3 file is empty")
            raise HTTPException(status_code=500, detail="Generated MP3 file is empty")

        logger.info(f"MP3 file size: {len(mp3_content)} bytes")

        # Clean up temporary files
        logger.info("Cleaning up temporary files...")
        for file_path in [temp_image_path, preprocessed_path, output_xml_path, output_midi_path, output_mp3_path]:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete {file_path}: {str(e)}")
        logger.info("Cleanup completed")

        # Return MP3 response
        return Response(
            content=mp3_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=sheet_music.mp3",
                "Content-Length": str(len(mp3_content))
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}")
        # Clean up on error
        for file_path in [temp_image_path, preprocessed_path, output_xml_path, output_midi_path, output_mp3_path]:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as cleanup_error:
                logger.warning(f"Could not delete {file_path}: {str(cleanup_error)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process-sheet-music-debug")
async def process_sheet_music_debug(image: UploadFile = File(...)):
    """Debug endpoint that returns detailed information about each step."""
    unique_id = str(uuid.uuid4())
    temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_upload_{unique_id}.png")
    output_xml_path = f"output_{unique_id}.musicxml"
    output_midi_path = f"output_{unique_id}.mid"
    output_mp3_path = f"output_{unique_id}.mp3"
    
    debug_info = {
        "steps": [],
        "files_created": [],
        "errors": []
    }

    try:
        # Step 1: Save uploaded image
        debug_info["steps"].append("Saving uploaded image")
        with open(temp_image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        debug_info["files_created"].append(temp_image_path)

        # Step 2: Preprocess image
        debug_info["steps"].append("Preprocessing image")
        preprocessed_path = preprocess_image(temp_image_path)
        if preprocessed_path:
            debug_info["files_created"].append(preprocessed_path)

        # Step 3: Process sheet music image
        debug_info["steps"].append("Processing sheet music to MusicXML")
        process_sheet_music_image(preprocessed_path if preprocessed_path else temp_image_path)
        
        if os.path.exists("output.musicxml"):
            os.rename("output.musicxml", output_xml_path)
            debug_info["files_created"].append(output_xml_path)

        # Step 4: Convert to MIDI
        debug_info["steps"].append("Converting MusicXML to MIDI")
        convert_musicxml_to_midi(output_xml_path, output_midi_path)
        if os.path.exists(output_midi_path):
            debug_info["files_created"].append(output_midi_path)

        # Step 5: Convert to MP3
        debug_info["steps"].append("Converting MIDI to MP3")
        try:
            soundfont_path = get_soundfont_path()
            debug_info["soundfont_path"] = soundfont_path
            debug_info["soundfont_exists"] = os.path.exists(soundfont_path)
            
            midi_to_mp3(output_midi_path, output_mp3_path)
            if os.path.exists(output_mp3_path):
                debug_info["files_created"].append(output_mp3_path)
                debug_info["mp3_size"] = os.path.getsize(output_mp3_path)
        except Exception as e:
            debug_info["errors"].append(f"MP3 conversion error: {str(e)}")

        # Clean up
        for file_path in [temp_image_path, preprocessed_path, output_xml_path, output_midi_path, output_mp3_path]:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

        return debug_info

    except Exception as e:
        debug_info["errors"].append(f"Processing error: {str(e)}")
        return debug_info

if __name__ == "__main__":
    import uvicorn
    try:
        logger.info("Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        logger.info("Server started successfully")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise