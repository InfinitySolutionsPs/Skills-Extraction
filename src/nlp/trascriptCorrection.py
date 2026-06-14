import os
import time
from pathlib import Path
from google import genai

# =========================
# GEMINI API KEY
# =========================
API_KEY = "AIzaSyB2zJrGaJCE1cy8r_vu0AxAPXZftHbcbGc"

# =========================
# INPUT / OUTPUT DIRECTORIES
# =========================
INPUT_DIR = Path("transcripts")
OUTPUT_DIR = Path("corrected_transcripts")

OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# GEMINI CLIENT
# =========================
client = genai.Client(api_key=API_KEY)

# =========================
# SPLIT LONG TRANSCRIPTS
# =========================
def split_text(text, chunk_size=3000):
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


# =========================
# CORRECT ARABIC TRANSCRIPT
# =========================
def correct_arabic_chunk(chunk):

    prompt = f"""
You are an Arabic educational transcript correction assistant.

Task:
Correct the following Arabic ASR transcript into clear Modern Standard Arabic suitable for NLP analysis.

Rules:
1. Do not summarize.
2. Do not add new information.
3. Preserve the original educational meaning.
4. Convert spoken or pronunciation-based Arabic into Modern Standard Arabic.
5. Correct spelling and punctuation.
6. Keep mathematical, scientific, and curriculum-related terms accurate.
7. Keep the original lesson structure.
8. If a word is unclear, keep it and mark it with [unclear].

Transcript:
\"\"\"
{chunk}
\"\"\"
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# =========================
# PROCESS ALL FILES
# =========================
for file in INPUT_DIR.glob("*.txt"):

    print(f"\nProcessing: {file.name}")

    raw_text = file.read_text(encoding="utf-8")

    chunks = split_text(raw_text, chunk_size=3000)

    corrected_chunks = []

    for i, chunk in enumerate(chunks, start=1):

        print(f"  Correcting chunk {i}/{len(chunks)}")

        try:
            corrected_text = correct_arabic_chunk(chunk)

            corrected_chunks.append(corrected_text)

            print("  Chunk corrected successfully.")

            # Sleep لتخفيف الضغط على API
            time.sleep(2)

        except Exception as e:
            print(f"  Error in chunk {i}: {e}")

    # دمج النتائج
    final_text = "\n\n".join(corrected_chunks)

    # حفظ الملف النهائي
    output_file = OUTPUT_DIR / f"{file.stem}_corrected.txt"

    output_file.write_text(final_text, encoding="utf-8")

    print(f"Saved: {output_file}")

print("\nAll transcripts corrected successfully.")
