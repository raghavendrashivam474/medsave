DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS medicines;

CREATE TABLE medicines (
    id SERIAL PRIMARY KEY,
    generic_name TEXT NOT NULL,
    salt TEXT NOT NULL,
    dosage TEXT,
    form TEXT,
    jan_price FLOAT NOT NULL
);

CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    brand_name TEXT NOT NULL,
    generic_id INTEGER,
    mrp FLOAT NOT NULL,
    FOREIGN KEY (generic_id) REFERENCES medicines (id),
    UNIQUE (brand_name, generic_id)
);

CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    lat FLOAT,
    lng FLOAT
);
