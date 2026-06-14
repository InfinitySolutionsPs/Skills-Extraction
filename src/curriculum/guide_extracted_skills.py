
!pip install pandas rapidfuzz -q
import pandas as pd
import re
from rapidfuzz import fuzz
from google.colab import files

uploaded = files.upload()

guide_pages = pd.read_csv("teacher_guide_detected_pages (1).csv")
video_skills = pd.read_csv("video_extracted_skills (1).csv")

guide_pages.head(), video_skills.head()

def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_ar(text):
    text = str(text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_skills_from_text(text):
    text = clean_text(text)

    skill_patterns = [
        r"أن\s+يقرأ\s+الطالب[^.،\n]*",
        r"أن\s+يكتب\s+الطالب[^.،\n]*",
        r"أن\s+يمثل\s+الطالب[^.،\n]*",
        r"أن\s+يتعرف\s+الطالب[^.،\n]*",
        r"أن\s+يذكر\s+الطالب[^.،\n]*",
        r"أن\s+يقارن\s+الطالب[^.،\n]*",
        r"أن\s+يرتب\s+الطالب[^.،\n]*",
        r"أن\s+يقرب\s+الطالب[^.،\n]*",
        r"قراءة\s+[^.،\n]*",
        r"كتابة\s+[^.،\n]*",
        r"تمثيل\s+[^.،\n]*"
    ]

    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text)
        skills.extend(matches)

    skills = [clean_text(s) for s in skills if len(clean_text(s)) > 10]
    skills = list(dict.fromkeys(skills))

    return skills

guide_skills_rows = []

for _, row in guide_pages.iterrows():
    lesson = row["lesson_title"]
    page = row["page_number"]
    text = row.get("page_preview", "")

    skills = extract_skills_from_text(text)

    for skill in skills:
        guide_skills_rows.append({
            "lesson_title": lesson,
            "page_number": page,
            "guide_skill": skill,
            "guide_skill_norm": normalize_ar(skill)
        })

guide_skills_df = pd.DataFrame(guide_skills_rows)

guide_skills_df.to_csv("guide_extracted_skills.csv", index=False, encoding="utf-8-sig")
files.download("guide_extracted_skills.csv")

guide_skills_df.head()

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

guide_df["lesson_norm"] = guide_df[guide_lesson_col].apply(normalize_ar)
guide_df["skill_norm"] = guide_df[guide_skill_col].apply(normalize_ar)

video_df["lesson_norm"] = video_df[video_lesson_col].apply(normalize_ar)
video_df["skill_norm"] = video_df[video_skill_col].apply(normalize_ar)

comparison_rows = []
threshold = 75

for lesson_norm in guide_df["lesson_norm"].dropna().unique():

    guide_lesson = guide_df[guide_df["lesson_norm"] == lesson_norm]
    video_lesson = video_df[video_df["lesson_norm"] == lesson_norm]

    lesson_title = guide_lesson[guide_lesson_col].iloc[0]

    for _, g in guide_lesson.iterrows():

        best_score = 0
        best_video_skill = None

        for _, v in video_lesson.iterrows():
            score = fuzz.token_set_ratio(g["skill_norm"], v["skill_norm"])

            if score > best_score:
                best_score = score
                best_video_skill = v[video_skill_col]

        comparison_rows.append({
            "lesson_title": lesson_title,
            "guide_skill": g[guide_skill_col],
            "best_video_skill_match": best_video_skill,
            "similarity_score": best_score,
            "matched": best_score >= threshold
        })

comparison_df = pd.DataFrame(comparison_rows)

comparison_df.to_csv("skills_comparison_results.csv", index=False, encoding="utf-8-sig")
files.download("skills_comparison_results.csv")

comparison_df.head()

