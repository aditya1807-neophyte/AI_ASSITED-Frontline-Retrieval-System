import sys
sys.path.insert(0, ".")
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(users)"))
    cols = result.fetchall()
    print("Users columns:", [c[1] for c in cols])
