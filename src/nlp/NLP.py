import re
import json
from pathlib import Path

INPUT_DIR = Path("corrected_transcripts")
OUTPUT_DIR = Path("nlp_processed")

OUTPUT_DIR.mkdir(exist_ok=True)

ARABIC_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u0640]")

STOPWORDS = {
    "من", "في", "على", "إلى", "الى", "عن", "أن", "ان", "إن", "انه", "أنها",
    "هذا", "هذه", "ذلك", "تلك", "الذي", "التي", "الذين", "ثم", "أو", "او",
    "و", "ف", "ب", "ك", "ل", "كان", "كانت", "يكون", "مع", "ما", "لا",
    "نعم", "أيضا", "ايضا", "هنا", "هناك", "كل", "بعض", "بعد", "قبل"
}

def normalize_arabic(text):
    text = re.sub(ARABIC_DIACRITICS, "", text)
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\s\.\,\؟\?\!\؛\:]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_sentences(text):
    sentences = re.split(r"[\.؟\?\!\؛]\s*", text)
    return [s.strip() for s in sentences if len(s.strip()) > 3]

def tokenize(sentence):
    return sentence.split()

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def process_text(text):
    normalized_text = normalize_arabic(text)
    sentences = split_sentences(normalized_text)

    processed = []

    for idx, sentence in enumerate(sentences, start=1):
        tokens = tokenize(sentence)
        filtered_tokens = remove_stopwords(tokens)

        processed.append({
            "sentence_id": idx,
            "sentence": sentence,
            "tokens": tokens,
            "filtered_tokens": filtered_tokens
        })

    return {
        "normalized_text": normalized_text,
        "sentences_count": len(sentences),
        "processed_sentences": processed
    }

for file in INPUT_DIR.glob("*.txt"):
    print(f"Processing NLP: {file.name}")

    text = file.read_text(encoding="utf-8")
    result = process_text(text)

    output_file = OUTPUT_DIR / f"{file.stem}_nlp.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved: {output_file}")

print("NLP preprocessing completed.")
