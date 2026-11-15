import sqlite3
import sys

db_path = sys.argv[1]
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name")
tables = cursor.fetchall()
print("Tables in database:")
for t in tables:
    print("  " + t[0])
conn.close()
