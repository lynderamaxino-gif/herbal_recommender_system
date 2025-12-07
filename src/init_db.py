import duckdb
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database location: ~/herbal_recommender/herbs.duckdb
DB_PATH = os.path.join(BASE_DIR, "herbs.duckdb")

# Data folder and schema folder
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

def main():
    # Connect to DuckDB (creates file if it doesn't exist)
    con = duckdb.connect(DB_PATH)

    # Read schema.sql
    schema_path = os.path.join(CONFIG_DIR, "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    # Remove old tables if they exist
    con.execute("DROP TABLE IF EXISTS herb_symptom_effects")
    con.execute("DROP TABLE IF EXISTS herbs")
    con.execute("DROP TABLE IF EXISTS symptoms")

    # Create tables fresh
    con.execute(schema_sql)

    # Load CSV files into the tables
    herbs_csv = os.path.join(DATA_DIR, "herbs.csv")
    symptoms_csv = os.path.join(DATA_DIR, "symptoms.csv")
    effects_csv = os.path.join(DATA_DIR, "herb_symptom_effects.csv")

    con.execute(f"""
        COPY herbs FROM '{herbs_csv}' (HEADER, AUTO_DETECT TRUE);
    """)
    con.execute(f"""
        COPY symptoms FROM '{symptoms_csv}' (HEADER, AUTO_DETECT TRUE);
    """)
    con.execute(f"""
        COPY herb_symptom_effects FROM '{effects_csv}' (HEADER, AUTO_DETECT TRUE);
    """)

    print("🌿 Herbal database created successfully!")
    print("Database file located at:", DB_PATH)

if __name__ == "__main__":
    main()
