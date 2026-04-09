import sqlite3
import os

def seed():
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Read and execute schema
    with open(schema_path, 'r') as f:
        cur.executescript(f.read())
    
    # Sample Medicines (Jan Aushadhi Generics)
    medicines = [
        ('Paracetamol', 'Paracetamol', '500mg', 'Tablet', 10.0),
        ('Amoxicillin', 'Amoxicillin', '250mg', 'Capsule', 25.0),
        ('Metformin', 'Metformin Hydrochloride', '500mg', 'Tablet', 15.0),
        ('Atorvastatin', 'Atorvastatin', '10mg', 'Tablet', 20.0),
        ('Azithromycin', 'Azithromycin', '500mg', 'Tablet', 45.0),
        ('Cetirizine', 'Cetirizine Hydrochloride', '10mg', 'Tablet', 5.0),
        ('Omeprazole', 'Omeprazole', '20mg', 'Capsule', 12.0),
        ('Amlodipine', 'Amlodipine Besylate', '5mg', 'Tablet', 8.0)
    ]
    cur.executemany("INSERT INTO medicines (generic_name, salt, dosage, form, jan_price) VALUES (?, ?, ?, ?, ?)", medicines)
    
    # Sample Brands mapped to Generics
    # generic_id 1 is Paracetamol
    # generic_id 2 is Amoxicillin
    # generic_id 3 is Metformin
    # generic_id 4 is Atorvastatin
    # generic_id 5 is Azithromycin
    # generic_id 6 is Cetirizine
    # generic_id 7 is Omeprazole
    # generic_id 8 is Amlodipine
    
    brands = [
        ('Crocin', 1, 35.0),
        ('Dolo 650', 1, 30.0),
        ('Calpol', 1, 32.0),
        ('Mox', 2, 75.0),
        ('Novamox', 2, 80.0),
        ('Glycomet', 3, 55.0),
        ('Lipitor', 4, 120.0),
        ('Atorva', 4, 90.0),
        ('Azithral', 5, 150.0),
        ('Zyrtec', 6, 25.0),
        ('Omez', 7, 60.0),
        ('Amlokind', 8, 45.0)
    ]
    cur.executemany("INSERT INTO brands (brand_name, generic_id, mrp) VALUES (?, ?, ?)", brands)
    
    # Sample Stores
    stores = [
        ('Jan Aushadhi Kendra - Sector 12', 'Shop 4, Huda Market, Sector 12', 'Noida', '201301', 28.59, 77.34),
        ('Generic Pharma Plus', 'Main Road, Karkarduma', 'Delhi', '110092', 28.64, 77.30),
        ('Affordable Meds Kendra', 'G-6, Lajpat Nagar II', 'Delhi', '110024', 28.56, 77.24),
        ('Jan Aushadhi Store - Andheri East', 'Marol Pipe Line, JB Nagar', 'Mumbai', '400059', 19.11, 72.87)
    ]
    cur.executemany("INSERT INTO stores (name, address, city, pincode, lat, lng) VALUES (?, ?, ?, ?, ?, ?)", stores)
    
    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
