# scripts/export_cleaned_data.py
# Manages PostgreSQL workflow: imports youtube_melic_techno_analysis.csv, cleans data, runs analysis queries, and exports to youtube_melic_techno_cleaned.csv
# Requires: .env file with DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
import unicodedata

# Load environment variables from .env
load_dotenv()

# Database connection parameters
db_params = {
    "dbname": os.getenv("DB_NAME"),  
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

# Validate required parameters
required_params = ["dbname", "user", "password"]
missing_params = [param for param, value in db_params.items() if param in required_params and not value]
if missing_params:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_params)}")

# Input and output paths
input_csv = "data/youtube_melic_techno_analysis.csv"
output_csv = "data/youtube_melic_techno_cleaned.csv"
temp_csv = "data/youtube_melic_techno_analysis_temp.csv"  # Temporary cleaned CSV

# Function to clean CSV of non-UTF-8 characters
def clean_csv(input_path, output_path):
    print(f"Cleaning {input_path} to remove non-UTF-8 characters...")
    with open(input_path, 'r', encoding='utf-8', errors='replace') as infile:
        lines = infile.readlines()
    # Normalize Unicode characters (e.g., Ü → U)
    cleaned_lines = [unicodedata.normalize('NFKD', line).encode('ascii', 'ignore').decode('ascii') for line in lines]
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.writelines(cleaned_lines)
    print(f"Cleaned CSV saved to {output_path}")

# Initialize connections
admin_conn = None
conn = None
try:
    # Connect to PostgreSQL server (admin connection to create database)
    print(f"Connecting to PostgreSQL server at {db_params['host']}:{db_params['port']}")
    admin_conn = psycopg2.connect(
        dbname="postgres",  # Connect to default database
        user=db_params["user"],
        password=db_params["password"],
        host=db_params["host"],
        port=db_params["port"]
    )
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    admin_cursor = admin_conn.cursor()

    # Create tracks database if it doesn't exist
    admin_cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_params["dbname"],))
    if not admin_cursor.fetchone():
        print(f"Creating database: {db_params['dbname']}")
        admin_cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_params["dbname"])))
    
    admin_cursor.close()
    admin_conn.close()

    # Connect to tracks database
    print(f"Connecting to database: {db_params['dbname']}")
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Create tracks table with Mood column only
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tracks (
        name VARCHAR(255),
        artist VARCHAR(255),
        file VARCHAR(255),
        tempo FLOAT,
        energy FLOAT,
        danceability FLOAT,
        valence_proxy FLOAT,
        mood VARCHAR(50)
    );
    """
    cursor.execute(create_table_query)

    # Clean the CSV to handle non-UTF-8 characters
    clean_csv(input_csv, temp_csv)

    # Debug: Print first few lines of cleaned CSV
    print(f"Previewing first few lines of {temp_csv}")
    with open(temp_csv, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i <= 5:  # Show first 5 lines
                print(f"Line {i}: {line.strip()}")
            else:
                break

    # Load the CSV into a DataFrame and normalize column names to lowercase
    print(f"Loading {temp_csv} into DataFrame...")
    df = pd.read_csv(temp_csv, encoding='utf-8')
    # Convert column names to lowercase to match table schema
    df.columns = df.columns.str.lower()

    # Try importing with copy_expert
    print(f"Attempting to import data from {temp_csv}")
    try:
        # Save the modified DataFrame back to temp_csv with lowercase column names
        df.to_csv(temp_csv, index=False, encoding='utf-8')
        with open(temp_csv, 'r', encoding='utf-8') as f:
            cursor.copy_expert("COPY tracks FROM STDIN WITH CSV HEADER DELIMITER ','", f)
    except psycopg2.Error as e:
        print(f"copy_expert failed: {e}")
        print("Falling back to pandas.to_sql import...")
        # Fallback to pandas.to_sql (columns are already lowercase)
        engine = create_engine(f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")
        df.to_sql('tracks', engine, if_exists='append', index=False)
        print("Data imported using pandas.to_sql")

    # Cleaning queries
    cleaning_queries = [
        # Remove duplicates
        """
        DELETE FROM tracks 
        WHERE ctid NOT IN (
            SELECT MIN(ctid) 
            FROM tracks 
            GROUP BY name, artist
        );
        """,
        # Handle missing values (using dataset means and defaults for Mood)
        """
        UPDATE tracks 
        SET 
            tempo = 125, 
            energy = 0.347, 
            danceability = 0.560, 
            valence_proxy = 0.735,
            mood = 'Neutral'  -- Default mood
        WHERE 
            tempo IS NULL OR 
            energy IS NULL OR 
            danceability IS NULL OR 
            valence_proxy IS NULL OR 
            mood IS NULL;
        """,
        # Fix tempo range
        """
        UPDATE tracks 
        SET tempo = CASE 
            WHEN tempo < 110 THEN 110 
            WHEN tempo > 140 THEN 140 
            ELSE tempo 
        END;
        """,
        # Ensure Mood values are valid
        """
        UPDATE tracks 
        SET mood = 'Neutral'
        WHERE mood NOT IN ('Happy', 'Neutral', 'Energetic', 'Calm');
        """
    ]
    print("Cleaning data...")
    for query in cleaning_queries:
        cursor.execute(query)

    # Analysis queries (updated to remove Cluster references)
    analysis_queries = {
        "Q1_Averages": """
        SELECT 
            ROUND(AVG(tempo)::numeric, 1) AS avg_tempo,
            ROUND(AVG(energy)::numeric, 3) AS avg_energy,
            ROUND(AVG(danceability)::numeric, 3) AS avg_danceability,
            ROUND(AVG(valence_proxy)::numeric, 3) AS avg_valence
        FROM tracks;
        """,
        "Q2_Bangers_By_Mood": """
        SELECT 
            name, 
            artist, 
            tempo, 
            energy, 
            danceability, 
            valence_proxy, 
            mood
        FROM tracks
        WHERE energy > 0.347 AND danceability > 0.560
        ORDER BY energy DESC, danceability DESC
        LIMIT 5;
        """,
        "Q3_Tempo_vs_Danceability": """
        SELECT 
            ROUND(tempo::numeric) AS tempo_bucket,
            COUNT(*) AS track_count,
            ROUND(AVG(danceability)::numeric, 3) AS avg_danceability,
            STRING_AGG(mood, ', ') AS moods
        FROM tracks
        GROUP BY ROUND(tempo::numeric)
        ORDER BY tempo_bucket;
        """,
        "Q4_Top_Artists": """
        SELECT 
            artist,
            COUNT(*) AS track_count,
            ROUND(AVG(energy)::numeric, 3) AS avg_energy,
            STRING_AGG(DISTINCT mood, ', ') AS moods
        FROM tracks
        WHERE energy > 0.347
        GROUP BY artist
        ORDER BY avg_energy DESC
        LIMIT 5;
        """,
        "Q5_Tempo_Distribution": """
        SELECT 
            CASE 
                WHEN tempo <= 122 THEN 'Slow (110-122)'
                WHEN tempo <= 126 THEN 'Mid (123-126)'
                ELSE 'Fast (127-140)'
            END AS tempo_range,
            COUNT(*) AS track_count,
            ROUND(AVG(energy)::numeric, 3) AS avg_energy,
            STRING_AGG(DISTINCT mood, ', ') AS moods
        FROM tracks
        GROUP BY tempo_range
        ORDER BY tempo_range;
        """,
        "Q6_Outliers": """
        SELECT 
            name, 
            artist, 
            tempo, 
            energy, 
            danceability, 
            valence_proxy, 
            mood
        FROM tracks
        WHERE 
            energy > (SELECT AVG(energy) + 2 * STDDEV(energy) FROM tracks)
            OR danceability > (SELECT AVG(danceability) + 2 * STDDEV(danceability) FROM tracks)
        LIMIT 5;
        """,
        "Q7_Mood_Distribution": """
        SELECT 
            mood,
            COUNT(*) AS track_count,
            ROUND(AVG(energy)::numeric, 3) AS avg_energy,
            ROUND(AVG(danceability)::numeric, 3) AS avg_danceability,
            ROUND(AVG(valence_proxy)::numeric, 3) AS avg_valence
        FROM tracks
        GROUP BY mood
        ORDER BY track_count DESC;
        """
    }

    print("Running analysis queries...")
    analysis_results = {}
    for name, query in analysis_queries.items():
        try:
            cursor.execute(query)
            analysis_results[name] = cursor.fetchall()
            print(f"{name}: {analysis_results[name]}")
        except psycopg2.Error as e:
            print(f"Error in query {name}: {e}")
            conn.rollback()  # Roll back to continue with other queries

    # Commit all changes
    conn.commit()

    # Export cleaned data to CSV
    print(f"Exporting cleaned data to {output_csv}")
    query = "SELECT * FROM tracks;"
    df = pd.read_sql(query, conn)
    df.to_csv(output_csv, index=False, sep=",", header=True)
    print(f"Exported {len(df)} rows to {output_csv}")

except psycopg2.Error as e:
    print(f"Database error: {e}")
except FileNotFoundError:
    print(f"Error: Input file {input_csv} not found")
except UnicodeEncodeError as e:
    print(f"Unicode encoding error: {e}")
    print("Try manually cleaning the CSV with scripts/clean_csv.py.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn is not None:
        conn.close()
        print("Tracks database connection closed.")
    if admin_conn is not None:
        admin_conn.close()
        print("Admin database connection closed.")
    # Clean up temporary CSV
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
        print(f"Removed temporary file {temp_csv}")