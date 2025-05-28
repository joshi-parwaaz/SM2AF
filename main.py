from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from src.prototype import *
import os
import tempfile
import uuid
from install_soundfont import midi_to_mp3

app = FastAPI()
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
    # Create unique filenames to avoid conflicts
    unique_id = str(uuid.uuid4())
    temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_upload_{unique_id}.png")
    output_xml_path = f"output_{unique_id}.musicxml"
    output_midi_path = f"output_{unique_id}.mid"
    output_mp3_path = f"output_{unique_id}.mp3"
    
    preprocessed_path = None
    files_to_cleanup = []

    try:
        # Save uploaded image
        with open(temp_image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        files_to_cleanup.append(temp_image_path)
        
        # Process image
        preprocessed_path = preprocess_image(temp_image_path)
        if preprocessed_path:
            files_to_cleanup.append(preprocessed_path)
        
        # Process sheet music
        process_sheet_music_image(preprocessed_path if preprocessed_path else temp_image_path)

        if os.path.exists(output_xml_path):
            files_to_cleanup.append(output_xml_path)
            
            # Convert to MIDI
            convert_musicxml_to_midi(output_xml_path, output_midi_path)
            
            if os.path.exists(output_midi_path):
                files_to_cleanup.append(output_midi_path)
                
                try:
                    # Convert to MP3
                    midi_to_mp3(output_midi_path, output_mp3_path)
                    
                    if os.path.exists(output_mp3_path):
                        files_to_cleanup.append(output_mp3_path)
                        
                        # Create a custom FileResponse that handles cleanup
                        def cleanup_files():
                            for file_path in files_to_cleanup:
                                try:
                                    if os.path.exists(file_path):
                                        os.remove(file_path)
                                except Exception as e:
                                    print(f"Warning: Could not delete {file_path}: {e}")
                        
                        # Return FileResponse with background task for cleanup
                        from fastapi import BackgroundTasks
                        background_tasks = BackgroundTasks()
                        background_tasks.add_task(cleanup_files)
                        
                        return FileResponse(
                            path=output_mp3_path,
                            media_type='audio/mpeg',
                            filename='sheet_music.mp3',
                            background=background_tasks
                        )
                    else:
                        raise HTTPException(status_code=500, detail="MP3 generation failed - file not created")
                        
                except FileNotFoundError as e:
                    raise HTTPException(status_code=500, detail=f"SoundFont not found: {str(e)}")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"MP3 conversion failed: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail="MIDI generation failed")
        else:
            raise HTTPException(status_code=500, detail="MusicXML generation failed - could not process sheet music")
            
    except Exception as e:
        # Clean up files if there's an error
        for file_path in files_to_cleanup:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as cleanup_error:
                print(f"Warning: Could not delete {file_path}: {cleanup_error}")
        
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Alternative version without BackgroundTasks (simpler)
@app.post("/process-sheet-music-simple")
async def process_sheet_music_simple(image: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_upload_{unique_id}.png")
    output_xml_path = f"output_{unique_id}.musicxml"
    output_midi_path = f"output_{unique_id}.mid"
    output_mp3_path = f"output_{unique_id}.mp3"

    try:
        # Save uploaded image
        with open(temp_image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Process image
        preprocessed_path = preprocess_image(temp_image_path)
        process_sheet_music_image(preprocessed_path if preprocessed_path else temp_image_path)

        if not os.path.exists(output_xml_path):
            raise HTTPException(status_code=500, detail="Failed to process sheet music - no MusicXML generated")

        # Convert to MIDI
        convert_musicxml_to_midi(output_xml_path, output_midi_path)
        if not os.path.exists(output_midi_path):
            raise HTTPException(status_code=500, detail="Failed to convert to MIDI")

        # Convert to MP3
        midi_to_mp3(output_midi_path, output_mp3_path)
        if not os.path.exists(output_mp3_path):
            raise HTTPException(status_code=500, detail="Failed to convert to MP3")

        # Read the MP3 file into memory and return it
        with open(output_mp3_path, "rb") as f:
            mp3_content = f.read()

        # Clean up temporary files
        for file_path in [temp_image_path, preprocessed_path, output_xml_path, output_midi_path, output_mp3_path]:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {e}")

        # Return the MP3 content as a response
        from fastapi.responses import Response
        return Response(
            content=mp3_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=sheet_music.mp3"}
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        for file_path in [temp_image_path, output_xml_path, output_midi_path, output_mp3_path]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")