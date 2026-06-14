import json
import time
from pathlib import Path
from google import genai

API_KEY = "AIzaSyB2zJrGaJCE1cy8r_vu0AxAPXZftHbcbGc"

INPUT_DIR = Path("corrected_transcripts")
OUTPUT_DIR = Path("skill_analysis_results")

OUTPUT_DIR.mkdir(exist_ok=True)

client = genai.Client(api_key=API_KEY)


def split_text(text, chunk_size=3500):
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


def analyze_skills(chunk):
    prompt = f"""
You are an educational AI analysis assistant.

Analyze the following Arabic educational transcript from a Palestinian curriculum lesson.

Tasks:
1. Extract the main educational concepts.
2. Extract the educational skills taught in the lesson.
3. Estimate the difficulty level for each skill: Easy, Medium, or Hard.
4. Identify prerequisite knowledge needed for each skill.
5. Provide a short AI-based educational recommendation.

Important rules:
- The transcript may contain ASR errors or unclear words.
- Ignore unclear or irrelevant noisy parts.
- Focus only on meaningful educational content.
- Do not invent skills unrelated to the transcript.
- Return ONLY valid JSON.
- Do not use markdown.

Required JSON format:
{{
  "concepts": [
    "concept 1",
    "concept 2"
  ],
  "skills": [
    {{
      "skill_name": "Skill name in English",
      "skill_description": "Short description",
      "difficulty": "Easy/Medium/Hard",
      "prerequisites": ["prerequisite 1", "prerequisite 2"],
      "recommendation": "Short recommendation"
    }}
  ],
  "overall_recommendation": "General recommendation for the lesson"
}}

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


def clean_json_response(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return text


for file in INPUT_DIR.glob("*.txt"):
    print(f"\nAnalyzing: {file.name}")

    raw_text = file.read_text(encoding="utf-8")
    chunks = split_text(raw_text)

    all_results = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"  Analyzing chunk {i}/{len(chunks)}")

        try:
            result_text = analyze_skills(chunk)
            result_text = clean_json_response(result_text)

            result_json = json.loads(result_text)

            all_results.append({
                "chunk_id": i,
                "analysis": result_json
            })

            print("  Chunk analyzed successfully.")
            time.sleep(2)

        except Exception as e:
            print(f"  Error in chunk {i}: {e}")

    output_file = OUTPUT_DIR / f"{file.stem}_skills.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"Saved: {output_file}")

print("\nSkill extraction completed.")
