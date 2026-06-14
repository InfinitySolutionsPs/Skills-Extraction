!pip install -q google-generativeai pandas tqdm

import pandas as pd
import google.generativeai as genai
from tqdm import tqdm
import json
import time
import re

# =========================
# 1. إعداد Gemini API
# =========================

GEMINI_API_KEY = "AQ.Ab8RN6J7Ih_DglGm5eAu0m_MoGVFJATMLvlFPBaRpd7Gdv_9VQ"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# 2. تحميل الملفات
# =========================

video_df = pd.read_csv("/content/video_extracted_skills.csv")
guide_df = pd.read_csv("/content/guide_extracted_skills.csv")

# =========================
# 3. أسماء الأعمدة
# =========================

VIDEO_LESSON_COL = "lesson_title"
VIDEO_SKILL_COL = "skill"
VIDEO_CONCEPT_COL = "concept"
VIDEO_OBJECTIVE_COL = "learning_objective"

GUIDE_LESSON_COL = "lesson_title"
GUIDE_SKILL_COL = "guide_skill"

# =========================
# 4. تنظيف بسيط للنصوص
# =========================

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text

video_df[VIDEO_LESSON_COL] = video_df[VIDEO_LESSON_COL].apply(clean_text)
video_df[VIDEO_SKILL_COL] = video_df[VIDEO_SKILL_COL].apply(clean_text)
video_df[VIDEO_CONCEPT_COL] = video_df[VIDEO_CONCEPT_COL].apply(clean_text)
video_df[VIDEO_OBJECTIVE_COL] = video_df[VIDEO_OBJECTIVE_COL].apply(clean_text)

guide_df[GUIDE_LESSON_COL] = guide_df[GUIDE_LESSON_COL].apply(clean_text)
guide_df[GUIDE_SKILL_COL] = guide_df[GUIDE_SKILL_COL].apply(clean_text)

# =========================
# 5. دالة استخراج JSON
# =========================

def extract_json(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {
        "match_status": "Parsing Error",
        "best_video_skill": "",
        "confidence": 0.0,
        "reason": text
    }

# =========================
# 6. دالة المقارنة بالذكاء الاصطناعي
# =========================

def ai_compare_skill(guide_skill, video_items):
    video_text = "\n\n".join(video_items)

    prompt = f"""
أنت خبير في تحليل مهارات الرياضيات للصف الثالث الأساسي ومقارنتها بدليل المعلم.

المهمة:
قارن مهارة دليل المعلم مع المهارات والمفاهيم والأهداف التعليمية المستخرجة من الفيديو.

مهارة دليل المعلم:
{guide_skill}

المحتوى المستخرج من الفيديو:
{video_text}

صنّف النتيجة إلى واحدة فقط من القيم التالية:

Exact Match
Semantic Match
Covered by General Skill
Covered by Learning Objective
Partial Match
Missing

تعريفات مهمة:
- Exact Match: نفس المهارة تقريبًا مذكورة في الفيديو.
- Semantic Match: المهارة موجودة بمعنى مشابه حتى لو بصياغة مختلفة.
- Covered by General Skill: مهارة الفيديو عامة لكنها تغطي مهارة الدليل التفصيلية.
- Covered by Learning Objective: الهدف التعليمي في الفيديو يغطي مهارة الدليل حتى لو لم تُذكر كمهارة صريحة.
- Partial Match: الفيديو يغطي جزءًا من المهارة فقط.
- Missing: لا توجد تغطية واضحة للمهارة.

مهم جدًا:
إذا كانت مهارة الفيديو عامة مثل "قراءة الأعداد بشكل صحيح"
ومهارة الدليل تفصيلية مثل "قراءة الأعداد التي تحتوي على صفر"
فصنّفها Covered by General Skill.

أرجع JSON فقط بهذا الشكل:

{{
  "match_status": "",
  "best_video_skill": "",
  "confidence": 0.0,
  "reason": ""
}}
"""

    try:
        response = model.generate_content(prompt)
        return extract_json(response.text)
    except Exception as e:
        return {
            "match_status": "API Error",
            "best_video_skill": "",
            "confidence": 0.0,
            "reason": str(e)
        }

# =========================
# 7. تنفيذ المقارنة لكل درس
# =========================

results = []

lessons = guide_df[GUIDE_LESSON_COL].dropna().unique()

for lesson in tqdm(lessons):

    guide_skills = guide_df[
        guide_df[GUIDE_LESSON_COL] == lesson
    ][GUIDE_SKILL_COL].dropna().unique().tolist()

    lesson_video = video_df[
        video_df[VIDEO_LESSON_COL] == lesson
    ]

    video_items = []

    for _, row in lesson_video.iterrows():
        item = f"""
المهارة: {row[VIDEO_SKILL_COL]}
المفهوم: {row[VIDEO_CONCEPT_COL]}
الهدف التعليمي: {row[VIDEO_OBJECTIVE_COL]}
"""
        video_items.append(item)

    for guide_skill in guide_skills:

        if len(video_items) == 0:
            results.append({
                "lesson_title": lesson,
                "guide_skill": guide_skill,
                "best_video_skill": "",
                "match_status": "Missing",
                "confidence": 0.0,
                "reason": "No video skills found for this lesson"
            })
            continue

        ai_result = ai_compare_skill(guide_skill, video_items)

        results.append({
            "lesson_title": lesson,
            "guide_skill": guide_skill,
            "best_video_skill": ai_result.get("best_video_skill", ""),
            "match_status": ai_result.get("match_status", ""),
            "confidence": ai_result.get("confidence", 0.0),
            "reason": ai_result.get("reason", "")
        })

        time.sleep(1)

# =========================
# 8. حفظ نتائج المقارنة
# =========================

results_df = pd.DataFrame(results)

results_df.to_csv(
    "/content/ai_skill_alignment_results.csv",
    index=False,
    encoding="utf-8-sig"
)

results_df.head()

!pip install -q google-generativeai pandas tqdm

import pandas as pd
import google.generativeai as genai
from tqdm import tqdm
import json
import time
import re

GEMINI_API_KEY = "AQ.Ab8RN6LlAM50CeLBGotCQ5jjgL5AqkGHk07D2hY8m5hJM8j9SQ"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

video_df = pd.read_csv("/content/video_extracted_skills (1).csv")
guide_df = pd.read_csv("/content/guide_extracted_skills.csv")

def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text)
    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text

for col in video_df.columns:
    video_df[col] = video_df[col].astype(str).apply(clean_text)

for col in guide_df.columns:
    guide_df[col] = guide_df[col].astype(str).apply(clean_text)

def extract_json(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    match = re.search(r"\[.*\]", text, re.DOTALL)

    if match:
        text = match.group()

    return json.loads(text)

def compare_lesson(lesson_name,
                   guide_skills,
                   video_records):

    guide_text = "\n".join([
        f"{i+1}. {s}"
        for i, s in enumerate(guide_skills)
    ])

    video_text = ""

    for i, row in enumerate(video_records):

        video_text += f"""

المهارة {i+1}
المهارة: {row['skill']}
المفهوم: {row['concept']}
الهدف التعليمي: {row['learning_objective']}

"""

    prompt = f"""
أنت خبير مناهج رياضيات.

لدي مهارات من دليل المعلم
ومهارات ومفاهيم وأهداف تعليمية مستخرجة من فيديو شرح الدرس.

اسم الدرس:
{lesson_name}

======================

مهارات دليل المعلم:

{guide_text}

======================

المحتوى المستخرج من الفيديو:

{video_text}

======================

لكل مهارة من دليل المعلم حدد:

Exact Match
Semantic Match
Covered by General Skill
Covered by Learning Objective
Partial Match
Missing

أرجع JSON Array فقط بالشكل التالي:

[
 {{
   "guide_skill":"",
   "best_video_skill":"",
   "match_status":"",
   "confidence":0.95,
   "reason":""
 }}
]

بدون أي نص إضافي.
"""

    response = model.generate_content(prompt)

    return extract_json(response.text)

results = []

lessons = sorted(
    guide_df["lesson_title"].dropna().unique()
)

for lesson in tqdm(lessons):

    guide_skills = guide_df[
        guide_df["lesson_title"] == lesson
    ]["guide_skill"].dropna().tolist()

    lesson_video = video_df[
        video_df["lesson_title"] == lesson
    ]

    if len(guide_skills) == 0:
        continue

    if len(lesson_video) == 0:
        continue

    video_records = lesson_video[
        [
            "skill",
            "concept",
            "learning_objective"
        ]
    ].to_dict("records")

    try:

        lesson_results = compare_lesson(
            lesson,
            guide_skills,
            video_records
        )

        for item in lesson_results:

            item["lesson_title"] = lesson

            results.append(item)

        time.sleep(2)

    except Exception as e:

        print("Error:", lesson)

        print(e)