import sqlite3
import json
import sys

if len(sys.argv) < 3:
    print("Usage: python db_writer.py <json_file> <table_name>")
    sys.exit(1)

json_filename = sys.argv[1]
table_name = sys.argv[2]

with open(f'{json_filename}', 'r', encoding='utf-8') as f:
    data = json.load(f)

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS ')

cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position TEXT,
        position_url TEXT UNIQUE,
        company TEXT,
        company_url TEXT,
        published_date TEXT,
        end_date TEXT
    )
''')

added_jobs = 0

for job in data:
    cursor.execute(f'''
        INSERT OR IGNORE INTO {table_name}
        (position, position_url, company, company_url, published_date, end_date)
        VALUES(?,?,?,?,?,?)
        ''', (
        job["position"],
        job["position_url"],
        job['company'],
        job['company_url'],
        job['published_date'],
        job['end_date'],
    ))
    if cursor.rowcount:
        added_jobs += 1

conn.commit()
conn.close()

print(f"added {added_jobs} jobs")