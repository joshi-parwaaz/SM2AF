from music21 import converter

input_xml = "output.musicxml"
output_midi = "output.mid"

# Load and convert
score = converter.parse(input_xml)
score.write('midi', fp=output_midi)

print("✅ Converted MusicXML to MIDI successfully.")
