# Sprint 2.2 — Completion Report

**Phase:** 2 — Data Foundation  
**Sprint:** 2.2 — First External Data Source (Kaggle Ingestion)  
**Status:** ✅ Complete  
**Date:** 2026-07-30

---

## 1. Executive Summary

Sprint 2.2 transformed the MedSave Data Engine from an architectural
framework into a functional, additive ingestion system.

The repository can now:

- Acquire external medicine datasets (CSV format)
- Parse them into internal entities
- Normalize entity values into a consistent standard
- Persist them into the production Supabase PostgreSQL database
- Do so idempotently and non-destructively, preserving existing records

The Flask API required zero modifications and now serves data from
both the original seed dataset and the newly ingested dataset
simultaneously.

---

## 2. Sprint Objective vs Delivered

| Objective | Status |
|-----------|--------|
| Download / read external dataset | ✅ |
| Parse dataset into Medicine and Brand entities | ✅ |
| Normalize entity values | ✅ |
| Persist entities into PostgreSQL | ✅ |
| Execute full pipeline via `python -m pipeline.data_engine` | ✅ |
| Flask endpoints continue functioning | ✅ |
| Schema remains unchanged | ✅ |
| Existing data preserved (additive ingestion) | ✅ |

---

## 3. Files Delivered

### Created

| File | Responsibility |
|------|----------------|
| `pipeline/logger.py` | Structured logging for all layers |
| `pipeline/parsers/csv_parser.py` | CSV → Medicine/Brand entities |
| `pipeline/normalizers/medicine_normalizer.py` | Standardization of entity values |

### Modified

| File | Change |
|------|--------|
| `pipeline/config.py` | Reads `backend/.env` so pipeline and API share `DATABASE_URL` |
| `pipeline/sources/kaggle.py` | Real fetch logic with local-file fallback when Kaggle credentials are unavailable |
| `pipeline/loaders/postgres_loader.py` | Dual-backend (SQLite/PostgreSQL) with additive check-then-insert |
| `pipeline/data_engine.py` | Full orchestration of source → parser → normalizer → loader flow |
| `pipeline/README.md` | Execution documentation |
| `pipeline/requirements.txt` | Pipeline dependencies |

### Unchanged (Verified)

- `backend/app.py`
- `backend/schema.sql`
- `backend/seed_data.py`
- `backend/.env`
- Frontend

---

## 4. Architecture

The final ingestion flow honors strict layer separation.

```text
Kaggle CSV
    |
    v
KaggleSource
(Acquires Raw File)
    |
    v
CsvParser
(Converts Rows into Entities)
    |
    v
MedicineNormalizer
(Standardizes Names, Dosage, Form)
    |
    v
PostgresLoader
(Additive Persistence with Duplicate Detection)
    |
    v
Supabase PostgreSQL
    |
    v
Flask API
```

### Layer Ownership

| Layer | Owns | Never Does |
|-------|------|------------|
| Source | Data acquisition | Parsing, database access |
| Parser | Format interpretation | Normalization, database access |
| Normalizer | Standardization | Parsing, database access |
| Loader | Database persistence | Parsing, normalization |

---

## 5. Key Design Decisions

### 5.1 Additive Ingestion (Not Destructive)

The initial implementation deleted existing rows before inserting new
ones. This was replaced with a check-then-insert strategy that:

- Preserves existing records across runs
- Detects duplicates by `(generic_name, dosage)` for medicines
- Detects duplicates by `(brand_name, generic_id)` for brands
- Makes repeated executions safe and idempotent
- Requires **zero schema changes**

### 5.2 Dual-Backend Loader (SQLite + PostgreSQL)

The loader automatically detects the database backend from
`DATABASE_URL`, matching the backend's behavior.

Benefits:

- Local SQLite development
- Production Supabase PostgreSQL
- Single pipeline implementation

### 5.3 Shared Configuration

`pipeline/config.py` now loads `backend/.env` first so the pipeline and
Flask backend always target the same database.

### 5.4 Local-File Fallback

If Kaggle authentication is unavailable, the source checks
`pipeline/raw/` before attempting a download.

This enables development without Kaggle credentials.

### 5.5 BOM-Tolerant CSV Parsing

The parser reads CSV files using `utf-8-sig`, automatically handling
UTF-8 BOM markers commonly found in exported datasets.

---

## 6. End-to-End Verification

### Test 1 — Original Seed Data Preserved

```text
GET /api/search?q=crocin

200 OK

Crocin
Paracetamol
500mg

Brand Price: ₹35
Jan Aushadhi: ₹10
```

### Test 2 — Newly Ingested Dataset

```text
GET /api/search?q=losartan

200 OK

Losar
Losartan Potassium
50MG

Brand Price: ₹65
Jan Aushadhi: ₹8.40
```

### Test 3 — Combined Dataset

```text
GET /api/search?q=paracetamol

200 OK

Crocin
Dolo 650
Calpol
```

This confirms:

- Seed data remains available
- Newly ingested data is searchable
- Both datasets coexist successfully

---

## 7. Capability Matrix

### Before Sprint 2.2

```text
Backend API                    ✓
Search                         ✓
Savings Engine                 ✓
Data Engine Architecture       ✓

External Dataset Acquisition   ✗
CSV Parsing                    ✗
Normalization                  ✗
Database Loading               ✗
End-to-End Ingestion           ✗
```

### After Sprint 2.2

```text
Backend API                    ✓
Search                         ✓
Savings Engine                 ✓
Data Engine Architecture       ✓

External Dataset Acquisition   ✓
CSV Parsing                    ✓
Normalization                  ✓
Database Loading               ✓
End-to-End Ingestion           ✓

Additive / Idempotent Loads    ✓
Dual-Backend Support           ✓
Shared Configuration           ✓
```

---

## 8. Known Limitations

| Limitation | Planned Sprint |
|------------|----------------|
| Kaggle authentication automation | 2.3 |
| Incremental / delta detection | 2.3 |
| Validation layer | 2.3 |
| Multiple data sources | 2.4 |
| Update logic | 2.3 |
| Dosage normalization consistency | Follow-up |

---

## 9. Recommendations for Sprint 2.3

1. Implement Kaggle authentication (`kaggle.json`)
2. Build the validation layer
3. Add upsert/update support
4. Introduce a second source adapter (Jan Aushadhi or CDSCO)
5. Standardize dosage formatting

---

## 10. Sign-Off

Sprint 2.2 delivers the planned objectives while introducing three
additional architectural improvements:

- Additive loading
- Dual-backend support
- Shared configuration

The Data Engine is now a functional, testable ingestion subsystem.

> **End Product Statement**
>
> The MedSave repository can now ingest a real external medicine
> dataset into the MedSave database without modifying the Flask API
> or database schema while preserving existing data.

Ready for review.
