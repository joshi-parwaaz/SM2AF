
import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, Upload, Camera, Play } from "lucide-react";
import Webcam from "react-webcam";

// Company logo image URL
const LOGO_URL = "/lovable-uploads/2eba8883-20bf-430c-bfba-dee12fe78063.png";

export default function SM2AFUploader() {
  const [image, setImage] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [loading, setLoading] = useState(false);
  const webcamRef = useRef<Webcam | null>(null);

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setImage(file);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) setImage(file);
  };

  const captureImage = () => {
    if (webcamRef.current) {
      const screenshot = webcamRef.current.getScreenshot();
      if (screenshot) {
        fetch(screenshot)
          .then(res => res.blob())
          .then(blob => setImage(new File([blob], "captured.png", { type: blob.type })));
        setShowCamera(false);
      }
    }
  };

  const handleSubmit = async () => {
    if (!image) return;
    setLoading(true);
    setAudioUrl(null);
    try {
      const formData = new FormData();
      formData.append("file", image);
      const response = await fetch("/api/convert", { method: "POST", body: formData });
      const blob = await response.blob();
      setAudioUrl(URL.createObjectURL(blob));
    } catch (error) {
      // (Optional) You may want to show a toast here for error handling
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-black via-purple-950 to-black p-4 transition-colors">
      <Card className="w-full max-w-lg shadow-xl rounded-3xl bg-gradient-to-br from-black/90 via-purple-900/90 to-black/90 backdrop-blur-md border-none">
        <CardContent className="py-10 flex flex-col gap-8">
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
          {/* Drag-and-drop uploader */}
          <div
            onDrop={handleDrop}
            onDragOver={e => e.preventDefault()}
            className={`p-6 rounded-2xl border-2 border-dashed transition
              ${image ? "border-green-500 bg-gradient-to-r from-green-900/30 to-purple-900/30" : "border-purple-600 bg-black/60"}
              text-center hover:border-purple-400 relative`}
          >
            <p className="text-lg font-medium text-white">Drag and drop your sheet music image here</p>
            <p className="text-sm text-purple-300 mt-1 mb-2">or upload a file below:</p>
            <Input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="mt-2 bg-black/60 border-purple-700 text-white cursor-pointer focus:ring-2 focus:ring-purple-500 transition"
              aria-label="Upload sheet music"
            />
            {image && (
              <div className="absolute right-4 bottom-2 text-green-400 text-xs font-semibold animate-pulse">
                ✔️ Image loaded
              </div>
            )}
          </div>
          {/* Camera */}
          {showCamera ? (
            <div className="flex flex-col items-center gap-3">
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/png"
                className="rounded-xl border-2 border-purple-600 shadow-lg max-w-full"
                videoConstraints={{ facingMode: "environment" }}
              />
              <Button
                onClick={captureImage}
                className="bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-800 hover:to-purple-600 font-semibold"
                type="button"
              >
                <Camera className="mr-2 h-5 w-5" />
                Capture
              </Button>
              <Button
                variant="ghost"
                onClick={() => setShowCamera(false)}
                type="button"
                className="text-gray-400 hover:text-white transition"
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              onClick={() => setShowCamera(true)}
              className="flex items-center gap-2 justify-center w-full bg-purple-800 hover:bg-purple-700/90 transition font-semibold shadow mb-2"
              type="button"
            >
              <Camera className="h-5 w-5" /> Use Camera
            </Button>
          )}
          {/* Submit button */}
          <Button
            onClick={handleSubmit}
            disabled={loading || !image}
            className="w-full bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-800 hover:to-purple-600 font-bold py-3 text-lg shadow-lg transition"
            type="button"
          >
            <Upload className="mr-2 h-5 w-5" />
            {loading ? "Converting..." : "Convert to Audio"}
          </Button>
          {/* Audio preview and download */}
          {audioUrl && (
            <div className="transition-all animate-in fade-in">
              <h2 className="text-center text-lg font-semibold text-green-400 mb-2">Conversion Complete!</h2>
              <audio controls src={audioUrl} className="w-full rounded-lg mb-3 bg-black" />
              <div className="flex flex-row gap-4 justify-center">
                <a
                  href={audioUrl}
                  download="output.wav"
                  className="flex items-center gap-2 px-4 py-2 rounded-xl font-semibold bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-800 hover:to-purple-600 text-white shadow transition"
                >
                  <Download className="h-5 w-5" />
                  Download Audio
                </a>
                <Button
                  onClick={() => {
                    const audio = document.querySelector("audio");
                    audio?.play();
                  }}
                  className="flex items-center gap-2 bg-black/60 text-purple-300 hover:text-purple-100 border border-purple-800"
                  type="button"
                >
                  <Play className="h-5 w-5" />
                  Play Again
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
