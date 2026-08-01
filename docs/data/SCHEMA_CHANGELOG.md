# MedSave Database Schema Changelog

**Location:** `backend/database/schema.sql`  
**Migration Scripts:** `backend/database/`

This document records every structural change made to the MedSave database schema across project versions.

Its purpose is to help contributors understand:

- What changed
- Why the change was made
- Which project components are affected
- How the database has evolved over time

The changelog should be updated whenever the database schema changes. Every modification should clearly describe its purpose, implementation, and expected impact on the backend, Data Engine, and future development.

---

# v0.5.0 — Database Evolution

**Milestone:** 5 — Database Evolution  
**Version:** v0.5.0  
**Date:** 2026-08-01

## Files Updated

- `backend/database/schema.sql`
- `backend/database/migration_v0.5.0.sql`
- `backend/seed_data.py` *(if schema changes require seed updates)*
- `backend/database/connection.py`
- Related backend queries (where required)
- Relevant project documentation

---

## Summary

Version **v0.5.0** focuses on evolving the existing database architecture while maintaining compatibility with the current backend APIs and the MedSave Data Engine.

Rather than redesigning the database, this milestone strengthens the existing schema through incremental improvements that support future scalability.

The overall philosophy of this release is:

- Evolve rather than replace.
- Preserve compatibility whenever possible.
- Strengthen database integrity.
- Improve long-term maintainability.
- Prepare the schema for future healthcare datasets.

All schema modifications fall into one or more of the following categories:

- Additive changes (new nullable columns)
- Stronger integrity constraints
- Improved foreign key relationships
- Performance-focused indexes
- Better documentation of database evolution

No existing tables are removed.

No existing columns are renamed.

Existing API contracts are preserved wherever possible.

The MedSave Data Engine continues to function using explicit column lists, allowing new nullable columns to be introduced without breaking existing data ingestion.

---

# Changes to `medicines` Table

The `medicines` table remains the central source of truth for generic medicine information.

Version **v0.5.0** extends the schema with additional metadata while preserving compatibility with the current backend APIs and Data Engine.

## New Columns

| Column | Type | Nullable | Purpose |
|---------|------|----------|---------|
| `manufacturer` | TEXT | Yes | Stores the pharmaceutical manufacturer. |
| `therapeutic_category` | TEXT | Yes | Categorizes medicines (e.g., Antibiotic, Analgesic). |
| `schedule` | TEXT | Yes | Stores regulatory schedule information (H, H1, X, etc.). |

All new columns are intentionally nullable.

This ensures:

- Existing data remains valid.
- Existing INSERT statements continue working.
- Future datasets can gradually populate these fields.

---

## Strengthened Constraints

The following constraints are introduced to improve data integrity.

### Unique Constraint

```sql
UNIQUE (generic_name, dosage)
```

This prevents duplicate medicine entries having the same generic name and dosage combination.

The Data Engine already avoids such duplicates during validation. The database now enforces the same rule.

---

### Price Validation

```sql
CHECK (jan_price > 0)
```

Medicine prices should always be positive.

This mirrors validation already performed by the Data Engine and ensures invalid data cannot be inserted directly into the database.

---

### Dosage Requirement

The `dosage` field is now required.

Although earlier versions permitted NULL values, the validation pipeline already rejected medicines without dosage information.

The schema has been updated so that the database accurately reflects existing validation rules instead of relying solely on application-level checks.

---

## Compatibility

The Data Engine inserts medicines using explicit column lists rather than `INSERT INTO medicines VALUES (...)`.

Because of this design:

- Existing loader logic continues to work.
- New nullable columns default to NULL.
- No loader modifications are required until richer datasets become available.

This approach allows the schema to evolve without disrupting existing ingestion workflows.

---

# Changes to `brands` Table

The `brands` table continues to represent branded medicines and their relationship to generic medicines.

The primary objective of this update is to strengthen referential integrity while preparing the schema for richer pricing and manufacturer information in future milestones.

## New Columns

| Column | Type | Nullable | Purpose |
|---------|------|----------|---------|
| `manufacturer` | TEXT | Yes | Stores the pharmaceutical manufacturer for branded medicines. |

The column is intentionally nullable.

Existing datasets do not currently provide complete manufacturer information for all branded medicines. Keeping the column nullable allows future data sources to populate it without affecting current functionality.

---

## Strengthened Constraints

### Generic Medicine Reference

The `generic_id` column is now mandatory.

Every branded medicine should reference a valid generic medicine.

Although the Data Engine already enforces this relationship during data loading, the database now guarantees it through a NOT NULL constraint.

---

### Price Validation

```sql
CHECK (mrp > 0)
```

Brand prices must always be positive.

This aligns database constraints with the validation rules already implemented in the Data Engine.

---

## Foreign Key Behaviour

The relationship between `brands` and `medicines` has been strengthened using cascading deletes.

```sql
FOREIGN KEY (generic_id)
REFERENCES medicines(id)
ON DELETE CASCADE
```

This ensures that deleting a generic medicine automatically removes any associated branded medicines.

Without this behaviour, orphaned brand records could remain in the database.

---

## Compatibility

Existing backend search queries continue to operate without modification.

The Data Engine continues inserting branded medicines using explicit column lists, so the new nullable `manufacturer` column does not require immediate pipeline changes.

Future government or commercial datasets can populate this information when available.

---

# Changes to `stores` Table

The `stores` table represents Jan Aushadhi Kendras and other pharmacies available through MedSave.

Although the current demonstration dataset contains only basic information, the schema has been extended to better support future integrations with official pharmacy directories.

## New Columns

| Column | Type | Nullable | Purpose |
|---------|------|----------|---------|
| `state` | TEXT | Yes | Stores the Indian state in which the pharmacy is located. |
| `phone` | TEXT | Yes | Stores the pharmacy contact number. |

Both columns are nullable because the current demonstration dataset does not contain complete information for every store.

These fields will become increasingly useful as MedSave integrates official Jan Aushadhi directory data and larger pharmacy datasets.

---

## API Compatibility

The existing Store API continues to operate without modification.

The backend serializes store records directly from the database.

As these new fields become available, they will automatically appear in API responses.

Frontend implementations should therefore treat these fields as optional rather than assuming they will always contain values.

---

## Future Expansion

The additional columns prepare the database for future capabilities such as:

- Richer pharmacy profiles
- Contact information display
- State-wise pharmacy filtering
- Improved search and discovery
- Government directory integration

No changes to the current Data Engine are required for these additions.

Future datasets can populate these fields incrementally without affecting existing records.

---

# Indexes and Query Performance

As the MedSave dataset grows, database indexing becomes increasingly important for maintaining fast search and lookup performance.

Version **v0.5.0** introduces indexes based on the current backend query patterns rather than anticipated future queries.

## New Indexes

| Index | Table | Columns | Primary Purpose |
|------|-------|---------|-----------------|
| `idx_medicines_generic_name` | medicines | `generic_name` | Generic medicine search |
| `idx_medicines_generic_dosage` | medicines | `generic_name`, `dosage` | Duplicate detection and validation |
| `idx_brands_brand_name` | brands | `brand_name` | Brand name search |
| `idx_brands_generic_id` | brands | `generic_id` | JOIN operations |
| `idx_stores_pincode` | stores | `pincode` | Store lookup by pincode |
| `idx_stores_coordinates` | stores | `latitude`, `longitude` | Future proximity searches |

---

## Why These Indexes?

The current backend primarily performs searches using:

- Generic medicine names
- Brand names
- Medicine-to-brand relationships
- Pharmacy pincode lookups

These indexes reduce unnecessary full-table scans as the medicine catalogue grows.

---

## Query Optimisation

The current backend frequently performs queries similar to:

```sql
SELECT ...
FROM brands
JOIN medicines
ON brands.generic_id = medicines.id
```

The new indexes improve:

- JOIN performance
- Search responsiveness
- Duplicate detection during ETL
- Future scalability

---

## Design Philosophy

Indexes have been added conservatively.

Only columns that are actively queried or expected to become common lookup fields have been indexed.

Additional indexes should only be introduced after identifying real performance bottlenecks rather than indexing every column by default.

---

# Migration Strategy

Version **v0.5.0** introduces a formal migration strategy for evolving the MedSave database while minimizing disruption to existing deployments.

## Canonical Schema

The file:

```text
backend/database/schema.sql
```

continues to represent the complete database definition for a fresh installation.

Any developer cloning the repository should be able to create the latest database directly from this file.

---

## Incremental Migration

To support existing PostgreSQL databases, this milestone also introduces:

```text
backend/database/migration_v0.5.0.sql
```

Rather than recreating the database, this migration evolves the existing schema using operations such as:

- `ALTER TABLE`
- `ADD COLUMN`
- `CREATE INDEX`
- `ADD CONSTRAINT`

This preserves existing records wherever practical while introducing the latest schema improvements.

---

## Backend Compatibility

The backend has been designed to remain compatible with the updated schema.

Key compatibility principles include:

- Existing API contracts remain unchanged.
- Existing SQL queries continue to function.
- New nullable columns do not affect current responses.
- Additional fields can be exposed incrementally as new frontend features are implemented.

This allows the backend and frontend to evolve independently while sharing the same database.

---

## Data Engine Compatibility

The MedSave Data Engine remains fully compatible with the updated schema.

Compatibility is achieved through several design decisions:

- Explicit column lists are used during INSERT operations.
- Validation occurs before data reaches the database.
- Newly introduced nullable columns default to `NULL`.
- Existing ETL workflows continue to operate without modification.

Future datasets can gradually populate the expanded schema without requiring changes to the ingestion architecture.

---

## Engineering Principles

Database evolution throughout MedSave follows a small set of engineering principles:

- Prefer additive changes over destructive changes.
- Preserve backward compatibility whenever possible.
- Keep the schema readable and maintainable.
- Reflect validation rules within the database itself.
- Allow the backend and Data Engine to evolve independently.

These principles ensure that future milestones can continue extending the database without repeated redesigns.

---

# Schema Evolution Timeline

| Version | Milestone | Primary Focus |
|---------|-----------|---------------|
| v0.1.0 | Initial Prototype | Basic medicine search prototype using SQLite |
| v0.2.0 | Backend Foundation | Flask APIs and improved database organization |
| v0.3.0 | Repository Architecture | Modular backend structure and project reorganization |
| v0.4.0 | Data Strategy & Validation | ETL pipeline, validation layer, PostgreSQL support, and documentation |
| v0.5.0 | Database Evolution | Schema refinement, stronger constraints, indexes, and migration strategy |

---

# Looking Ahead

The database architecture established in **v0.5.0** is designed to support future MedSave milestones without requiring significant structural redesign.

Potential future enhancements include:

- Pharmacy inventory and stock tracking
- Multiple medicine pricing sources
- Regional availability information
- Manufacturer and distributor metadata
- Medicine images and packaging details
- Government healthcare scheme integration
- User bookmarks and medicine history
- AI-assisted medicine recommendations
- Analytics and reporting datasets

These capabilities are intentionally outside the scope of this milestone but have influenced several design decisions introduced in this release.

---

# Guiding Principles

As MedSave continues to evolve, the database should remain guided by a few core principles:

- Design for long-term maintainability.
- Prefer incremental evolution over large rewrites.
- Keep business rules close to the data whenever appropriate.
- Maintain compatibility with existing APIs and the Data Engine.
- Document every structural change alongside its rationale.

Following these principles will help ensure that future contributors can understand not only *what* changed, but *why* those decisions were made.

---

# End of Changelog

This document should be reviewed and updated whenever structural database changes are introduced.

Every schema modification should include:

- A description of the change.
- The motivation behind it.
- Any compatibility considerations.
- The expected impact on the backend, Data Engine, and future development.

Maintaining this changelog helps preserve architectural context and provides a clear history of how the MedSave database has evolved over time.