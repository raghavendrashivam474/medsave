-- =============================================================================
-- MedSave Database Migration
-- Version    : v0.5.0
-- Migrates from : v0.4.0
-- Updated    : 2026-08-01
-- =============================================================================
--
-- PURPOSE
--     Evolves an existing v0.4.0 MedSave database to v0.5.0 without
--     destroying existing data.
--
-- WHEN TO USE THIS FILE
--     Use this file when you have an existing database already populated
--     with data and want to apply the v0.5.0 schema changes safely.
--
--     For a completely fresh installation, use schema.sql instead.
--
-- HOW TO RUN (PostgreSQL)
--     psql $DATABASE_URL -f backend/database/migration_v0.5.0.sql
--
-- HOW TO RUN (SQLite)
--     SQLite does not support all ALTER TABLE operations used here.
--     For SQLite development environments, the recommended approach is:
--         1. Delete backend/database.db
--         2. Run python backend/database/seed_data.py
--     This recreates the database from the updated schema.
--
-- SAFETY
--     - No tables are dropped.
--     - No existing columns are removed.
--     - No existing data is modified.
--     - All new columns are nullable with no default required.
--     - All ALTER TABLE operations use IF NOT EXISTS where supported.
--     - All CREATE INDEX operations use IF NOT EXISTS.
--     - The migration is safe to inspect before running.
--
-- WHAT THIS MIGRATION DOES
--     Section 1 — Constraints on existing columns
--         1a. Add NOT NULL to brands.generic_id
--         1b. Add CHECK (jan_price > 0) to medicines.jan_price
--         1c. Add CHECK (mrp > 0) to brands.mrp
--         1d. Add ON DELETE CASCADE to brands -> medicines foreign key
--         1e. Add UNIQUE(generic_name, dosage) to medicines
--
--     Section 2 — New nullable columns
--         2a. medicines.manufacturer
--         2b. medicines.therapeutic_category
--         2c. medicines.schedule
--         2d. brands.manufacturer
--         2e. stores.state
--         2f. stores.phone
--
--     Section 3 — Indexes
--         3a. idx_medicines_generic_name
--         3b. idx_medicines_generic_dosage
--         3c. idx_brands_brand_name
--         3d. idx_brands_generic_id
--         3e. idx_stores_pincode
--         3f. idx_stores_coordinates
--
-- ROLLBACK
--     A rollback script is not provided automatically.
--     To undo this migration on a development database, the simplest
--     approach is to restore from a backup or reseed from scratch.
--     On a production database, create a backup before running.
--
-- =============================================================================


-- =============================================================================
-- PRE-FLIGHT CHECK
-- Verify the tables we expect to exist are actually present.
-- If any of these fail, stop and investigate before proceeding.
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'medicines'
    ) THEN
        RAISE EXCEPTION
            'Migration aborted: table "medicines" not found. '
            'Is this a v0.4.0 MedSave database?';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'brands'
    ) THEN
        RAISE EXCEPTION
            'Migration aborted: table "brands" not found. '
            'Is this a v0.4.0 MedSave database?';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'stores'
    ) THEN
        RAISE EXCEPTION
            'Migration aborted: table "stores" not found. '
            'Is this a v0.4.0 MedSave database?';
    END IF;

    RAISE NOTICE 'Pre-flight check passed. All expected tables exist.';
END;
$$;


-- =============================================================================
-- SECTION 1 — CONSTRAINTS ON EXISTING COLUMNS
--
-- These strengthen the integrity of columns that already exist.
-- Each operation is guarded to avoid errors if already applied.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1a. brands.generic_id — enforce NOT NULL
--
-- The pipeline loader never inserts a NULL generic_id, but the v0.4.0
-- schema allowed it. This enforces what the loader already guarantees.
--
-- Guard: check for existing nulls first. If any exist, log and skip.
-- In a clean dataset this should never block.
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    null_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO null_count
    FROM brands
    WHERE generic_id IS NULL;

    IF null_count > 0 THEN
        RAISE WARNING
            'Skipping NOT NULL constraint on brands.generic_id: '
            '% rows have NULL generic_id. Clean these rows first.',
            null_count;
    ELSE
        -- Check if constraint already applied
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'brands'
              AND column_name = 'generic_id'
              AND is_nullable = 'NO'
        ) THEN
            RAISE NOTICE 'brands.generic_id is already NOT NULL. Skipping.';
        ELSE
            ALTER TABLE brands ALTER COLUMN generic_id SET NOT NULL;
            RAISE NOTICE 'Applied NOT NULL to brands.generic_id.';
        END IF;
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 1b. medicines.jan_price — add CHECK (jan_price > 0)
--
-- The validator already rejects non-positive prices before they reach
-- the loader. This enforces the same rule at the database level.
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'medicines'
          AND constraint_name = 'medicines_jan_price_check'
    ) THEN
        RAISE NOTICE 'CHECK on medicines.jan_price already exists. Skipping.';
    ELSE
        ALTER TABLE medicines
            ADD CONSTRAINT medicines_jan_price_check
            CHECK (jan_price > 0);
        RAISE NOTICE 'Added CHECK (jan_price > 0) to medicines.';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 1c. brands.mrp — add CHECK (mrp > 0)
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'brands'
          AND constraint_name = 'brands_mrp_check'
    ) THEN
        RAISE NOTICE 'CHECK on brands.mrp already exists. Skipping.';
    ELSE
        ALTER TABLE brands
            ADD CONSTRAINT brands_mrp_check
            CHECK (mrp > 0);
        RAISE NOTICE 'Added CHECK (mrp > 0) to brands.';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 1d. brands.generic_id — add ON DELETE CASCADE to foreign key
--
-- The v0.4.0 schema had a foreign key without cascade behaviour.
-- We drop the old constraint and recreate it with CASCADE.
--
-- The old constraint name in v0.4.0 was auto-generated by PostgreSQL.
-- We find it dynamically rather than hardcoding a name.
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    old_constraint_name TEXT;
BEGIN
    -- Find the existing FK constraint name dynamically
    SELECT tc.constraint_name INTO old_constraint_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = 'brands'
      AND tc.constraint_type = 'FOREIGN KEY'
      AND kcu.column_name = 'generic_id'
    LIMIT 1;

    IF old_constraint_name IS NULL THEN
        RAISE NOTICE
            'No existing FK on brands.generic_id found. '
            'Adding fresh FK with CASCADE.';
        ALTER TABLE brands
            ADD CONSTRAINT brands_generic_id_fkey
            FOREIGN KEY (generic_id)
            REFERENCES medicines (id)
            ON DELETE CASCADE;
        RAISE NOTICE 'Added FK with ON DELETE CASCADE to brands.generic_id.';

    ELSE
        -- Check if it already has CASCADE
        IF EXISTS (
            SELECT 1
            FROM information_schema.referential_constraints
            WHERE constraint_name = old_constraint_name
              AND delete_rule = 'CASCADE'
        ) THEN
            RAISE NOTICE
                'FK on brands.generic_id already has CASCADE. Skipping.';
        ELSE
            -- Drop old FK and recreate with CASCADE
            EXECUTE format(
                'ALTER TABLE brands DROP CONSTRAINT %I', old_constraint_name
            );
            ALTER TABLE brands
                ADD CONSTRAINT brands_generic_id_fkey
                FOREIGN KEY (generic_id)
                REFERENCES medicines (id)
                ON DELETE CASCADE;
            RAISE NOTICE
                'Replaced FK "%" with CASCADE on brands.generic_id.',
                old_constraint_name;
        END IF;
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 1e. medicines — add UNIQUE(generic_name, dosage)
--
-- The pipeline loader deduplicates on (generic_name, dosage) in Python.
-- This enforces the same rule at the database level.
--
-- Guard: check for existing duplicates first. If duplicates exist,
-- log them and skip — do not fail the migration.
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    dup_count INTEGER;
BEGIN
    -- Count duplicate (generic_name, dosage) pairs
    SELECT COUNT(*) INTO dup_count
    FROM (
        SELECT generic_name, dosage
        FROM medicines
        GROUP BY generic_name, dosage
        HAVING COUNT(*) > 1
    ) dupes;

    IF dup_count > 0 THEN
        RAISE WARNING
            'Skipping UNIQUE(generic_name, dosage) on medicines: '
            '% duplicate pairs found. Deduplicate rows first.',
            dup_count;
    ELSE
        IF EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE table_name = 'medicines'
              AND constraint_name = 'medicines_generic_name_dosage_key'
        ) THEN
            RAISE NOTICE
                'UNIQUE(generic_name, dosage) already exists. Skipping.';
        ELSE
            ALTER TABLE medicines
                ADD CONSTRAINT medicines_generic_name_dosage_key
                UNIQUE (generic_name, dosage);
            RAISE NOTICE
                'Added UNIQUE(generic_name, dosage) to medicines.';
        END IF;
    END IF;
END;
$$;


-- =============================================================================
-- SECTION 2 — NEW NULLABLE COLUMNS
--
-- All new columns are nullable with no default value.
-- This guarantees existing INSERT statements in the pipeline loader
-- continue to work without any modification.
--
-- Each column addition is guarded with an existence check.
-- Re-running this migration on an already-migrated database is safe.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 2a. medicines.manufacturer
-- Planned: pharmaceutical manufacturer name
-- Source:  PMBI Jan Aushadhi catalogue (Phase 1 expansion)
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'medicines' AND column_name = 'manufacturer'
    ) THEN
        RAISE NOTICE 'medicines.manufacturer already exists. Skipping.';
    ELSE
        ALTER TABLE medicines ADD COLUMN manufacturer TEXT;
        RAISE NOTICE 'Added medicines.manufacturer (nullable TEXT).';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 2b. medicines.therapeutic_category
-- Planned: therapeutic classification (Antibiotic, Antihypertensive, etc.)
-- Source:  PMBI catalogue, WHO Essential Medicines List
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'medicines'
          AND column_name = 'therapeutic_category'
    ) THEN
        RAISE NOTICE
            'medicines.therapeutic_category already exists. Skipping.';
    ELSE
        ALTER TABLE medicines ADD COLUMN therapeutic_category TEXT;
        RAISE NOTICE
            'Added medicines.therapeutic_category (nullable TEXT).';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 2c. medicines.schedule
-- Planned: drug schedule under Indian pharmaceutical regulation
-- Values:  H, H1, X, G, etc.
-- Source:  CDSCO regulatory data (future integration)
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'medicines' AND column_name = 'schedule'
    ) THEN
        RAISE NOTICE 'medicines.schedule already exists. Skipping.';
    ELSE
        ALTER TABLE medicines ADD COLUMN schedule TEXT;
        RAISE NOTICE 'Added medicines.schedule (nullable TEXT).';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 2d. brands.manufacturer
-- Planned: brand manufacturer name
-- Source:  NPPA pricing data, commercial datasets (future integration)
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'brands' AND column_name = 'manufacturer'
    ) THEN
        RAISE NOTICE 'brands.manufacturer already exists. Skipping.';
    ELSE
        ALTER TABLE brands ADD COLUMN manufacturer TEXT;
        RAISE NOTICE 'Added brands.manufacturer (nullable TEXT).';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 2e. stores.state
-- Planned: Indian state name
-- Source:  Phase 4 Jan Aushadhi Kendra directory
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'stores' AND column_name = 'state'
    ) THEN
        RAISE NOTICE 'stores.state already exists. Skipping.';
    ELSE
        ALTER TABLE stores ADD COLUMN state TEXT;
        RAISE NOTICE 'Added stores.state (nullable TEXT).';
    END IF;
END;
$$;


-- -----------------------------------------------------------------------------
-- 2f. stores.phone
-- Planned: contact phone number for the pharmacy
-- Source:  Phase 4 Jan Aushadhi Kendra directory
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'stores' AND column_name = 'phone'
    ) THEN
        RAISE NOTICE 'stores.phone already exists. Skipping.';
    ELSE
        ALTER TABLE stores ADD COLUMN phone TEXT;
        RAISE NOTICE 'Added stores.phone (nullable TEXT).';
    END IF;
END;
$$;


-- =============================================================================
-- SECTION 3 — INDEXES
--
-- All indexes are created with IF NOT EXISTS.
-- Re-running this migration on an already-migrated database is safe.
--
-- Index choices are based on query patterns in:
--     backend/api/search.py
--     backend/api/stores.py
--     pipeline/loaders/postgres_loader.py
-- =============================================================================

-- medicines.generic_name — search API WHERE clause, loader dedup SELECT
CREATE INDEX IF NOT EXISTS idx_medicines_generic_name
    ON medicines (generic_name);

-- medicines(generic_name, dosage) — loader dedup key, UNIQUE constraint support
CREATE INDEX IF NOT EXISTS idx_medicines_generic_dosage
    ON medicines (generic_name, dosage);

-- brands.brand_name — search API WHERE clause
CREATE INDEX IF NOT EXISTS idx_brands_brand_name
    ON brands (brand_name);

-- brands.generic_id — search API JOIN, loader dedup SELECT
CREATE INDEX IF NOT EXISTS idx_brands_generic_id
    ON brands (generic_id);

-- stores.pincode — stores API pincode filter
CREATE INDEX IF NOT EXISTS idx_stores_pincode
    ON stores (pincode);

-- stores(lat, lng) — proximity search, future SQL-side distance queries
CREATE INDEX IF NOT EXISTS idx_stores_coordinates
    ON stores (lat, lng);

RAISE NOTICE 'All indexes created or already exist.';


-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'MedSave migration v0.5.0 complete.';
    RAISE NOTICE 'Schema is now at v0.5.0.';
    RAISE NOTICE '==========================================';
END;
$$;
