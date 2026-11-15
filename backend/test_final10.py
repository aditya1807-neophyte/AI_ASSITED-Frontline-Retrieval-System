
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine

# Delete the database file directly
import os
db_path = "data/frontline.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print("Deleted existing database file")

# Create all tables
from sqlalchemy import inspect
inspector = inspect(engine)
print("Tables before creation:", inspector.get_table_names())

Base.metadata.create_all(bind=engine)

print("After creation - tables:", inspector.get_table_names())
