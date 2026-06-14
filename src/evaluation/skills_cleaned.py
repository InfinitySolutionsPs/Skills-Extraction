!pip install pandas rapidfuzz -q

import pandas as pd
import re
from rapidfuzz import fuzz
from google.colab import files

guide_df = pd.read_csv("guide_extracted_skills.csv")
video_df = pd.read_csv("video_extracted_skills (1).csv")

guide_lesson_col = "lesson_title"
guide_skill_col  = "guide_skill"

video_lesson_col = "lesson_title"
video_skill_col  = "skill"

def normalize_ar(text):
    text = str(text)
    text = re.sub(r'[إأآاٱ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_skills(text):
    text = str(text)
    parts = re.split(r'،|,|؛|;|\n| و(?=أن )| و(?=\w)', text)
    parts = [p.strip() for p in parts if len(p.strip()) >= 8]
    return parts

def clean_skill_text(text):
    text = str(text).strip()
    text = re.sub(r'^(أن\s+)?', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

guide_rows = []

for _, row in guide_df.iterrows():
    lesson = row[guide_lesson_col]
    skill_text = row[guide_skill_col]

    for skill in split_skills(skill_text):
        skill = clean_skill_text(skill)
        guide_rows.append({
            "lesson_title": lesson,
            "skill": skill,
            "skill_norm": normalize_ar(skill)
        })

guide_clean = pd.DataFrame(guide_rows)

guide_clean = guide_clean.drop_duplicates(
    subset=["lesson_title", "skill_norm"]
).reset_index(drop=True)

guide_clean.to_csv("guide_skills_cleaned.csv", index=False, encoding="utf-8-sig")
files.download("guide_skills_cleaned.csv")

guide_clean.shape

video_rows = []

for _, row in video_df.iterrows():
    lesson = row[video_lesson_col]
    skill_text = row[video_skill_col]

    for skill in split_skills(skill_text):
        skill = clean_skill_text(skill)
        video_rows.append({
            "lesson_title": lesson,
            "skill": skill,
            "skill_norm": normalize_ar(skill)
        })

video_clean = pd.DataFrame(video_rows)

video_clean = video_clean.drop_duplicates(
    subset=["lesson_title", "skill_norm"]
).reset_index(drop=True)

video_clean.to_csv("video_skills_cleaned.csv", index=False, encoding="utf-8-sig")
files.download("video_skills_cleaned.csv")

video_clean.shape

comparison_rows = []
threshold = 75

for lesson in guide_clean["lesson_title"].dropna().unique():

    guide_lesson = guide_clean[guide_clean["lesson_title"] == lesson]
    video_lesson = video_clean[video_clean["lesson_title"].apply(normalize_ar) == normalize_ar(lesson)]

    for _, g in guide_lesson.iterrows():

        best_score = 0
        best_video_skill = None

        for _, v in video_lesson.iterrows():
            score = fuzz.token_set_ratio(g["skill_norm"], v["skill_norm"])

            if score > best_score:
                best_score = score
                best_video_skill = v["skill"]

        comparison_rows.append({
            "lesson_title": lesson,
            "guide_skill": g["skill"],
            "best_video_skill_match": best_video_skill,
            "similarity_score": best_score,
            "matched": best_score >= threshold
        })

comparison_df = pd.DataFrame(comparison_rows)

comparison_df.to_csv("skills_comparison_after_cleaning.csv", index=False, encoding="utf-8-sig")
files.download("skills_comparison_after_cleaning.csv")

comparison_df.head()

lesson_accuracy = comparison_df.groupby("lesson_title").agg(
    guide_skills_count=("guide_skill", "count"),
    matched_skills_count=("matched", "sum"),
    average_similarity=("similarity_score", "mean")
).reset_index()

lesson_accuracy["coverage_accuracy"] = (
    lesson_accuracy["matched_skills_count"] / lesson_accuracy["guide_skills_count"]
) * 100

lesson_accuracy.to_csv("lesson_skill_accuracy_after_cleaning.csv", index=False, encoding="utf-8-sig")
files.download("lesson_skill_accuracy_after_cleaning.csv")

lesson_accuracy

