# test_connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

try:
    url = URL.create(
        "mysql+mysqlconnector",
        username="root",
        password="yourpass",
        host="127.0.0.1",
        port=3306,
        database="Homebase"
    )
    engine = create_engine(url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DATABASE()"))
        db = result.fetchone()[0]
        print(f"✓ Successfully connected to database: {db}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM Users"))
        count = result.fetchone()[0]
        print(f"✓ Found {count} users in the database")
        
except Exception as e:

    print(f"✗ Connection failed: {e}")

