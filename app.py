import psycopg

import os
from dotenv import load_dotenv

load_dotenv()

# 1. Connect 🔌
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="swiggy",
    user="atharva",
    password=os.getenv("password")
)
cursor = conn.cursor()
print("PostgreSQL se connect ho gaye! 🐘✅")

# ✏️ UPDATE
cursor.execute(
    "UPDATE customers SET city = %s WHERE id = %s",
    ("Delhi", 1)
)
print(f"{cursor.rowcount} row update hui ✏️")

# 🗑️ DELETE
cursor.execute(
    "DELETE FROM customers WHERE id = %s",
    (3,)
)
print(f"{cursor.rowcount} row delete hui 🗑️")

conn.commit()   # 💾 data badla hai, toh commit zaroori!

# 📖 Check karo
cursor.execute("SELECT * FROM customers ORDER BY id")
for id, naam, city in cursor.fetchall():
    print(f"{id}. {naam} ({city})")

conn.close()