# Herbal Symptom Recommender – Technical Summary

## 1. Objective
To build a data-driven system that recommends herbs for specific symptoms using a scoring model
(potency, cost, availability, and popularity).

## 2. Data Model
- `raw_herbs.csv`: list of herbs with core attributes.
- `symptoms.csv`: list of symptoms.
- `herb_symptom.csv`: mapping table between herbs and symptoms with scores.

## 3. Implementation
- Python script reads the CSVs / database.
- Scores are combined into a single ranking value.
- The top-scoring herb is shown as the main recommendation.
- Additional herbs are shown as secondary options.

## 4. Sample Use Case
Symptom: **insomnia**

Output:
- Best herb: (example) **Valerian Root**
- Alternatives: Passionflower, Skullcap, Chamomile

## 5. Lessons Learned
- Importance of clean data for accurate recommendations.
- How scoring weights change the final ranking.
- How tech can support traditional/ancestral herbal knowledge.

## 6. Future Work
- Add toxicity / contraindications.
- Build a simple web UI for non-technical users.
- Explore ML models for ranking instead of manual scores.
