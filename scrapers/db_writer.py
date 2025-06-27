import sqlite3
import json

def insert_jobs_to_db(json_filename, table_name, log_callback=print):
    with open(f'{json_filename}', 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect("main.db")
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

    log_callback(f"Added {added_jobs} new jobs to {table_name}.")