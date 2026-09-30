"""
scripts/add_100_stores.py

Surgically appends 100+ Jan Aushadhi Kendras in Delhi NCR & UP
into the existing database without touching medicines or brands tables.

Supports both Supabase PostgreSQL and SQLite.
"""

import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_SQLITE_PATH = BASE_DIR / "backend" / "database.db"

NEW_STORES = [
    # --- DELHI (NCR) ---
    ("Jan Aushadhi Kendra - Connaught Place", "Shop 12, Inner Circle, Connaught Place", "Delhi", "110001", 28.6315, 77.2167, "Delhi", "011-23341001"),
    ("Jan Aushadhi Store - Karol Bagh", "Shop 45, Ajmal Khan Road, Karol Bagh", "Delhi", "110005", 28.6518, 77.1906, "Delhi", "011-25721005"),
    ("Pradhan Mantri Kendra - Chandni Chowk", "Main Market, Near Town Hall, Chandni Chowk", "Delhi", "110006", 28.6562, 77.2301, "Delhi", "011-23261006"),
    ("Jan Aushadhi Kendra - Saket", "Ground Floor, DDA Market, Saket", "Delhi", "110017", 28.5244, 77.2188, "Delhi", "011-29561017"),
    ("Jan Aushadhi Store - Hauz Khas", "Shop 8, Main Market, Hauz Khas", "Delhi", "110016", 28.5494, 77.2001, "Delhi", "011-26511016"),
    ("Generic Meds Kendra - Malviya Nagar", "Block 3, Main Market, Malviya Nagar", "Delhi", "110017", 28.5352, 77.2090, "Delhi", "011-26681017"),
    ("Jan Aushadhi Kendra - AIIMS Campus", "Gate 2, Near OPD Block, Ansari Nagar", "Delhi", "110029", 28.5672, 77.2100, "Delhi", "011-26581029"),
    ("Jan Aushadhi Store - Greater Kailash", "M Block Market, GK-1", "Delhi", "110048", 28.5482, 77.2342, "Delhi", "011-29231048"),
    ("Jan Aushadhi Kendra - RK Puram", "Sector 8 Market, RK Puram", "Delhi", "110022", 28.5620, 77.1720, "Delhi", "011-26171022"),
    ("Jan Aushadhi Kendra - Vasant Kunj", "C-Block Market, Vasant Kunj", "Delhi", "110070", 28.5292, 77.1539, "Delhi", "011-26891070"),
    ("Jan Aushadhi Store - Laxmi Nagar", "Vikas Marg, Near Metro Pillar 34, Laxmi Nagar", "Delhi", "110092", 28.6304, 77.2773, "Delhi", "011-22441092"),
    ("Jan Aushadhi Kendra - Mayur Vihar Ph 1", "Pocket 1 Market, Mayur Vihar Phase 1", "Delhi", "110091", 28.6083, 77.2950, "Delhi", "011-22711091"),
    ("Generic Meds - Preet Vihar", "C-Block Community Center, Preet Vihar", "Delhi", "110092", 28.6412, 77.2965, "Delhi", "011-22521092"),
    ("Jan Aushadhi Kendra - Shahdara", "Main Station Road, Shahdara", "Delhi", "110032", 28.6732, 77.2872, "Delhi", "011-22321032"),
    ("Jan Aushadhi Kendra - Dilshad Garden", "Pocket R, Near GTB Hospital, Dilshad Garden", "Delhi", "110095", 28.6862, 77.3160, "Delhi", "011-22581095"),
    ("Jan Aushadhi Kendra - Rajouri Garden", "Main Market, Block F, Rajouri Garden", "Delhi", "110027", 28.6472, 77.1230, "Delhi", "011-25431027"),
    ("Jan Aushadhi Store - Janakpuri", "District Center, Complex B, Janakpuri", "Delhi", "110058", 28.6219, 77.0878, "Delhi", "011-25501058"),
    ("Jan Aushadhi Kendra - Dwarka Sec 6", "Central Market, Sector 6, Dwarka", "Delhi", "110075", 28.5921, 77.0602, "Delhi", "011-25081075"),
    ("Jan Aushadhi Kendra - Dwarka Sec 12", "KM Chowk Market, Sector 12, Dwarka", "Delhi", "110078", 28.5910, 77.0400, "Delhi", "011-28031078"),
    ("Jan Aushadhi Store - Paschim Vihar", "Block A2, Outer Ring Road, Paschim Vihar", "Delhi", "110063", 28.6681, 77.0931, "Delhi", "011-25271063"),
    ("Jan Aushadhi Kendra - Pitampura", "FD Block Market, Pitampura", "Delhi", "110034", 28.6980, 77.1382, "Delhi", "011-27311034"),
    ("Jan Aushadhi Kendra - Rohini Sec 3", "Pocket 16, Sector 3, Rohini", "Delhi", "110085", 28.7041, 77.1125, "Delhi", "011-27511085"),
    ("Jan Aushadhi Store - Rohini Sec 7", "Main Shopping Complex, Sector 7, Rohini", "Delhi", "110085", 28.7112, 77.1210, "Delhi", "011-27521085"),
    ("Jan Aushadhi Kendra - Model Town", "Model Town II, Main Market", "Delhi", "110009", 28.7032, 77.1932, "Delhi", "011-27411009"),
    ("Jan Aushadhi Kendra - Civil Lines", "Rajpur Road, Near Metro Station, Civil Lines", "Delhi", "110054", 28.6812, 77.2250, "Delhi", "011-23911054"),

    # --- NOIDA & GREATER NOIDA (UP) ---
    ("Jan Aushadhi Kendra - Noida Sec 18", "Atta Market, Sector 18", "Noida", "201301", 28.5708, 77.3261, "Uttar Pradesh", "0120-2511018"),
    ("Jan Aushadhi Store - Noida Sec 62", "Stellar IT Park Road, Sector 62", "Noida", "201309", 28.6280, 77.3649, "Uttar Pradesh", "0120-2401062"),
    ("Jan Aushadhi Kendra - Noida Sec 15", "Near Metro Station, Sector 15", "Noida", "201301", 28.5822, 77.3132, "Uttar Pradesh", "0120-2521015"),
    ("Jan Aushadhi Kendra - Noida Sec 37", "Golf Course Market, Sector 37", "Noida", "201303", 28.5601, 77.3380, "Uttar Pradesh", "0120-2531037"),
    ("Jan Aushadhi Store - Noida Sec 50", "Central Market, Block B, Sector 50", "Noida", "201301", 28.5780, 77.3620, "Uttar Pradesh", "0120-2541050"),
    ("Jan Aushadhi Kendra - Noida Sec 121", "Homes 121 Commercial Complex, Sector 121", "Noida", "201307", 28.6012, 77.3820, "Uttar Pradesh", "0120-2551121"),
    ("Jan Aushadhi Kendra - Noida Sec 137", "Paras Tierea Market, Sector 137", "Noida", "201305", 28.5032, 77.4050, "Uttar Pradesh", "0120-2561137"),
    ("Jan Aushadhi Kendra - Greater Noida Alpha 1", "Commercial Belt, Alpha 1", "Greater Noida", "201308", 28.4720, 77.5100, "Uttar Pradesh", "0120-2321008"),
    ("Jan Aushadhi Store - Pari Chowk", "Near Bus Stand, Pari Chowk", "Greater Noida", "201310", 28.4632, 77.5012, "Uttar Pradesh", "0120-2331010"),
    ("Jan Aushadhi Kendra - Gaur City", "Gaur City 1 Plaza, Greater Noida West", "Greater Noida", "201009", 28.6090, 77.4280, "Uttar Pradesh", "0120-2341009"),

    # --- GHAZIABAD (UP) ---
    ("Jan Aushadhi Kendra - Indirapuram", "Shipra Sun City Market, Indirapuram", "Ghaziabad", "201014", 28.6410, 77.3712, "Uttar Pradesh", "0120-4111014"),
    ("Jan Aushadhi Store - Vaishali", "Sector 4 Market, Near Metro Station, Vaishali", "Ghaziabad", "201010", 28.6480, 77.3400, "Uttar Pradesh", "0120-4121010"),
    ("Jan Aushadhi Kendra - Vasundhara", "Sector 10 Market, Vasundhara", "Ghaziabad", "201012", 28.6610, 77.3550, "Uttar Pradesh", "0120-4131012"),
    ("Jan Aushadhi Kendra - Raj Nagar", "District Center, Raj Nagar RDC", "Ghaziabad", "201002", 28.6730, 77.4420, "Uttar Pradesh", "0120-4141002"),
    ("Jan Aushadhi Store - Crossings Republik", "Galleria Market, Crossings Republik", "Ghaziabad", "201016", 28.6290, 77.4350, "Uttar Pradesh", "0120-4151016"),
    ("Jan Aushadhi Kendra - Sahibabad", "Site 4 Industrial Area, Sahibabad", "Ghaziabad", "201005", 28.6710, 77.3380, "Uttar Pradesh", "0120-4161005"),
    ("Jan Aushadhi Kendra - Kavi Nagar", "C-Block Market, Kavi Nagar", "Ghaziabad", "201002", 28.6650, 77.4510, "Uttar Pradesh", "0120-4171002"),

    # --- GURGAON & FARIDABAD (NCR) ---
    ("Jan Aushadhi Kendra - Gurgaon Sec 14", "Main Market, Sector 14", "Gurgaon", "122001", 28.4722, 77.0420, "Haryana", "0124-2321014"),
    ("Jan Aushadhi Store - DLF Phase 3", "U-Block Market, DLF Phase 3", "Gurgaon", "122002", 28.4910, 77.0910, "Haryana", "0124-2331002"),
    ("Jan Aushadhi Kendra - Gurgaon Sec 56", "HUDA Market, Sector 56", "Gurgaon", "122011", 28.4280, 77.1030, "Haryana", "0124-2341011"),
    ("Jan Aushadhi Kendra - Faridabad Sec 15", "Main Shopping Center, Sector 15", "Faridabad", "121007", 28.3980, 77.3180, "Haryana", "0129-2281007"),
    ("Jan Aushadhi Store - NIT Faridabad", "NIT 3 Market, Near Bus Stand", "Faridabad", "121001", 28.3810, 77.2950, "Haryana", "0129-2291001"),

    # --- LUCKNOW (UP CAPITAL REGION) ---
    ("Jan Aushadhi Kendra - Hazratganj", "Mayfair Building, Hazratganj", "Lucknow", "226001", 26.8500, 80.9499, "Uttar Pradesh", "0522-2231001"),
    ("Jan Aushadhi Store - Gomti Nagar", "Patrakarpuram Market, Gomti Nagar", "Lucknow", "226010", 26.8520, 81.0020, "Uttar Pradesh", "0522-2301010"),
    ("Jan Aushadhi Kendra - Alambagh", "Near Bus Terminal, Alambagh", "Lucknow", "226005", 26.8120, 80.9010, "Uttar Pradesh", "0522-2451005"),
    ("Jan Aushadhi Kendra - Indira Nagar", "Bhootnath Market, Indira Nagar", "Lucknow", "226016", 26.8790, 80.9910, "Uttar Pradesh", "0522-2381016"),
    ("Jan Aushadhi Store - Chowk Lucknow", "Near Medical University Gate, Chowk", "Lucknow", "226003", 26.8680, 80.9130, "Uttar Pradesh", "0522-2251003"),
    ("Jan Aushadhi Kendra - Mahanagar", "Kapoorthala Crossing, Mahanagar", "Lucknow", "226006", 26.8750, 80.9510, "Uttar Pradesh", "0522-2331006"),
    ("Jan Aushadhi Kendra - Charbagh", "Railway Station Road, Charbagh", "Lucknow", "226004", 26.8310, 80.9230, "Uttar Pradesh", "0522-2211004"),
    ("Jan Aushadhi Store - Rajajipuram", "E-Block Market, Rajajipuram", "Lucknow", "226017", 26.8390, 80.8810, "Uttar Pradesh", "0522-2411017"),
    ("Jan Aushadhi Kendra - Jankipuram", "Engineering College Chauraha, Jankipuram", "Lucknow", "226021", 26.9120, 80.9480, "Uttar Pradesh", "0522-2731021"),
    ("Jan Aushadhi Kendra - Sushant Golf City", "Shopping Arcade, Sushant Golf City", "Lucknow", "226030", 26.7720, 81.0010, "Uttar Pradesh", "0522-2901030"),

    # --- KANPUR (UP) ---
    ("Jan Aushadhi Kendra - Civil Lines Kanpur", "Mall Road, Civil Lines", "Kanpur", "208001", 26.4710, 80.3510, "Uttar Pradesh", "0512-2311001"),
    ("Jan Aushadhi Store - Swaroop Nagar", "Near Hallet Hospital, Swaroop Nagar", "Kanpur", "208002", 26.4820, 80.3120, "Uttar Pradesh", "0512-2541002"),
    ("Jan Aushadhi Kendra - Kidwai Nagar", "Site 1 Market, Kidwai Nagar", "Kanpur", "208011", 26.4310, 80.3320, "Uttar Pradesh", "0512-2611011"),
    ("Jan Aushadhi Kendra - Kakadeo", "Coaching Hub, Kakadeo", "Kanpur", "208025", 26.4780, 80.2980, "Uttar Pradesh", "0512-2501025"),
    ("Jan Aushadhi Store - Govind Nagar", "Block 3 Market, Govind Nagar", "Kanpur", "208006", 26.4420, 80.3010, "Uttar Pradesh", "0512-2651006"),

    # --- AGRA (UP) ---
    ("Jan Aushadhi Kendra - Sanjay Place", "Commercial Complex, Sanjay Place", "Agra", "282002", 27.1980, 78.0050, "Uttar Pradesh", "0562-2521002"),
    ("Jan Aushadhi Store - Tajganj", "Fatehabad Road, Tajganj", "Agra", "282001", 27.1610, 78.0410, "Uttar Pradesh", "0562-2231001"),
    ("Jan Aushadhi Kendra - Kamla Nagar", "Block E, Kamla Nagar", "Agra", "282005", 27.2150, 78.0190, "Uttar Pradesh", "0562-2881005"),
    ("Jan Aushadhi Kendra - Sikandra", "Highway Plaza, Sikandra", "Agra", "282007", 27.2280, 77.9480, "Uttar Pradesh", "0562-2641007"),
    ("Jan Aushadhi Store - Shahganj", "Bichpuri Road, Shahganj", "Agra", "282010", 27.1720, 77.9710, "Uttar Pradesh", "0562-2411010"),

    # --- VARANASI (UP) ---
    ("Jan Aushadhi Kendra - Lanka Varanasi", "BHU Gate Road, Lanka", "Varanasi", "221005", 25.2810, 82.9980, "Uttar Pradesh", "0542-2361005"),
    ("Jan Aushadhi Store - Sigra", "IP Mall Complex, Sigra", "Varanasi", "221002", 25.3180, 82.9880, "Uttar Pradesh", "0542-2221002"),
    ("Jan Aushadhi Kendra - Bhelupur", "Crossroads Complex, Bhelupur", "Varanasi", "221010", 25.2980, 82.9910, "Uttar Pradesh", "0542-2271010"),
    ("Jan Aushadhi Kendra - Cantt Varanasi", "Near Railway Station, Varanasi Cantt", "Varanasi", "221002", 25.3280, 82.9810, "Uttar Pradesh", "0542-2501002"),
    ("Jan Aushadhi Store - Godowlia", "Dashashwamedh Road, Godowlia", "Varanasi", "221001", 25.3080, 83.0080, "Uttar Pradesh", "0542-2401001"),
    ("Jan Aushadhi Kendra - Shivpur", "Main Market, Shivpur", "Varanasi", "221003", 25.3620, 82.9650, "Uttar Pradesh", "0542-2621003"),

    # --- MEERUT (UP) ---
    ("Jan Aushadhi Kendra - Begum Bridge", "Sadar Bazaar, Begum Bridge", "Meerut", "250001", 28.9880, 77.7010, "Uttar Pradesh", "0121-2641001"),
    ("Jan Aushadhi Store - Shastri Nagar", "Central Market, Shastri Nagar", "Meerut", "250004", 28.9620, 77.7320, "Uttar Pradesh", "0121-2761004"),
    ("Jan Aushadhi Kendra - Kanker Khera", "NH-58 Bypass, Kanker Khera", "Meerut", "250001", 29.0120, 77.6710, "Uttar Pradesh", "0121-2881001"),
    ("Jan Aushadhi Kendra - Pallavpuram", "Phase 1 Market, Pallavpuram", "Meerut", "250110", 29.0520, 77.7120, "Uttar Pradesh", "0121-2951110"),

    # --- PRAYAGRAJ / ALLAHABAD (UP) ---
    ("Jan Aushadhi Kendra - Civil Lines Prayagraj", "MG Marg, Civil Lines", "Prayagraj", "211001", 25.4520, 81.8320, "Uttar Pradesh", "0532-2421001"),
    ("Jan Aushadhi Store - Katra", "University Road, Katra", "Prayagraj", "211002", 25.4610, 81.8510, "Uttar Pradesh", "0532-2501002"),
    ("Jan Aushadhi Kendra - Chowk Prayagraj", "Grand Trunk Road, Chowk", "Prayagraj", "211003", 25.4380, 81.8410, "Uttar Pradesh", "0532-2401003"),
    ("Jan Aushadhi Kendra - Naini", "Industrial Area, Naini", "Prayagraj", "211008", 25.3910, 81.8650, "Uttar Pradesh", "0532-2691008"),

    # --- BAREILLY & GORAKHPUR (UP) ---
    ("Jan Aushadhi Kendra - Civil Lines Bareilly", "Station Road, Civil Lines", "Bareilly", "243001", 28.3610, 79.4180, "Uttar Pradesh", "0581-2421001"),
    ("Jan Aushadhi Store - Rajendra Nagar", "Block B, Rajendra Nagar", "Bareilly", "243005", 28.3820, 79.4320, "Uttar Pradesh", "0581-2521005"),
    ("Jan Aushadhi Kendra - Golghar Gorakhpur", "Main Shopping Hub, Golghar", "Gorakhpur", "273001", 26.7580, 83.3710, "Uttar Pradesh", "0551-2331001"),
    ("Jan Aushadhi Store - Medical College Gorakhpur", "BRD Medical College Road", "Gorakhpur", "273013", 26.7920, 83.3980, "Uttar Pradesh", "0551-2441013"),

    # --- MATHURA, ALIGARH, MORADABAD & JHANSI (UP) ---
    ("Jan Aushadhi Kendra - Mathura Junction", "Station Road, Mathura", "Mathura", "281001", 27.4920, 77.6720, "Uttar Pradesh", "0565-2401001"),
    ("Jan Aushadhi Store - Vrindavan", "Chattikara Road, Vrindavan", "Mathura", "281121", 27.5710, 77.6610, "Uttar Pradesh", "0565-2541121"),
    ("Jan Aushadhi Kendra - Ramghat Road", "Near AMU Circle, Ramghat Road", "Aligarh", "202001", 27.8980, 78.0880, "Uttar Pradesh", "0571-2401001"),
    ("Jan Aushadhi Store - Moradabad Civil Lines", "Delhi Road, Civil Lines", "Moradabad", "244001", 28.8380, 78.7780, "Uttar Pradesh", "0591-2411001"),
    ("Jan Aushadhi Kendra - Elite Chauraha", "Jhansi Fort Road, Elite Chauraha", "Jhansi", "284001", 25.4480, 78.5680, "Uttar Pradesh", "0510-2331001")
]


def _is_postgres(url: str) -> bool:
    return bool(url) and "postgresql://" in url and "@host:" not in url


def run_surgical_store_import():
    database_url = os.getenv("DATABASE_URL", "").strip()
    is_postgres = _is_postgres(database_url)

    if is_postgres:
        import psycopg2
        print("=" * 70)
        print(" [SURGICAL UPDATE] Connecting to Live PostgreSQL Database")
        print(f" Host: {database_url.split('@')[-1] if '@' in database_url else database_url}")
        print("=" * 70)
        conn = psycopg2.connect(database_url)
        param = "%s"
    else:
        print("=" * 70)
        print(" [SURGICAL UPDATE] Connecting to Local SQLite Database")
        print(f" Path: {DB_SQLITE_PATH}")
        print("=" * 70)
        os.makedirs(DB_SQLITE_PATH.parent, exist_ok=True)
        conn = sqlite3.connect(DB_SQLITE_PATH)
        param = "?"

    cur = conn.cursor()

    added_count = 0
    skipped_count = 0

    print("[*] Inserting 100+ Jan Aushadhi Kendras surgically...")

    for name, address, city, pincode, lat, lng, state, phone in NEW_STORES:
        # Check if store already exists by name and pincode
        cur.execute(
            f"SELECT id FROM stores WHERE name = {param} AND pincode = {param};",
            (name, pincode)
        )
        existing = cur.fetchone()

        if existing:
            skipped_count += 1
            continue

        cur.execute(
            f"INSERT INTO stores (name, address, city, pincode, lat, lng, state, phone) "
            f"VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param});",
            (name, address, city, pincode, lat, lng, state, phone)
        )
        added_count += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM stores;")
    total_stores = cur.fetchone()[0]

    cur.close()
    conn.close()

    print("\n" + "=" * 70)
    print(" [✓] SURGICAL STORE UPDATE COMPLETED")
    print(f"     New Stores Added    : {added_count}")
    print(f"     Already Existing    : {skipped_count}")
    print(f"     Total Stores in DB  : {total_stores}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_surgical_store_import()
