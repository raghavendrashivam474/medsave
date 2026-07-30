# MedSave Data Engine

## Overview

The MedSave Data Engine is a dedicated subsystem responsible for the complete lifecycle of medicine data, from acquisition through to database loading.

It operates independently of the Flask API and frontend. The Flask API remains completely unaware of the Data Engine. Its sole responsibility is to populate the database that the backend already serves.

---

## Architecture

```text
                 Flask API
                      |
                      v
               PostgreSQL Database
                      ^
                      |
               PostgreSQL Loader
                      ^
                      |
               Validation Layer
                      ^
                      |
             Normalization Layer
                      ^
                      |
                  Parser Layer
                      ^
                      |
                Source Adapters
```

Data flows strictly upward through the pipeline.

Each layer has a single responsibility and communicates only with the layer immediately below it.

---

## Folder Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `entities/` | Internal pipeline data models independent of the database schema. |
| `sources/` | External data source adapters implementing `BaseSource`. |
| `parsers/` | Convert raw datasets into pipeline entities. |
| `normalizers/` | Clean and standardize entity values. |
| `validators/` | Apply business validation rules before loading. |
| `loaders/` | Persist validated entities into the database. |
| `raw/` | Store downloaded datasets exactly as received. |
| `processed/` | Store processed datasets. |
| `config.py` | Shared configuration and environment variables. |
| `data_engine.py` | Entry point of the Data Engine. |

---

## Execution Flow

When fully implemented, the Data Engine executes the following workflow.

```text
1. Load configuration

2. Source Adapter
       |
       v
Download dataset

3. Parser
       |
       v
Medicine Entity
Brand Entity

4. Normalizer
       |
       v
Standardized Entities

5. Validator
       |
       v
Validated Entities

6. Loader
       |
       v
PostgreSQL Database
```

---

## Running the Data Engine

From the repository root:

```bash
python -m pipeline.data_engine
```

Expected output:

```text
=====================================

  MedSave Data Engine
  Version 0.1

  Pipeline initialized successfully.

=====================================
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL / SQLite connection string | sqlite:///backend/medsave.db |
| RAW_DIR | Directory for raw downloaded datasets | pipeline/raw |
| PROCESSED_DIR | Directory for processed datasets | pipeline/processed |

---

## Extending the Data Engine

### Adding a New Data Source

1. Create a new adapter in `pipeline/sources/`.
2. Inherit from `BaseSource`.
3. Implement:
   - `get_source_name()`
   - `fetch()`
   - `get_metadata()`
4. Export the class from `pipeline/sources/__init__.py`.

### Adding a New Loader

1. Create a new loader in `pipeline/loaders/`.
2. Follow the same interface as `PostgresLoader`.
3. Export the loader from `pipeline/loaders/__init__.py`.

The remainder of the pipeline should require no changes.

---

## Future Roadmap

| Sprint | Objective |
|---------|-----------|
| 2.1 | Data Engine Foundation |
| 2.2 | Kaggle Source + CSV Parser |
| 2.3 | Normalization + Validation |
| 2.4 | PostgreSQL Loader |
| 2.5 | Additional Data Sources |
| 2.6 | Scheduling & Monitoring |

---

## Design Principles

- Entities are independent of the database schema.
- Database IDs belong exclusively to the loader layer.
- Source adapters never perform parsing.
- Parsers never perform normalization.
- Normalizers never perform database operations.
- Validators enforce business rules before persistence.
- The loader is the only layer permitted to execute SQL.
- The Flask API remains completely unaware of the Data Engine.
- Every external source must inherit from `BaseSource`.
- Every pipeline layer has a single responsibility.

---

## Capability Mapping

| Capability | Primary Module |
|------------|----------------|
| Entity Representation | `pipeline/entities/` |
| Data Acquisition | `pipeline/sources/` |
| Data Parsing | `pipeline/parsers/` |
| Data Normalization | `pipeline/normalizers/` |
| Data Validation | `pipeline/validators/` |
| Database Persistence | `pipeline/loaders/` |
| Configuration | `pipeline/config.py` |
| Pipeline Orchestration | `pipeline/data_engine.py` |

---

## Current Repository Capabilities

| Capability | Status |
|------------|--------|
| Flask Backend | ✅ Complete |
| Medicine Search | ✅ Complete |
| Savings Calculation | ✅ Complete |
| Store Lookup | ✅ Complete |
| Data Engine Foundation | ✅ Complete |
| Source Abstraction | ✅ Complete |
| Entity Model | ✅ Complete |
| Configuration Layer | ✅ Complete |
| CSV Parsing | 🚧 Planned |
| Normalization | 🚧 Planned |
| Validation | 🚧 Planned |
| Database Loading | 🚧 Planned |
| Kaggle Integration | 🚧 Planned |

---

## Repository Evolution

```text
MVP
 |
 v
Deployment
 |
 v
Database Recovery
 |
 v
Data Engine Foundation (Sprint 2.1)
 |
 v
Kaggle Ingestion (Sprint 2.2)
 |
 v
Normalization & Validation (Sprint 2.3)
 |
 v
Production Data Pipeline
```

---

## End Product

The MedSave Data Engine transforms MedSave from a project relying on manually seeded sample data into a modular, extensible ingestion framework.

Future data sources, including Kaggle, Jan Aushadhi, CDSCO, NPPA, and other trusted medicine repositories, can be integrated by implementing new source adapters while reusing the existing parser, normalizer, validator, and loader infrastructure.

The Flask API and frontend remain unchanged throughout this evolution.
