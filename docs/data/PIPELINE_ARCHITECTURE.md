# MedSave Pipeline Architecture

**Version:** 1.0  
**Sprint:** 2.3  
**Status:** Complete  
**Last Updated:** 2026-07-31

---

## Overview

The MedSave Data Engine is a standalone ETL pipeline responsible for acquiring, processing, validating, and loading medicine data into the MedSave database.

It operates independently of both the backend API and frontend.

The Flask backend never communicates directly with the pipeline.

Instead, the pipeline populates the database, and the backend simply serves that data through its APIs.

This separation keeps data engineering independent from application development and makes each system easier to maintain.

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
|      Database        |
+----------------------+
        ▲
        │
+----------------------+
| Flask Backend API    |
+----------------------+
        ▲
        │
+----------------------+
| Frontend Application |
+----------------------+
```

---

## Pipeline Layers

### Source Layer

**Location**

```
pipeline/sources/
```

### Responsibility

Acquire raw datasets from external providers.

Each source should expose:

- Source identification
- Dataset retrieval
- Metadata about the source

Current implementation:

- KaggleSource

Sources should never:

- Parse data
- Validate data
- Normalize values
- Execute SQL

---

### Parser Layer

**Location**

```
pipeline/parsers/
```

### Responsibility

Convert raw files into internal pipeline entities.

Current implementation:

- CsvParser

Responsibilities include:

- Reading CSV files
- Checking required columns
- Creating Medicine entities
- Creating Brand entities
- Skipping malformed rows

Parsers should never:

- Normalize values
- Validate business rules
- Access the database

---

### Normalizer Layer

**Location**

```
pipeline/normalizers/
```

### Responsibility

Convert inconsistent raw values into standardized representations.

Current implementation:

- MedicineNormalizer

Examples include:

- Title Case names
- Standard medicine forms
- Price rounding
- Dosage formatting

Normalizers should never:

- Reject records
- Execute SQL
- Access external systems

---

### Validator Layer

**Location**

```
pipeline/validators/
```

### Responsibility

Apply business validation rules.

Current implementation:

- PipelineValidator

Validation includes:

- Required fields
- Accepted medicine forms
- Positive prices
- Reasonable numeric limits

Validators should:

- Accept
- Reject
- Log failures

Validators should never modify records.

---

### Loader Layer

**Location**

```
pipeline/loaders/
```

### Responsibility

Persist validated entities into the database.

Current implementation:

- PostgresLoader

Responsibilities include:

- Opening database connections
- Transactions
- Deduplication
- Insert operations
- Commit / Rollback

The loader is the only layer permitted to execute SQL.

---

## Entity Layer

**Location**

```
pipeline/entities/
```

Entities represent the internal pipeline models.

Current entities include:

- Medicine
- Brand

These models intentionally remain independent of the database schema.

Database IDs and foreign keys belong only inside the loader.

---

## Configuration

**Location**

```
pipeline/config.py
```

Configuration includes:

- Database URL
- Raw dataset location
- Processed dataset location

Both the backend and pipeline share the same database configuration.

---

## Logging

**Location**

```
pipeline/logger.py
```

Responsibilities include:

- Pipeline execution logs
- Validation summaries
- Error reporting
- Progress reporting

Future improvements may include structured logging and log rotation.

---

## Pipeline Execution Flow

A typical execution follows this sequence:

```text
Load Configuration

↓

Download Dataset

↓

Parse Raw Data

↓

Normalize Values

↓

Validate Records

↓

Load Database

↓

Commit Transaction

↓

Generate Summary
```

---

## Engineering Principles

| Principle | Description |
|------------|-------------|
| Single Responsibility | Every layer performs exactly one task |
| Separation of Concerns | Each stage is isolated from the others |
| Idempotency | Running the pipeline repeatedly is safe |
| Modularity | New sources can be added without changing existing layers |
| Database Isolation | Only the loader communicates with the database |
| Shared Configuration | Backend and pipeline use the same configuration |
| Extensibility | New datasets should integrate naturally into the architecture |

---

## Extending the Pipeline

### Adding a New Data Source

1. Create a new module inside `pipeline/sources/`
2. Inherit from the common source interface.
3. Implement dataset retrieval.
4. Register the source.
5. Update the pipeline configuration if required.

---

### Adding a New Parser

1. Create a parser inside `pipeline/parsers/`
2. Convert raw data into pipeline entities.
3. Return standardized entity collections.

---

### Adding a New Validation Rule

1. Update the validator.
2. Add the new business rule.
3. Log validation failures clearly.

No other pipeline layer should require modification.

---

## Current Capability Status

| Layer | Status |
|--------|--------|
| Source | ✅ Complete |
| Parser | ✅ Complete |
| Normalizer | ✅ Complete |
| Validator | ✅ Complete |
| Loader | ✅ Complete |
| Configuration | ✅ Complete |
| Logging | ✅ Complete |
| Orchestration | ✅ Complete |

---

## Future Evolution

The current architecture has been intentionally designed to support future expansion.

Potential future additions include:

- Multiple concurrent data sources
- Automated scheduled ingestion
- Incremental updates
- Dataset version tracking
- Source reliability scoring
- Data lineage
- Quality dashboards
- AI-assisted data validation

These enhancements should integrate naturally into the existing architecture without requiring major structural changes.

---

## Final Notes

The ETL pipeline forms the foundation of MedSave's data ecosystem.

Every medicine search result, price comparison, generic recommendation, and future AI capability ultimately depends on the quality of this pipeline.

For this reason, future contributors should prioritize maintaining clear separation between layers, preserving modularity, and extending the architecture rather than replacing it.
