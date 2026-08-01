# MedSave Future Data Expansion Plan

**Version:** 2.0
**Sprint:** Milestone 5
**Status:** Active
**Last Updated:** 2026-08-01

---

## Purpose

This document defines the long-term roadmap for expanding the MedSave data ecosystem beyond the current demonstration dataset.

It outlines how new datasets should be introduced, the order in which they should be integrated, and the engineering principles that should guide every future expansion.

The objective is to build a scalable, trustworthy, and maintainable medicine database capable of supporting MedSave throughout its evolution.

---

## Schema Readiness — v0.5.0

As of Milestone 5, the MedSave database schema has been evolved to support future data expansion with minimal structural changes.

Rather than introducing new tables for every future dataset, the schema now includes carefully planned nullable columns that can be populated incrementally as additional data sources are integrated.

This allows future pipeline work to focus primarily on ingestion and validation instead of repeated schema redesign.

The current schema is prepared for:

- Official PMBI medicine catalogue
- NPPA pricing information
- CDSCO regulatory metadata
- Jan Aushadhi Kendra directory expansion

Future schema changes should remain incremental and continue following the engineering principles defined within `SCHEMA_CHANGELOG.md`.

---

## Expansion Principles

Every future dataset should follow these principles:

1. **Trust before size.** Official government data should always be preferred over larger community datasets.

2. **Pipeline first.** Every dataset must pass through the existing ETL pipeline. No dataset should bypass parsing, normalization, validation, or loading.

3. **Additive by design.** New data should enrich the existing database rather than replace it whenever possible.

4. **Documentation before implementation.** Every new source should be evaluated and documented before engineering work begins.

5. **Validation before persistence.** No dataset should enter the database without passing the validation layer.

6. **Schema before ingestion.** If a future dataset requires additional database fields, evolve the schema first and document the changes in `docs/data/SCHEMA_CHANGELOG.md` before extending the ETL pipeline.

---

## Phase 1 — Jan Aushadhi Integration

### Priority

Highest

### Objective

Integrate the official PMBI Jan Aushadhi medicine catalogue as MedSave's primary medicine source.

### Expected Scale

Approximately 2,000 medicines.

### Why It Matters

The Jan Aushadhi catalogue aligns directly with MedSave's core objective:

- Official Government data
- Generic medicines
- Official Jan Aushadhi pricing
- High credibility
- Reliable long-term source

### Planned Work

- Create `JanAushadhiSource`
- Build PDF / HTML parser
- Normalize records
- Validate records
- Load into the database
- Preserve compatibility with existing pipeline

### Expected Outcome

Most common medicine searches should return meaningful results using official government data.

---

## Phase 2 — NPPA Pricing Integration

### Priority

High

### Objective

Enrich medicine pricing using official NPPA price information.

### Expected Benefits

- Price validation
- Ceiling price comparison
- More trustworthy savings calculations

### Planned Work

- Create `NPPASource`
- Build Excel parser
- Cross-reference existing medicine prices
- Flag inconsistent pricing

---

## Phase 3 — Expanded Medicine Catalogue

### Priority

Medium

### Objective

Increase medicine coverage using larger public datasets.

Potential sources include:

- Larger Kaggle datasets
- Government Open Data
- Additional public medicine catalogues

### Expected Benefits

- Better search coverage
- More branded medicines
- More dosage variations
- Better demonstration quality

---

## Phase 4 — Real Pharmacy Data

### Priority

High

### Objective

Replace demonstration pharmacy records with verified Jan Aushadhi Kendra locations.

### Planned Data

- Store name
- Address
- City
- State
- Pincode
- Coordinates
- Contact information

### Expected Outcome

Users can search for real pharmacies and navigate to genuine Jan Aushadhi Kendras.

---

## Future Pipeline Modules

Future expansion may introduce modules such as:

| Module | Purpose |
|----------|---------|
| `pipeline/sources/jan_aushadhi.py` | Official medicine catalogue |
| `pipeline/sources/nppa.py` | Government pricing |
| `pipeline/sources/kendra.py` | Pharmacy directory |
| `pipeline/parsers/pdf_parser.py` | PDF extraction |
| `pipeline/parsers/excel_parser.py` | Excel processing |

The existing architecture has already been designed to accommodate these additions.

---

## Current Schema Readiness

Following the database evolution completed in **Milestone 5 (v0.5.0)**, the schema has been prepared to support future data expansion with minimal structural changes.

Rather than requiring new columns for every future dataset, several expansion fields now exist as nullable columns and can be populated incrementally by future pipeline sources.

### Medicines

| Field | Current Status | Planned Source |
|-------|----------------|----------------|
| `manufacturer` | 🟡 Ready | PMBI Medicine Catalogue |
| `therapeutic_category` | 🟡 Ready | PMBI Medicine Catalogue |
| `schedule` | 🟡 Ready | CDSCO Regulatory Data |

### Brands

| Field | Current Status | Planned Source |
|-------|----------------|----------------|
| `manufacturer` | 🟡 Ready | NPPA Pricing Data |

### Stores

| Field | Current Status | Planned Source |
|-------|----------------|----------------|
| `state` | 🟡 Ready | Jan Aushadhi Kendra Directory |
| `phone` | 🟡 Ready | Jan Aushadhi Kendra Directory |

These fields are intentionally nullable so that existing datasets remain fully compatible while future data sources can enrich the database over time.

Most future expansion work should therefore focus on extending the ETL pipeline rather than modifying the database schema.

---

## Long-Term Expansion Roadmap

```text
v0.4.0
Demonstration Dataset
(Kaggle)

        │
        ▼

v0.5.0
Database Evolution
Schema ready for future expansion

        │
        ▼

Phase 1
Official PMBI Medicine Catalogue
Populates:
• manufacturer
• therapeutic_category

        │
        ▼

Phase 2
Official NPPA Pricing
Populates:
• brands.manufacturer

        │
        ▼

Phase 3
Expanded Medicine Datasets
Populates:
• medicines.schedule
(if regulatory datasets are integrated)

        │
        ▼

Phase 4
Official Jan Aushadhi Kendra Directory
Populates:
• stores.state
• stores.phone

        │
        ▼

Future
Multi-source Healthcare Knowledge Base
```

---

## Success Criteria

The expansion effort will be considered successful when:

- Official government medicine data becomes the primary source.
- Medicine coverage increases substantially.
- Real pharmacy locations replace demonstration data.
- Multiple trusted sources contribute to the database.
- All records pass validation.
- The pipeline remains modular and idempotent.
- Contributors can integrate future datasets without major architectural changes.

---

## Future Opportunities

Once the data foundation matures, MedSave can support features such as:

- AI-powered medicine recommendations
- Generic alternative suggestions
- Medicine availability prediction
- Regional medicine analytics
- Price trend analysis
- Pharmacy intelligence dashboards
- Healthcare research insights

These capabilities depend directly on building a strong and trustworthy data layer first.

---

## Final Notes

Data expansion is not simply about increasing the number of records.

It is about improving confidence, completeness, and maintainability while preserving the modular architecture already established within MedSave.

Every future dataset should strengthen the quality of the platform without increasing unnecessary complexity.

A carefully curated dataset will always provide greater long-term value than a large but unreliable collection of records.

As of **v0.5.0**, the underlying database schema has been prepared for the planned expansion phases documented above. Future work should primarily involve integrating new data sources through the existing ETL pipeline while preserving the stability, maintainability, and modular architecture of the platform.
