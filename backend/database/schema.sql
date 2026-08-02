-- =============================================================================
-- MedSave Canonical Database Schema
-- Version : v0.5.0
-- Updated : 2026-08-01
-- =============================================================================
--
-- This file defines the complete MedSave database schema from scratch.
-- It is used for fresh installations of the project.
--
-- For evolving an existing database without data loss, use:
--     backend/database/migration_v0.5.0.sql
--
-- Supported databases:
--     PostgreSQL  (primary — production)
--     SQLite      (fallback — local development)
--
-- SQLite compatibility notes:
--     - SQLite does not support SERIAL. Use INTEGER PRIMARY KEY instead.
--     - SQLite does not support ALTER TABLE ADD CONSTRAINT after creation.
--     - SQLite does not enforce foreign keys unless PRAGMA foreign_keys = ON.
--     - This file targets PostgreSQL syntax for the canonical schema.
--       The seed_data.py script handles SQLite separately.
--
-- Drop order respects foreign key dependencies.
-- brands references medicines, so brands must be dropped first.
-- =============================================================================

DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS stores;


-- =============================================================================
-- TABLE: medicines
--
-- Stores generic medicine records.
-- Each record represents one generic medicine at one dosage strength.
--
-- Deduplication key (enforced by UNIQUE constraint):
--     (generic_name, dosage)
--     This matches the pipeline loader duplicate detection logic in
--     pipeline/loaders/postgres_loader.py.
--
-- Future columns planned (see docs/data/FUTURE_DATA_EXPANSION.md):
--     manufacturer         TEXT  -- pharmaceutical manufacturer name
--     therapeutic_category TEXT  -- e.g. Antibiotic, Antihypertensive
--     schedule             TEXT  -- drug schedule (H, H1, X, G, etc.)
--
-- All future columns are added as nullable to preserve pipeline
-- compatibility. The loader inserts explicit column lists and will
-- never be broken by new nullable columns.
-- =============================================================================

CREATE TABLE medicines (
    id                   SERIAL PRIMARY KEY,

    -- Core identity fields (required)
    generic_name         TEXT    NOT NULL,
    salt                 TEXT    NOT NULL,
    dosage               TEXT    NOT NULL,
    form                 TEXT    NOT NULL,
    jan_price            FLOAT   NOT NULL CHECK (jan_price > 0),

    -- Future expansion fields (nullable — populated by future pipeline sources)
    manufacturer         TEXT,
    therapeutic_category TEXT,
    schedule             TEXT,

    -- Deduplication constraint — matches pipeline loader logic
    UNIQUE (generic_name, dosage)
);

COMMENT ON TABLE medicines IS
    'Generic medicine records. One row per generic medicine per dosage strength.';

COMMENT ON COLUMN medicines.generic_name IS
    'Generic or scientific name of the medicine. Title Case. Required.';

COMMENT ON COLUMN medicines.salt IS
    'Active pharmaceutical ingredient (API). Title Case. Required.';

COMMENT ON COLUMN medicines.dosage IS
    'Strength of the medicine (e.g. 500MG, 10MG). Uppercase. Required.';

COMMENT ON COLUMN medicines.form IS
    'Physical form from standard vocabulary (Tablet, Capsule, Syrup, etc.). Required.';

COMMENT ON COLUMN medicines.jan_price IS
    'Jan Aushadhi scheme price in INR. Must be positive.';

COMMENT ON COLUMN medicines.manufacturer IS
    'Pharmaceutical manufacturer. Nullable. Populated when official source data is available.';

COMMENT ON COLUMN medicines.therapeutic_category IS
    'Therapeutic category (e.g. Antibiotic, Antihypertensive). Nullable.';

COMMENT ON COLUMN medicines.schedule IS
    'Drug schedule under Indian pharmaceutical regulation (H, H1, X, G, etc.). Nullable.';


-- =============================================================================
-- TABLE: brands
--
-- Stores branded medicine records linked to their generic counterpart.
--
-- Each brand row references exactly one medicine (generic) row.
-- A medicine may have many brands (one-to-many).
--
-- Deduplication key (enforced by UNIQUE constraint):
--     (brand_name, generic_id)
--     This matches the pipeline loader duplicate detection logic.
--
-- Foreign key behaviour:
--     ON DELETE CASCADE — if a generic medicine is deleted, all its
--     associated brand records are automatically removed. This prevents
--     orphaned brand rows with no linked generic.
--
-- Future columns planned (see docs/data/FUTURE_DATA_EXPANSION.md):
--     manufacturer  TEXT  -- brand manufacturer name
-- =============================================================================

CREATE TABLE brands (
    id           SERIAL PRIMARY KEY,

    -- Core identity fields (required)
    brand_name   TEXT    NOT NULL,
    generic_id   INTEGER NOT NULL,
    mrp          FLOAT   NOT NULL CHECK (mrp > 0),

    -- Future expansion fields (nullable)
    manufacturer TEXT,

    -- Referential integrity
    FOREIGN KEY (generic_id)
        REFERENCES medicines (id)
        ON DELETE CASCADE,

    -- Deduplication constraint — matches pipeline loader logic
    UNIQUE (brand_name, generic_id)
);

COMMENT ON TABLE brands IS
    'Branded medicine records. Each brand links to exactly one generic medicine.';

COMMENT ON COLUMN brands.brand_name IS
    'Commercial brand name of the medicine. Title Case. Required.';

COMMENT ON COLUMN brands.generic_id IS
    'Foreign key to medicines.id. NOT NULL — every brand must have a generic. Cascades on delete.';

COMMENT ON COLUMN brands.mrp IS
    'Maximum Retail Price of the branded medicine in INR. Must be positive.';

COMMENT ON COLUMN brands.manufacturer IS
    'Brand manufacturer name. Nullable. Populated when source data is available.';


-- =============================================================================
-- TABLE: stores
--
-- Stores Jan Aushadhi pharmacy (Kendra) location records.
--
-- Currently populated with demonstration data.
-- Phase 4 will replace this with real verified pharmacy locations.
-- (see docs/data/FUTURE_DATA_EXPANSION.md — Phase 4)
--
-- Future columns planned:
--     state    TEXT  -- Indian state name
--     phone    TEXT  -- contact phone number
-- =============================================================================

CREATE TABLE stores (
    id       SERIAL PRIMARY KEY,

    -- Core identity fields (required)
    name     TEXT  NOT NULL,
    address  TEXT  NOT NULL,
    city     TEXT  NOT NULL,
    pincode  TEXT  NOT NULL,

    -- Location coordinates (nullable — not all stores may have GPS data)
    lat      FLOAT,
    lng      FLOAT,

    -- Future expansion fields (nullable)
    state    TEXT,
    phone    TEXT
);

COMMENT ON TABLE stores IS
    'Jan Aushadhi pharmacy (Kendra) records. Currently demonstration data.';

COMMENT ON COLUMN stores.name IS
    'Name of the pharmacy or Kendra. Required.';

COMMENT ON COLUMN stores.address IS
    'Street address of the store. Required.';

COMMENT ON COLUMN stores.city IS
    'City where the store is located. Required.';

COMMENT ON COLUMN stores.pincode IS
    'Indian postal pincode. Required. Used for pincode-based store lookup.';

COMMENT ON COLUMN stores.lat IS
    'Latitude coordinate. Nullable. Used for proximity search.';

COMMENT ON COLUMN stores.lng IS
    'Longitude coordinate. Nullable. Used for proximity search.';

COMMENT ON COLUMN stores.state IS
    'Indian state name. Nullable. Populated during Phase 4 pharmacy data integration.';

COMMENT ON COLUMN stores.phone IS
    'Contact phone number. Nullable. Populated during Phase 4 pharmacy data integration.';


-- =============================================================================
-- INDEXES
--
-- All indexes are chosen based on actual query patterns observed in:
--     backend/api/search.py  — medicine and brand name search
--     backend/api/stores.py  — pincode lookup and proximity fetch
--     pipeline/loaders/postgres_loader.py — deduplication SELECTs
--
-- Index rationale documented per index below.
-- =============================================================================

-- medicines.generic_name
-- Used in: search API WHERE clause (ILIKE %s)
-- Used in: loader SELECT for deduplication
CREATE INDEX idx_medicines_generic_name
    ON medicines (generic_name);

-- medicines(generic_name, dosage) — composite
-- Used in: loader deduplication key (generic_name, dosage)
-- Supports the UNIQUE constraint lookup efficiently
CREATE INDEX idx_medicines_generic_dosage
    ON medicines (generic_name, dosage);

-- brands.brand_name
-- Used in: search API WHERE clause (ILIKE %s)
CREATE INDEX idx_brands_brand_name
    ON brands (brand_name);

-- brands.generic_id
-- Used in: search API JOIN ON b.generic_id = m.id
-- Used in: loader deduplication SELECT
-- Critical for join performance as medicine dataset grows
CREATE INDEX idx_brands_generic_id
    ON brands (generic_id);

-- stores.pincode
-- Used in: stores API WHERE pincode = ?
CREATE INDEX idx_stores_pincode
    ON stores (pincode);

-- stores(lat, lng) — composite
-- Used in: proximity search fetches all rows then filters in Python
-- Prepares for future SQL-side distance calculation
CREATE INDEX idx_stores_coordinates
    ON stores (lat, lng);
