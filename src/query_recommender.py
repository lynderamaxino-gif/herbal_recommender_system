import duckdb
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "herbs.duckdb")


def get_connection():
    return duckdb.connect(DB_PATH)


def get_symptom_id(con, symptom_name: str):
    row = con.execute(
        """
        SELECT symptom_id, name
        FROM symptoms
        WHERE lower(name) = lower(?)
        """,
        [symptom_name],
    ).fetchone()
    return row  # (symptom_id, name) or None


def top_herbs_for_symptom(con, symptom_id: int, limit: int = 3):
    """
    Return the top N herbs for this symptom, ranked by therapeutic_score.
    """
    query = """
    WITH scored AS (
        SELECT
            h.common_name,
            h.latin_name,
            e.potency_score,
            e.evidence_level,
            h.toxicity_flag,
            h.toxicity_level,
            h.toxicity_notes,
            (0.7 * e.potency_score + 0.3 * e.evidence_level) AS therapeutic_score
        FROM herb_symptom_effects e
        JOIN herbs h USING (herb_id)
        WHERE e.symptom_id = ?
    )
    SELECT *
    FROM scored
    ORDER BY therapeutic_score DESC
    LIMIT ?;
    """
    return con.execute(query, [symptom_id, limit]).fetchall()


def most_available_herb_for_symptom(con, symptom_id: int):
    """
    Herb that is easiest to obtain (availability + popularity + cost).
    """
    query = """
    WITH by_availability AS (
      SELECT
        h.common_name,
        h.latin_name,
        h.availability_score,
        h.popularity_score,
        h.cost_score,
        h.toxicity_flag,
        h.toxicity_level,
        h.toxicity_notes,
        (0.5 * h.availability_score
         + 0.3 * h.popularity_score
         + 0.2 * (1 - h.cost_score)) AS availability_rank
      FROM herb_symptom_effects e
      JOIN herbs h USING (herb_id)
      WHERE e.symptom_id = ?
    )
    SELECT *
    FROM by_availability
    ORDER BY availability_rank DESC
    LIMIT 1;
    """
    return con.execute(query, [symptom_id]).fetchone()


def print_top_herbs(best_list, proper_name: str):
    if not best_list:
        print("No potency data found for this symptom.")
        return

    print("Top therapeutic options:\n")

    for idx, row in enumerate(best_list, start=1):
        (
            name,
            latin,
            potency,
            evidence,
            tox_flag,
            tox_level,
            tox_notes,
            therapeutic_score,
        ) = row

        print(f"#{idx}: {name} ({latin})")
        print(f"  Potency score: {potency}, Evidence: {evidence}")
        print(f"  Combined therapeutic score: {therapeutic_score:.2f}")

        if tox_flag:
            print(f"  ⚠ Toxicity level: {tox_level}")
            if tox_notes:
                print(f"  ⚠ Notes: {tox_notes}")

        print("  Explanation:")
        print(f"  - Commonly used for {proper_name}.")
        print(
            f"  - Ranks #{idx} based on potency ({potency}) and evidence ({evidence})."
        )
        if idx == 1:
            print("  - This is the primary / strongest recommendation.")
        else:
            print("  - This is a follow-up / alternative option.")
        print()  # blank line between herbs


def print_availability_option(avail):
    if not avail:
        print("No availability data found.")
        return

    (
        name,
        latin,
        availability,
        popularity,
        cost,
        tox_flag,
        tox_level,
        tox_notes,
        availability_rank,
    ) = avail

    print("Most common / readily available option:")
    print(f"  {name} ({latin})")
    print(f"  Availability score: {availability}")
    print(f"  Popularity score: {popularity}")
    print(f"  Cost score (lower is cheaper): {cost}")
    print(f"  Combined availability rank: {availability_rank:.2f}")

    if tox_flag:
        print(f"  ⚠ Toxicity level: {tox_level}")
        if tox_notes:
            print(f"  ⚠ Notes: {tox_notes}")

    print("\nExplanation:")
    print("- This herb is chosen as the most accessible option.")
    print(f"- It scores well for availability ({availability}) and popularity ({popularity}).")
    if cost is not None and cost <= 0.4:
        print("- It is also relatively affordable compared to other options.")
    if tox_flag:
        print(f"- Toxicity is {tox_level}: {tox_notes}")


def main(symptom_name: str):
    con = get_connection()
    row = get_symptom_id(con, symptom_name)
    if row is None:
        print(f"No symptom found matching: {symptom_name}")
        return
    symptom_id, proper_name = row

    # 🔹 Get top 3 herbs instead of just one
    best_list = top_herbs_for_symptom(con, symptom_id, limit=3)
    avail = most_available_herb_for_symptom(con, symptom_id)

    print(f"Symptom: {proper_name}\n")

    print_top_herbs(best_list, proper_name)
    print()
    print_availability_option(avail)

    print("\n⚠️ This is an educational tool only, not medical advice.")
    print("⚠️ Always consult a qualified healthcare professional before using herbs.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/query_recommender.py <symptom_name>")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))

