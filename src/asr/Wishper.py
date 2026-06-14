import whisper
from pathlib import Path

# =========================================
# AUDIO DIRECTORY
# =========================================
AUDIO_DIR = Path("math_audio")

# =========================================
# OUTPUT DIRECTORY
# =========================================
OUTPUT_DIR = Path("Math_transcripts")

OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================
# LOAD WHISPER MODEL
# =========================================
model = whisper.load_model("base")

# خيارات أخرى:
# tiny   -> أسرع وأقل دقة
# small  -> أفضل
# medium -> أقوى
# large  -> أعلى دقة (أبطأ)

# =========================================
# PROCESS AUDIO FILES
# =========================================
for audio_file in AUDIO_DIR.glob("*.wav"):

    print(f"\nProcessing: {audio_file.name}")

    try:

        result = model.transcribe(
            str(audio_file),
            language="ar",
            fp16=False
        )

        transcript_text = result["text"]

        output_file = OUTPUT_DIR / f"{audio_file.stem}.txt"

        output_file.write_text(
            transcript_text,
            encoding="utf-8"
        )

        print(f"Saved: {output_file}")

    except Exception as e:

        print(f"Error processing {audio_file.name}: {e}")

print("\nAll audio files transcribed successfully.")