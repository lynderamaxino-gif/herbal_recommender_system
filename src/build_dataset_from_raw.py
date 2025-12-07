import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

RAW_PATH = os.path.join(DATA_DIR, "raw_herbs.csv")
HERBS_PATH = os.path.join(DATA_DIR, "herbs.csv")
SYMPTOMS_PATH = os.path.join(DATA_DIR, "symptoms.csv")
EFFECTS_PATH = os.path.join(DATA_DIR, "herb_symptom_effects.csv")

def main():
    df_raw = pd.read_csv(RAW_PATH)

    # 1. Give each herb an ID
    df_raw = df_raw.copy()
    df_raw["herb_id"] = range(1, len(df_raw) + 1)

    herbs_cols = [
        "herb_id",
        "common_name",
        "latin_name",
        "toxicity_flag",
        "toxicity_level",
        "availability_score",
        "cost_score",
        "popularity_score",
        "toxicity_notes",
    ]
    df_herbs = df_raw[herbs_cols]
    df_herbs.to_csv(HERBS_PATH, index=False)

    # 2. Build unique symptom list
    all_symptoms = set()
    for uses in df_raw["uses"].fillna(""):
        for s in str(uses).split(";"):
            name = s.strip()
            if name:
                all_symptoms.add(name)

    symptom_list = sorted(all_symptoms)
    df_symptoms = pd.DataFrame({
        "symptom_id": range(1, len(symptom_list) + 1),
        "name": symptom_list,
        "description": ["" for _ in symptom_list],
    })
    df_symptoms.to_csv(SYMPTOMS_PATH, index=False)

    # Map name -> id
    symptom_to_id = {
        row["name"]: row["symptom_id"]
        for _, row in df_symptoms.iterrows()
    }

    # 3. Build herb_symptom_effects
    rows = []
    for _, herb in df_raw.iterrows():
        herb_id = herb["herb_id"]
        uses = str(herb["uses"])
        for s in uses.split(";"):
            name = s.strip()
            if not name:
                continue
            symptom_id = symptom_to_id.get(name)
            if symptom_id is None:
                continue

            row = {
                "herb_id": herb_id,
                "symptom_id": symptom_id,
                "potency_score": 0.6,       # defaults for now
                "evidence_level": 0.5,      # tweak later or add to raw_herbs.csv
                "dosage_min": 1.0,
                "dosage_max": 3.0,
                "unit": "generic_units",
            }
            rows.append(row)

    df_effects = pd.DataFrame(rows)
    df_effects.to_csv(EFFECTS_PATH, index=False)

    print("✅ Built herbs.csv, symptoms.csv, herb_symptom_effects.csv from raw_herbs.csv")

if __name__ == "__main__":
    main()
