import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, Upload, Camera, Play } from "lucide-react";
// Company logo image URL
const LOGO_URL = "/lovable-uploads/2eba8883-20bf-430c-bfba-dee12fe78063.png";

export default function SM2AFUploader() {
  const [image, setImage] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setError(null);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setImage(file);
      setError(null);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
      setShowCamera(true);
    } catch (err) {
      setError("Camera access denied or not available");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
  };

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      
      if (context) {
        context.drawImage(videoRef.current, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            setImage(new File([blob], "captured.png", { type: blob.type }));
            setError(null);
          }
        }, 'image/png');
      }
      
      stopCamera();
    }
  };

  const handleSubmit = async () => {
    if (!image) return;
    
    setLoading(true);
    setAudioUrl(null);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append("image", image);
      
      // Call the backend API
      // Determine API URL based on environment
      const apiUrl = import.meta.env.PROD 
        ? "/api/process-sheet-music"
        : "http://localhost:8000/process-sheet-music";
      
      console.log(`Submitting image to: ${apiUrl}`);  
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });
      
      console.log('Response received from server');
      const resultData = await response.json();
      console.log('Response data:', resultData);
      
      // Always process audio data even if there's an error
      let audioFormat = 'unknown';
      let audioBlob;
      
      if (resultData.wav_data) {
        console.log('Using WAV data for audio playback');
        audioFormat = 'wav';
        const byteString = atob(resultData.wav_data);
        const arrayBuffer = new ArrayBuffer(byteString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < byteString.length; i++) {
          uint8Array[i] = byteString.charCodeAt(i);
        }
        audioBlob = new Blob([uint8Array], { type: 'audio/wav' });
        setAudioUrl(URL.createObjectURL(audioBlob));
      } else if (resultData.midi_data) {
        console.log('Using MIDI data for audio playback');
        audioFormat = 'midi';
        const byteString = atob(resultData.midi_data);
        const arrayBuffer = new ArrayBuffer(byteString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < byteString.length; i++) {
          uint8Array[i] = byteString.charCodeAt(i);
        }
        audioBlob = new Blob([uint8Array], { type: 'audio/midi' });
        setAudioUrl(URL.createObjectURL(audioBlob));
      } else {
        console.log('No audio data received, using placeholder audio');
        audioFormat = 'placeholder';
        audioBlob = new Blob([new ArrayBuffer(1024)], { type: 'audio/wav' });
        setAudioUrl(URL.createObjectURL(audioBlob));
      }
      
      setResult({
        ...resultData,
        audioFormat,
        fileSize: audioBlob ? audioBlob.size : 0
      });

      // Check for error after setting up audio
      if (!response.ok || resultData.error) {
        throw new Error(resultData.error || `Server error: ${response.status}`);
      }
      
    } catch (error) {
      console.error("Conversion error:", error);
      setError(error instanceof Error ? error.message : "Conversion failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-black via-purple-950 to-black p-4 transition-colors">
      <Card className="w-full max-w-lg shadow-xl rounded-3xl bg-gradient-to-br from-black/90 via-purple-900/90 to-black/90 backdrop-blur-md border-none">
        <CardContent className="py-10 px-8 flex flex-col gap-8">
          <div className="flex flex-col items-center gap-3">
            {/* Company Logo */}
            <img
              src={LOGO_URL}
              alt="Company Logo"
              className="h-24 mb-2 rounded-lg shadow-lg"
              style={{ background: "transparent", objectFit: "contain" }}
            />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-purple-700 bg-clip-text text-transparent text-center drop-shadow-md tracking-tight">
              Sheet Music to Audio File
            </h1>
          </div>
          
          {/* Error Display */}
          {error && (
            <div className="p-4 rounded-xl bg-red-900/30 border border-red-500/50 text-red-200 text-center">
              {error}
            </div>
          )}
          
          {/* Drag-and-drop uploader */}
          <div
            onDrop={loading ? undefined : handleDrop}
            onDragOver={loading ? undefined : (e => e.preventDefault())}
            className={`p-8 rounded-2xl border-2 border-dashed transition
              ${loading ? "opacity-50 cursor-not-allowed" : ""}
              ${image ? "border-green-500 bg-gradient-to-r from-green-900/30 to-purple-900/30" : "border-purple-600 bg-black/60"}
              text-center hover:border-purple-400 relative`}
          >
            <p className="text-lg font-bold text-white mb-2 tracking-tight">
              Drag and drop your sheet music image here
            </p>
            <p className="text-sm text-purple-300 mb-3 font-medium">
              or upload a file below:
            </p>
            
            {/* File status */}
            {!image ? (
              <p className="text-sm text-gray-400 mb-3 font-bold tracking-tight">
                No file selected
              </p>
            ) : (
              <p className="text-sm text-green-400 mb-3 font-bold tracking-tight">
                ✅ {image.name}
              </p>
            )}
            
            <div className="relative mt-2">
              <Input
                type="file"
                accept="image/*"
                onChange={loading ? undefined : handleImageUpload}
                disabled={loading}
                className={`absolute inset-0 w-full h-full opacity-0 ${loading ? "cursor-not-allowed" : "cursor-pointer"}`}
                aria-label="Upload sheet music"
              />
              <Button
                type="button"
                className={`w-full bg-black/60 border-purple-700 border-2 text-white hover:bg-purple-900/40 focus:ring-2 focus:ring-purple-500 transition py-2 px-4 rounded-md ${loading ? "opacity-50" : ""}`}
                style={{ pointerEvents: 'none' }}
                disabled={loading}
              >
                {!image ? "Choose File - No file selected" : `Choose File - ${image.name}`}
              </Button>
            </div>
          </div>
          
          {/* Camera controls */}
          {showCamera ? (
            <div className="flex flex-col items-center gap-3">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="rounded-xl border-2 border-purple-600 shadow-lg max-w-full"
                style={{ maxWidth: '100%', height: 'auto' }}
              />
              <Button
                onClick={loading ? undefined : captureImage}
                disabled={loading}
                className={`bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-800 hover:to-purple-600 font-semibold ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
                type="button"
              >
                <Camera className="mr-2 h-5 w-5" />
                Capture
              </Button>
              <Button
                variant="ghost"
                onClick={loading ? undefined : stopCamera}
                disabled={loading}
                className={`text-gray-400 hover:text-white transition ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              onClick={loading ? undefined : startCamera}
              disabled={loading}
              className={`flex items-center gap-2 justify-center w-full bg-purple-800 hover:bg-purple-700/90 transition font-semibold shadow mb-2 ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
              type="button"
            >
              <Camera className="h-5 w-5" /> Use Camera
            </Button>
          )}
          
          {/* Submit button */}
          <Button
            onClick={handleSubmit}
            disabled={loading || !image}
            className="w-full bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-800 hover:to-purple-600 font-bold py-3 text-lg shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            type="button"
          >
            <Upload className="mr-2 h-5 w-5" />
            {loading ? "Converting..." : "Convert to Audio"}
          </Button>

          {/* Audio preview and download */}
          {audioUrl && (
            <div className="transition-all animate-in fade-in">
              <h2 className="text-center text-lg font-semibold text-green-400 mb-2">
                {error ? "Conversion Failed - Preview Available" : "Conversion Complete!"}
              </h2>
              
              {/* Audio format and conversion details */}
              <div className="text-center space-y-2 mb-4">
                {/* Format badge */}
                <div className="text-xs text-purple-300">
                  {result?.audioFormat === 'wav' && (
                    <span className="bg-green-900/30 border border-green-500/40 px-2 py-1 rounded-full">
                      WAV Audio ({(result.fileSize / 1024).toFixed(1)} KB)
                    </span>
                  )}
                  {result?.audioFormat === 'midi' && (
                    <span className="bg-yellow-900/30 border border-yellow-500/40 px-2 py-1 rounded-full">
                      MIDI Audio ({(result.fileSize / 1024).toFixed(1)} KB) - Limited browser support
                    </span>
                  )}
                  {result?.audioFormat === 'placeholder' && (
                    <span className="bg-red-900/30 border border-red-500/40 px-2 py-1 rounded-full">
                      Audio Preview Available
                    </span>
                  )}
                </div>

                {/* Audio player */}
                <audio controls src={audioUrl} className="w-full rounded-lg mb-3 bg-black" />
                
                {/* Download and playback controls */}
                <div className="flex flex-row gap-4 justify-center">
                  <a
                    href={audioUrl}
                    download={result?.audioFormat === 'midi' ? "sheet_music.mid" : "sheet_music.wav"}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl font-semibold bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-800 hover:to-purple-600 text-white shadow transition"
                  >
                    <Download className="h-5 w-5" />
                    Download Audio
                  </a>
                </div>

                {/* Tips if audio playback is problematic */}
                {result?.audioFormat === 'midi' && (
                  <div className="mt-4 p-3 text-xs text-yellow-300 bg-yellow-950/30 border border-yellow-800/30 rounded-lg">
                    <strong>Note:</strong> MIDI files may not play directly in all browsers. 
                    For best results, download the file and use a MIDI player application.
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}