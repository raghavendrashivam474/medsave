# MedSave Dataset Limitations

**Version:** 1.0  
**Sprint:** 2.3  
**Status:** Complete  
**Last Updated:** 2026-07-31

---

## Purpose

This document provides an honest assessment of the current MedSave dataset.

Understanding the dataset's limitations is just as important as understanding its strengths. This document helps contributors, reviewers, and evaluators clearly understand what the current dataset can support today and what improvements are planned for future milestones.

The objective is to remain transparent about the current state while defining a clear path toward a production-quality healthcare dataset.

---

## Current Dataset Summary

| Property | Value |
|----------|-------|
| Primary Source | Kaggle (Community Dataset) |
| Total Records | 25 Medicine–Brand pairs |
| Unique Generic Medicines | ~8 |
| Unique Brands | 25 |
| Pharmacy Records | 4 (Sample Data) |
| Last Updated | July 2026 |

---

## Limitation 1 — Small Dataset

### Current Situation

The current dataset contains only a small collection of medicines suitable for development and demonstration.

Users searching for medicines outside this collection will receive no matching results.

### Demonstration Impact

Reliable demonstration medicines currently include:

- Losartan
- Amlodipine
- Levothyroxine
- Metformin
- Atorvastatin
- Paracetamol
- Amoxicillin
- Azithromycin
- Cetirizine
- Omeprazole

### Planned Resolution

Integrate the official PMBI Jan Aushadhi medicine catalogue containing approximately 2,000 medicines.

**Severity:** High

---

## Limitation 2 — Community Dataset

### Current Situation

The current medicine dataset originates from Kaggle and has not been officially verified against Government of India sources.

Medicine prices and details should therefore be considered suitable for development rather than authoritative healthcare information.

### Demonstration Impact

Price comparisons should be presented as representative examples rather than official values.

### Planned Resolution

Replace the demonstration dataset with:

- PMBI Jan Aushadhi catalogue
- NPPA official pricing data

**Severity:** High

---

## Limitation 3 — Sample Pharmacy Data

### Current Situation

The current pharmacy locations are manually created demonstration records.

They are intended only to validate application functionality.

### Demonstration Impact

Store search and map navigation demonstrate workflow rather than real pharmacy availability.

### Planned Resolution

Integrate the official Jan Aushadhi Kendra directory published by PMBI.

**Severity:** High

---

## Limitation 4 — Manual Updates

### Current Situation

The ETL pipeline currently executes manually.

Medicine information remains unchanged until a contributor performs another pipeline run.

### Demonstration Impact

Prices and medicine availability may gradually become outdated.

### Planned Resolution

Introduce scheduled pipeline execution and automated dataset refreshes.

**Severity:** Medium

---

## Limitation 5 — Dosage Formatting

### Current Situation

Dosages currently follow a simplified format.

Examples include:

```text
50MG
100MG
500MG
50MCG
```

Formatting may differ from the way users naturally search for medicines.

### Demonstration Impact

Search accuracy may depend on consistent formatting.

### Planned Resolution

Introduce standardized dosage normalization across all supported datasets.

**Severity:** Medium

---

## Limitation 6 — Missing Manufacturer Information

### Current Situation

Manufacturer information is not currently included.

### Demonstration Impact

Users cannot compare manufacturers or verify medicine producers.

### Planned Resolution

Include manufacturer details when integrating official PMBI datasets.

**Severity:** Low

---

## Limitation 7 — Single Data Source

### Current Situation

The current pipeline relies on a single external dataset.

A single-source architecture limits confidence in data accuracy.

### Demonstration Impact

Medicine information cannot currently be cross-validated.

### Planned Resolution

Adopt a multi-source strategy combining:

- PMBI
- NPPA
- Kaggle
- data.gov.in
- CDSCO

This will improve both completeness and confidence.

**Severity:** High

---

## Demonstration Guidance

For the current prototype, the following searches provide reliable demonstrations:

| Search | Expected Result |
|---------|-----------------|
| Losartan | Multiple branded alternatives |
| Metformin | Diabetes medicines |
| Paracetamol | Generic and branded comparison |
| Atorvastatin | Cholesterol medicines |
| Amlodipine | Blood pressure medicines |

Searching outside the current demonstration dataset may produce no results.

---

## Summary

| Limitation | Severity | Planned Resolution |
|------------|----------|-------------------|
| Small dataset | High | Integrate PMBI catalogue |
| Community data source | High | Replace with official datasets |
| Sample pharmacy data | High | Real Jan Aushadhi locations |
| Manual updates | Medium | Scheduled pipeline execution |
| Dosage formatting | Medium | Improved normalization |
| Missing manufacturer data | Low | PMBI enrichment |
| Single source dependency | High | Multi-source architecture |

---

## Future Outlook

These limitations are expected during the early stages of development.

The architecture has already been designed to support gradual evolution toward a larger, more reliable, and government-backed healthcare dataset.

Future milestones will focus on improving data quality rather than fundamentally changing the existing pipeline.

---

## Final Notes

Transparency is an important engineering principle.

Rather than hiding current limitations, MedSave documents them openly so that contributors understand where improvements are needed and evaluators can accurately assess the project's current maturity.

The existing dataset successfully demonstrates the complete data pipeline, while future milestones will focus on expanding its scale, reliability, and real-world applicability.
