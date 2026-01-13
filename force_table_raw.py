import os
import psycopg2
from urllib.parse import urlparse

# Get Config from the same place the app gets it
from config import Config

uri = Config.SQLALCHEMY_DATABASE_URI
print(f"Target DB: {uri}")

try:
    result = urlparse(uri)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Connected to DB via Psycopg2 directly.")
    
    # 1. Check if table exists
    cursor.execute("SELECT to_regclass('public.lost_item');")
    exists = cursor.fetchone()[0]
    
    if exists:
        print("Table 'lost_item' ALREADY EXISTS.")
        # Check columns
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'lost_item';")
        cols = cursor.fetchall()
        print(f"Columns found: {[c[0] for c in cols]}")
    else:
        print("Table 'lost_item' MISSING. Creating now...")
        create_sql = """
        CREATE TABLE IF NOT EXISTS lost_item (
            id SERIAL PRIMARY KEY,
            description VARCHAR(200) NOT NULL,
            location_found VARCHAR(100),
            found_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
            image_filename VARCHAR(255),
            status VARCHAR(20) DEFAULT 'unclaimed',
            found_by_id INTEGER REFERENCES "user"(id),
            claimed_by_id INTEGER REFERENCES "user"(id),
            claimed_at TIMESTAMP WITHOUT TIME ZONE,
            condo_id INTEGER REFERENCES condominium(id)
        );
        """
        cursor.execute(create_sql)
        print("Table 'lost_item' CREATED via Raw SQL.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
