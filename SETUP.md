# SM2AF Application Setup and Improvement Guide

## Basic Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontEnd
   npm install
   ```

## Running the Application

1. Start the backend server:
   ```bash
   python main.py
   ```
2. Start the frontend development server:
   ```bash
   cd frontEnd
   npm run dev
   ```
3. Access the application at http://localhost:8080 (or the port shown in the terminal)

## Improving Audio Quality

The application currently uses a fallback method to generate audio files. To improve the audio quality, you can install external tools that provide better MIDI to WAV conversion:

### Installing FluidSynth (recommended)

#### macOS
```bash
brew install fluid-synth
```

#### Ubuntu/Debian
```bash
sudo apt-get install fluidsynth
```

#### Windows
Download from: https://github.com/FluidSynth/fluidsynth/releases

### Installing a SoundFont

FluidSynth requires a SoundFont file to generate quality audio. Download a free SoundFont like FluidR3_GM:

1. Download from: https://musical-artifacts.com/artifacts/1229
2. Place the .sf2 file in one of these locations:
   - Linux: `/usr/share/sounds/sf2/FluidR3_GM.sf2`
   - macOS: `/usr/local/share/sounds/sf2/FluidR3_GM.sf2`
   - Or specify the path in the `convert_midi_to_wav` function in `src/prototype.py`

### Alternative: TiMidity++

If FluidSynth doesn't work well on your system, try TiMidity++:

#### macOS
```bash
brew install timidity
```

#### Ubuntu/Debian
```bash
sudo apt-get install timidity
```

#### Windows
Download from: http://timidity.sourceforge.net/

## Troubleshooting

If you encounter issues with the audio conversion:
1. Check if FluidSynth or TiMidity is properly installed
2. Ensure the SoundFont file is accessible
3. Check permissions for writing to output files
4. Examine the terminal output for specific error messages
