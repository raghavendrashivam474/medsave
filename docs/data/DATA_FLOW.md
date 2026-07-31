# MedSave Data Flow

**Version:** 1.0  
**Sprint:** 2.3  
**Status:** Complete  
**Last Updated:** 2026-07-31

---

## Overview

This document describes how data flows through the MedSave system—from external medicine datasets to the information ultimately displayed to users.

Understanding this flow helps contributors identify responsibilities, maintain separation of concerns, and extend the system without introducing unnecessary coupling.

---

## End-to-End Flow

```text
External Dataset
        │
        ▼
Source Layer
        │
        ▼
Parser Layer
        │
        ▼
Normalizer Layer
        │
        ▼
Validator Layer
        │
        ▼
Loader Layer
        │
        ▼
Database
        │
        ▼
Backend API
        │
        ▼
Frontend
        │
        ▼
User
```

---

## Step 1 — Source Acquisition

### Responsibility

Acquire raw medicine datasets.

Current implementation:

- KaggleSource

Typical workflow:

```text
Dataset Available?

      │
      ▼

Yes ─────────► Use Local Dataset

No

      ▼

Download Dataset

      ▼

Return Dataset Path
```

The source layer only retrieves data.

It does not parse, validate, normalize, or store anything.

---

## Step 2 — Parsing

### Responsibility

Convert raw CSV files into internal entities.

Current implementation:

- CsvParser

Workflow:

```text
CSV File

      ▼

Validate Required Columns

      ▼

Read Each Row

      ▼

Create Medicine Entity

+

Create Brand Entity

      ▼

Return Entity Collections
```

The parser should never:

- Modify values
- Apply business rules
- Access the database

---

## Step 3 — Normalization

### Responsibility

Standardize values before validation.

Current implementation:

- MedicineNormalizer

Typical transformations include:

| Field | Example |
|--------|----------|
| Generic Name | PARACETAMOL → Paracetamol |
| Salt | paracetamol sodium → Paracetamol Sodium |
| Dosage | 500mg → 500MG |
| Form | tab → Tablet |
| Prices | Rounded to two decimals |

Output consists of clean, consistent entities.

---

## Step 4 — Validation

### Responsibility

Ensure every entity satisfies business rules before persistence.

Current implementation:

- PipelineValidator

Typical checks include:

- Required fields
- Positive prices
- Accepted medicine forms
- Valid dosage values

Validation philosophy:

```text
Valid Record

        ▼

Accept

──────────────

Invalid Record

        ▼

Reject

        ▼

Log Reason

        ▼

Continue Pipeline
```

Pipeline execution should never stop because of a single invalid record.

---

## Step 5 — Database Loading

### Responsibility

Persist validated entities.

Current implementation:

- PostgresLoader

Workflow:

```text
Connect Database

      ▼

Load Existing Records

      ▼

Detect Duplicates

      ▼

Insert New Medicines

      ▼

Insert Brands

      ▼

Commit Transaction
```

Important characteristics:

- Additive
- Idempotent
- Transaction-safe

Running the pipeline multiple times should never duplicate existing data.

---

## Step 6 — Backend API

Once data has been stored, the backend becomes responsible for serving it.

Example flow:

```text
Frontend Search

        ▼

GET /api/search

        ▼

Execute SQL Query

        ▼

Join Medicines + Brands

        ▼

Calculate Savings

        ▼

Return JSON
```

The backend does not perform ETL.

It simply exposes stored data through REST APIs.

---

## Step 7 — Frontend Rendering

The frontend consumes JSON responses returned by the backend.

Example information displayed:

- Brand Name
- Generic Name
- Medicine Form
- Dosage
- Brand Price
- Generic Price
- Estimated Savings

The frontend never interacts directly with the ETL pipeline.

---

## Data Transformation Summary

| Stage | Input | Output |
|--------|-------|--------|
| Source | External Dataset | Raw Dataset |
| Parser | Raw Dataset | Medicine & Brand Entities |
| Normalizer | Raw Entities | Standardized Entities |
| Validator | Standardized Entities | Valid Entities |
| Loader | Valid Entities | Database Records |
| Backend | Database | JSON Response |
| Frontend | JSON | User Interface |

---

## Example Journey

### Raw Dataset

```text
Losartan,Losartan Potassium,50MG,Tablet,Losar,65.00,8.40
```

↓

### Parsed Entity

```text
Medicine
Brand
```

↓

### Normalized

```text
Generic Name → Losartan
Dosage → 50MG
Form → Tablet
```

↓

### Validated

```text
✓ Accepted
```

↓

### Stored

```text
Medicines Table

Brands Table
```

↓

### Backend

```text
GET /api/search?q=losartan
```

↓

### Frontend

```text
Brand : Losar

Generic : Losartan

MRP : ₹65

Jan Aushadhi : ₹8.40

Savings : 87.1%
```

---

## Boundary Contracts

Each layer communicates only with the next layer.

```text
Source

↓

Parser

↓

Normalizer

↓

Validator

↓

Loader

↓

Database

↓

Backend

↓

Frontend
```

No layer should bypass another.

For example:

- Sources should never execute SQL.
- Parsers should never validate business rules.
- Validators should never modify values.
- Frontend should never access the database directly.

Maintaining these boundaries keeps the architecture modular and maintainable.

---

## Engineering Principles

The MedSave data flow follows several important principles:

- Single responsibility for every stage.
- Clear separation of concerns.
- Deterministic processing.
- Idempotent execution.
- Reusable components.
- Database isolation.
- Loose coupling between pipeline and application.

These principles ensure that future contributors can extend the system confidently without introducing unnecessary complexity.

---

## Final Notes

The data flow described here represents the backbone of MedSave.

Every medicine search, price comparison, generic recommendation, and future AI-powered feature ultimately depends on this pipeline functioning reliably.

As the project evolves, new datasets, validators, parsers, and loaders should integrate naturally into this workflow while preserving the existing architectural boundaries.
