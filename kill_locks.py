import psycopg2
from dotenv import load_dotenv
import os

load_dotenv('pipeline/.env')
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Kill all idle in transaction queries or blocking queries
cur.execute("""
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction' OR wait_event_type = 'Lock';
""")
conn.commit()

print("Killed blocking processes.")

cur.execute('SELECT COUNT(*) FROM "Hackathon"')
print(f"Total Hackathons: {cur.fetchone()[0]}")

conn.close()
