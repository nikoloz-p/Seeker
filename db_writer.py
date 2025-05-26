import sqlite3
import json

with open('jobs_ge.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs_ge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position TEXT,
        position_url TEXT,
        company TEXT,
        company_url TEXT,
        published_date TEXT,
        end_date TEXT
    )
''')

for job in data:
    cursor.execute('''
        INSERT INTO jobs_ge(position, position_url, company, company_url, published_date, end_date)
        VALUES(?,?,?,?,?,?)
        ''', (
        job["position"],
        job["position_url"],
        job['company'],
        job['company_url'],
        job['published_date'],
        job['end_date'],
    ))

conn.commit()
conn.close()
print("Data inserted into jobs_ge table")