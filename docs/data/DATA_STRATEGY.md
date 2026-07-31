# MedSave Data Strategy

**Version:** 1.0  
**Sprint:** 2.3  
**Status:** Active  
**Last Updated:** 2026-07-31

---

## Purpose

This document defines the overall data strategy for MedSave.

It answers the core questions established in the Data Strategy milestone:

- Where should medicine data come from?
- How should multiple datasets be combined?
- How should duplicates be handled?
- How should inconsistent naming be normalized?
- How should data quality be verified?
- How should future updates be managed?

The objective is to build a scalable and trustworthy data foundation capable of supporting MedSave throughout its future evolution.

---

## Strategic Objective

Build a reliable medicine dataset capable of powering:

- Medicine Search
- Generic Alternative Discovery
- Price Comparison
- Nearby Pharmacy Search
- Future AI Recommendations
- Healthcare Analytics

Data quality is prioritized over data quantity.

A smaller, verified dataset is significantly more valuable than a larger dataset containing inconsistencies, duplicate records, or unreliable information.

---

## Data Source Strategy

### Current Primary Source

**Kaggle — Medicine Recommendation System**

The project currently relies on a small Kaggle dataset for development and demonstration purposes.

This dataset is intentionally lightweight and allows rapid development while the pipeline architecture matures.

It should be viewed as a temporary development source rather than the project's long-term dataset.

---

### Future Primary Source

**Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBI)**

The official Jan Aushadhi medicine catalogue should become MedSave's primary data source.

Advantages include:

- Official Government source
- Accurate Jan Aushadhi pricing
- Generic medicine catalogue
- High credibility
- Long-term sustainability

Integration will require PDF or HTML extraction before entering the existing ETL pipeline.

---

### Supplementary Sources

| Source | Primary Purpose |
|----------|----------------|
| NPPA | Official medicine pricing validation |
| Kaggle (larger datasets) | Broader medicine coverage |
| data.gov.in | Supplementary government datasets |
| CDSCO | Regulatory validation |
| WHO Essential Medicines List | Reference and completeness validation |

---

## Source Evolution Roadmap

### Phase 1

```
Kaggle CSV
        ↓
Pipeline
        ↓
Database
```

Development dataset only.

---

### Phase 2

```
PMBI
NPPA
Kaggle

        ↓

Unified Pipeline

        ↓

Database
```

Government data becomes authoritative.

---

### Phase 3

```
PMBI
NPPA
CDSCO
Government Open Data
Real Pharmacy Data

        ↓

Unified Pipeline

        ↓

Database
```

Multiple trusted sources contribute to a single unified medicine catalogue.

---

## Duplicate Handling Strategy

Duplicates are managed at multiple levels.

### Within a Single Pipeline Run

Multiple branded medicines often reference the same generic medicine.

During loading, generic medicines are deduplicated using:

- Generic Name
- Dosage

Brands remain separate records linked to their corresponding generic medicine.

---

### Across Multiple Pipeline Runs

Before inserting new records, the loader checks existing database records.

Previously imported medicines are skipped automatically.

This guarantees that repeated pipeline executions remain idempotent.

Running the same dataset multiple times produces the same database state.

---

### Future Cross-Source Deduplication

As multiple datasets become available, duplicate detection will rely on:

- Canonical generic names
- Active ingredient (salt)
- Dosage
- Medicine form

Whenever conflicts occur, official Government datasets should take precedence over community datasets.

---

## Normalization Strategy

Normalization occurs immediately after parsing and before validation.

Its purpose is to convert inconsistent raw data into a standard internal representation.

### Current Rules

| Field | Normalization |
|--------|---------------|
| Generic Name | Title Case |
| Salt | Title Case |
| Dosage | Uppercase |
| Form | Standard vocabulary |
| Jan Price | Two decimal places |
| Brand Price | Two decimal places |

---

### Standard Medicine Forms

The following forms should be treated as canonical:

- Tablet
- Capsule
- Syrup
- Injection
- Cream
- Ointment
- Gel
- Drops
- Suspension
- Powder
- Lotion
- Solution
- Spray
- Patch
- Inhaler

Unknown values should pass through while generating validation warnings.

---

### Future Improvements

Future normalization should include:

- Dosage formatting (`500MG → 500 mg`)
- Chemical synonym resolution
- Generic name standardization
- Brand spelling correction
- Unit normalization

---

## Validation Strategy

Validation occurs after normalization and before persistence.

Its purpose is to prevent invalid or inconsistent data from entering the database.

### Medicine Validation

Each medicine should satisfy:

- Generic name present
- Salt present
- Dosage present
- Valid medicine form
- Positive Jan Aushadhi price

---

### Brand Validation

Each brand should satisfy:

- Brand name present
- Linked generic medicine
- Positive MRP

---

### Validation Principles

- Validators never modify data.
- Validators only accept or reject.
- Every rejection should include a clear reason.
- Invalid records should not stop pipeline execution.
- Validation summaries should be generated after every run.

---

## Update Strategy

### Current

Updates are performed manually whenever a new dataset becomes available.

Each execution adds new records while preserving existing data.

---

### Future

Future improvements include:

| Phase | Improvement |
|--------|-------------|
| Phase 2 | Scheduled pipeline execution |
| Phase 2 | Automatic source downloads |
| Phase 3 | Incremental updates |
| Phase 3 | Source version tracking |
| Future | Data freshness monitoring |

---

## Engineering Principles

The MedSave data layer follows several core principles:

1. Prefer official sources over community sources.
2. Validate data before storing it.
3. Keep pipeline stages independent.
4. Preserve idempotency.
5. Maintain complete documentation.
6. Avoid destructive updates by default.
7. Design for future expansion without disrupting existing architecture.

---

## Long-Term Vision

The current pipeline has been intentionally designed as a modular system.

Future contributors should extend the existing architecture rather than replacing it.

As MedSave evolves, additional datasets, validators, parsers, and loaders should integrate naturally into the existing workflow while preserving the separation between:

```
Source

↓

Parser

↓

Normalizer

↓

Validator

↓

Entities

↓

Loader

↓

Database
```

Maintaining this architecture will ensure the data layer remains scalable, maintainable, and capable of supporting future AI-powered healthcare features.

---

## Final Notes

The quality of MedSave depends directly on the quality of its data.

Every search result, recommendation, price comparison, and future intelligent feature will ultimately rely on the decisions documented in this strategy.

For this reason, improvements to the data layer should prioritize accuracy, transparency, maintainability, and long-term sustainability over short-term convenience.
