import pandas as pd
import re

# Keywords to detect symptom words
SYMPTOM_KEYWORDS = [
    "pain", "headache", "anxiety", "insomnia", "indigestion", "cold",
    "stress", "nervousness", "allergies", "fatigue", "detox",
    "sore throat", "joint pain", "inflammation", "nausea", "digestion",
    "liver support", "heart palpitations", "hypertension"
]

# Herb preparation method keywords
FORM_KEYWORDS = [
    "dried", "fresh", "fresh root", "root", "tea", "tincture",
    "capsules", "extract", "powder", "leaf", "berries", "seeds",
    "essential oil"
]

def is_symptom(value):
    value = str(value).lower()
    return any(word in value for word in SYMPTOM_KEYWORDS)

def is_form(value):
    value = str(value).lower()
    return any(word in value for word in FORM_KEYWORDS)

def try_float(x):
    try: return float(x)
    except: return None

# Load messy sheet
df = pd.read_csv("data/raw_herbs.csv")

clean_rows = []

for _, row in df.iterrows():
    common = row[0]
    latin = row[1]

    forms = []
    symptoms = []
    toxicity_notes = []

    availability = None
    cost = None
    popularity = None
    toxicity_flag = 0
    toxicity_level = "low"

    # Loop through each cell in the row after latin name
    for cell in row[2:]:
        cell_str = str(cell).strip()

        # Skip blanks
        if cell_str == "" or cell_str.lower() == "nan":
            continue

        # 1. check if it's a form
        if is_form(cell_str):
            forms.append(cell_str)
            continue

        # 2. check if it's a symptom
        if is_symptom(cell_str):
            symptoms.append(cell_str)
            continue

        # 3. check if it's a number (score)
        num = try_float(cell_str)
        if num is not None:
            if availability is None: availability = num
            elif cost is None: cost = num
            elif popularity is None: popularity = num
            else:
                pass
            continue

        # 4. check toxicity level
        if cell_str.lower() in ["low", "medium", "high"]:
            toxicity_level = cell_str
            continue

        # 5. everything else = toxicity notes
        toxicity_notes.append(cell_str)

    clean_rows.append({
        "common_name": common,
        "latin_name": latin,
        "forms": "; ".join(forms),
        "uses": "; ".join(symptoms),
        "availability_score": availability,
        "cost_score": cost,
        "popularity_score": popularity,
        "toxicity_flag": 1 if toxicity_level != "low" else 0,
        "toxicity_level": toxicity_level,
        "toxicity_notes": " ".join(toxicity_notes)
    })

clean_df = pd.DataFrame(clean_rows)
clean_df.to_csv("data/raw_herbs_clean.csv", index=False)

print("🌿 Cleaned dataset created: data/raw_herbs_clean.csv")
