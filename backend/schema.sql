CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generic_name TEXT NOT NULL,
    salt TEXT NOT NULL,
    dosage TEXT,
    form TEXT,
    jan_price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL,
    generic_id INTEGER,
    mrp REAL NOT NULL,
    FOREIGN KEY (generic_id) REFERENCES medicines (id)
);

CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    lat REAL,
    lng REAL
);
