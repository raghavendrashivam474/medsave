# MedSave Data Audit

**Version:** 1.0  
**Sprint:** 2.3  
**Status:** Complete  
**Last Updated:** 2026-07-31

---

## Purpose

This document records the findings of the current dataset audit conducted as part of the MedSave Data Strategy milestone.

It documents what data currently exists, its quality, its limitations, and what gaps need to be addressed before the dataset can support production use.

---

## Current Dataset

### Location

```
pipeline/raw/medicine_dataset.csv
```

### Source

Kaggle — Medicine Recommendation System Dataset

https://www.kaggle.com/datasets/pranayverma472/medicine-recommendation-system

### Format

CSV with UTF-8 encoding (BOM-tolerant parsing applied).

### Size

| Metric | Value |
|--------|-------|
| Total rows | 25 |
| Total columns | 7 |
| Unique generic medicines | ~8 |
| Unique branded medicines | 25 |

---

## Column Inventory

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| name | str | Generic medicine name | Losartan |
| salt | str | Active ingredient | Losartan Potassium |
| dosage | str | Strength | 50MG |
| form | str | Physical form | Tablet |
| brand_name | str | Commercial brand | Losar |
| mrp | float | Brand retail price (INR) | 65.00 |
| jan_price | float | Jan Aushadhi price (INR) | 8.40 |

---

## Data Quality Findings

### Finding 1 — Dosage Format Inconsistency

Dosage values in the raw dataset use uppercase without spacing.

```
50MG
25MG
100MG
50MCG
```

The normalizer currently applies `.upper().strip()` which preserves this format.

A future improvement should standardize dosage into a consistent format such as `50 mg` or `50mg` across all sources.

**Severity:** Medium

**Impact:** Search results may not match user queries like "50 mg".

---

### Finding 2 — Dataset Size

The current dataset contains 25 rows covering approximately 8 generic medicines.

This is sufficient for development and demonstration but is not representative of a real medicine catalogue.

India has thousands of approved generic medicines listed under the Jan Aushadhi scheme alone.

**Severity:** High

**Impact:** Search results will be sparse for anything outside the demonstration dataset.

---

### Finding 3 — Limited Medicine Categories

The current dataset covers a narrow range of therapeutic categories.

Current categories include:

- Antihypertensives
- Thyroid
- Antibiotics
- Diabetes
- Lipid-lowering
- Analgesics
- Antiallergics
- Gastric medicines

Missing categories include:

- Cardiovascular
- Respiratory
- Neurological
- Oncology
- Ophthalmology
- Dermatology
- Vitamins & Supplements
- Pediatric medicines

**Severity:** High

**Impact:** Demonstration is limited to a small subset of common medicines.

---

### Finding 4 — No Manufacturer Information

The current dataset does not include manufacturer information.

Manufacturer information would improve transparency and support future features.

**Severity:** Low

**Impact:** Additional datasets will eventually be required.

---

### Finding 5 — Store Data is Synthetic

Current pharmacy records are manually seeded demonstration data.

They do not represent actual Jan Aushadhi Kendra locations.

**Severity:** High

**Impact:** The store locator cannot demonstrate real-world usefulness until a genuine pharmacy dataset is integrated.

---

## Validation Results

Current validation status:

| Metric | Value |
|--------|-------|
| Medicines Passed | 25 |
| Medicines Rejected | 0 |
| Brands Passed | 25 |
| Brands Rejected | 0 |

The current dataset is internally consistent and suitable for development.

---

## Summary

| Finding | Severity | Recommended Action |
|----------|----------|-------------------|
| Dosage format inconsistency | Medium | Improve normalization |
| Dataset too small | High | Expand using reliable datasets |
| Limited medicine categories | High | Integrate additional medicine sources |
| Missing manufacturer information | Low | Future enhancement |
| Synthetic pharmacy data | High | Replace with real pharmacy dataset |

---

## Next Steps

The next documents in this milestone include:

- DATA_SOURCES.md
- DATA_STRATEGY.md
- PIPELINE_ARCHITECTURE.md
- FUTURE_DATA_EXPANSION.md

These documents will define where future datasets should come from, how they will be processed, and how MedSave's data layer will evolve over time.
