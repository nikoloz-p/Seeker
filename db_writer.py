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

cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position TEXT,
        position_url TEXT UNIQUE,
        company TEXT,
        company_url TEXT,
        published_date TEXT,
        end_date TEXT,
        date TEXT
    )
''')

added_jobs = 0

for job in data:
    cursor.execute(f'''
        INSERT OR IGNORE INTO {table_name}
        (position, position_url, company, company_url, published_date, end_date, date)
        VALUES(?,?,?,?,?,?,?)
        ''', (
        job.get("position"),
        job.get("position_url"),
        job.get('company'),
        job.get('company_url'),
        job.get('published_date'),
        job.get('end_date'),
        job.get('date'),
    ))
    if cursor.rowcount:
        added_jobs += 1

conn.commit()
conn.close()

print(f"added {added_jobs} jobs")