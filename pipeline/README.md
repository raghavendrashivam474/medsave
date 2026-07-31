# MedSave Data Engine

## Overview

The MedSave Data Engine is a dedicated ETL subsystem responsible for the complete lifecycle of medicine data—from acquisition through processing, validation, and database loading.

It operates independently of both the Flask backend and the frontend application.

The backend never communicates directly with the pipeline. Instead, the Data Engine prepares and maintains the database, while the backend simply exposes that data through REST APIs.

This separation keeps data engineering isolated from application logic and allows both systems to evolve independently.

---

## High-Level Architecture

```text
External Data Sources
        │
        ▼
+----------------------+
|   Source Layer       |
| pipeline/sources/    |
+----------------------+
        │
        ▼
+----------------------+
|   Parser Layer       |
| pipeline/parsers/    |
+----------------------+
        │
        ▼
+----------------------+
| Normalizer Layer     |
| pipeline/normalizers/|
+----------------------+
        │
        ▼
+----------------------+
| Validator Layer      |
| pipeline/validators/ |
+----------------------+
        │
        ▼
+----------------------+
|   Loader Layer       |
| pipeline/loaders/    |
+----------------------+
        │
        ▼
+----------------------+
| PostgreSQL / SQLite  |
+----------------------+
        ▲
        │
+----------------------+
| Flask Backend API    |
+----------------------+
        ▲
        │
+----------------------+
| Frontend             |
+----------------------+
```

Data always flows downward through the pipeline.

Each layer communicates only with its adjacent layer, maintaining clear separation of responsibilities.

---

## Directory Responsibilities

| Component | Responsibility |
|-----------|----------------|
| entities/ | Internal pipeline models independent of the database schema |
| sources/ | External dataset adapters |
| parsers/ | Convert raw datasets into pipeline entities |
| normalizers/ | Standardize entity values |
| validators/ | Apply business validation rules |
| loaders/ | Persist validated entities into the database |
| raw/ | Original datasets exactly as received |
| processed/ | Intermediate or processed datasets |
| config.py | Shared configuration |
| logger.py | Pipeline logging |
| data_engine.py | Pipeline orchestration entry point |

---

## Running the Data Engine

From the project root:

```bash
python -m pipeline.data_engine
```

Example output:

```text
========================================

        MedSave Data Engine
        Version 0.3

Pipeline Initialized

Source Loaded
Parser Completed
Normalization Completed
Validation Completed
Database Updated

========================================

Medicines Loaded : 25
Brands Loaded    : 25

Pipeline Completed Successfully
```

---

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| DATABASE_URL | Database connection | SQLite fallback |
| RAW_DIR | Raw dataset directory | pipeline/raw |
| PROCESSED_DIR | Processed dataset directory | pipeline/processed |

---

## Layer Responsibilities

| Layer | Responsible For | Never Responsible For |
|-------|------------------|------------------------|
| Source | Acquiring datasets | Parsing, validation, SQL |
| Parser | Creating entities | Normalization, SQL |
| Normalizer | Standardizing values | Validation, SQL |
| Validator | Applying business rules | Modifying entities |
| Loader | Database persistence | Parsing or normalization |

---

## Extending the Pipeline

### Adding a New Source

1. Create a module inside `pipeline/sources/`
2. Inherit from the common source interface.
3. Implement:
   - `get_source_name()`
   - `fetch()`
   - `get_metadata()`
4. Export it from `pipeline/sources/__init__.py`

---

### Adding a New Parser

1. Create a parser inside `pipeline/parsers/`
2. Convert raw data into pipeline entities.
3. Return collections of `Medicine` and `Brand`.

---

### Adding a New Validation Rule

Update the validator with the required business rule.

Validation should:

- Accept
- Reject
- Log failures

It should never modify incoming entities.

---

## Current Capability Status

| Capability | Status |
|------------|--------|
| Source abstraction | ✅ Complete |
| Kaggle source | ✅ Complete |
| CSV parsing | ✅ Complete |
| Data normalization | ✅ Complete |
| Validation | ✅ Complete |
| PostgreSQL loader | ✅ Complete |
| SQLite fallback | ✅ Complete |
| Idempotent loading | ✅ Complete |
| Shared configuration | ✅ Complete |
| Structured logging | ✅ Complete |
| Jan Aushadhi integration | 🚧 Planned |
| NPPA integration | 🚧 Planned |
| Real pharmacy dataset | 🚧 Planned |
| Scheduled execution | 🚧 Planned |

---

## Related Documentation

| Document | Location |
|----------|----------|
| Pipeline Architecture | docs/data/PIPELINE_ARCHITECTURE.md |
| Data Flow | docs/data/DATA_FLOW.md |
| Data Strategy | docs/data/DATA_STRATEGY.md |
| Data Sources | docs/data/DATA_SOURCES.md |
| Data Audit | docs/data/DATA_AUDIT.md |
| Dataset Limitations | docs/data/DATASET_LIMITATIONS.md |
| Future Data Expansion | docs/data/FUTURE_DATA_EXPANSION.md |

---

## Design Principles

The MedSave Data Engine follows several core engineering principles:

- Every layer has a single responsibility.
- Pipeline entities remain independent of the database schema.
- Source adapters only acquire data.
- Parsers only create entities.
- Normalizers only standardize values.
- Validators only verify business rules.
- The loader is the only component permitted to execute SQL.
- The backend communicates only with the database.
- The frontend communicates only with the backend.
- Every new data source integrates through the existing pipeline rather than bypassing it.

---

## Long-Term Vision

The Data Engine has been designed as a modular foundation for MedSave's future growth.

As new government datasets, pharmacy directories, pricing authorities, and healthcare sources become available, they should integrate into the existing pipeline without requiring major architectural changes.

This approach keeps the data layer scalable, maintainable, and capable of supporting future AI-powered healthcare features while preserving the engineering principles established during the project's early development.
