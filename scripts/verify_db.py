import sqlite3

conn = sqlite3.connect("./backend/database.db")
c = conn.cursor()

c.execute("SELECT count(*) FROM medicines")
med_count = c.fetchone()[0]

c.execute("SELECT count(*) FROM brands")
brand_count = c.fetchone()[0]

print("=" * 95)
print(f" DATABASE AUDIT: {med_count} Generics | {brand_count} Branded Alternatives")
print("=" * 95)
print(f"{'Generic / Strength':<35} | {'Jan Price':<10} | {'Brand Name':<25} | {'MRP':<8} | {'Savings %'}")
print("-" * 95)

query = """
SELECT m.generic_name, m.jan_price, b.brand_name, b.mrp, 
       ROUND(((b.mrp - m.jan_price) / b.mrp) * 100, 1) as savings
FROM medicines m
JOIN brands b ON m.id = b.generic_id
ORDER BY savings DESC
LIMIT 12
"""
for row in c.execute(query):
    print(f"{row[0]:<35} | Rs {row[1]:<7.2f} | {row[2]:<25} | Rs {row[3]:<5.2f} | {row[4]}%")

print("-" * 95)
