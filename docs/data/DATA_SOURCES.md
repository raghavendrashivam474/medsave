# MedSave Data Sources

**Version:** 1.0  
**Sprint:** 2.3  
**Status:** Complete  
**Last Updated:** 2026-07-31

---

## Purpose

This document evaluates publicly available medicine datasets that MedSave could integrate as future data sources.

Each source is assessed based on credibility, licensing, completeness, update frequency, ease of integration, and long-term sustainability.

The objective is not to integrate every source immediately, but to understand what options exist and determine which sources should be prioritized as the project evolves.

---

## Evaluation Criteria

| Criterion | Description |
|-----------|-------------|
| Credibility | Is the source official or government-backed? |
| License | Can the data be legally used? |
| Completeness | How comprehensive is the dataset? |
| Update Frequency | How often is the data refreshed? |
| Format | Is the data machine-readable? |
| Integration Effort | How difficult is integration? |
| Sustainability | Will this source remain available long-term? |

---

## Source 1 — Jan Aushadhi Product List (PMBI)

| Property | Value |
|----------|-------|
| Provider | Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBI) |
| URL | https://janaushadhi.gov.in/ProductList.aspx |
| Format | PDF / HTML |
| Records | 2,000+ medicines |
| Update Frequency | Periodic |
| Credibility | Very High |

### Description

The official Jan Aushadhi product catalogue contains medicine names, salts, dosage forms, strengths, and official Jan Aushadhi prices.

Since price comparison is one of MedSave's primary objectives, this should become the project's primary medicine source.

### Integration Assessment

Data currently requires extraction from PDF or HTML.

A dedicated source adapter should eventually automate this process.

**Recommendation:** Highest Priority

---

## Source 2 — Kaggle Medicine Datasets

| Property | Value |
|----------|-------|
| Provider | Kaggle Community |
| URL | https://www.kaggle.com |
| Format | CSV |
| Records | Hundreds to thousands |
| Update Frequency | Dataset dependent |
| Credibility | Medium |

### Description

Kaggle provides multiple medicine datasets contributed by the community.

The current MedSave demonstration dataset originates from Kaggle.

### Current Dataset

- Medicine Recommendation System
- Approximately 25 medicines
- Used only for development

### Integration Assessment

CSV datasets integrate directly with the existing parser.

Useful until larger official datasets are adopted.

**Recommendation:** High Priority (Short Term)

---

## Source 3 — CDSCO Drug Database

| Property | Value |
|----------|-------|
| Provider | Central Drugs Standard Control Organisation |
| URL | https://cdscoonline.gov.in |
| Format | Web Portal |
| Records | Thousands |
| Update Frequency | Continuous |
| Credibility | Very High |

### Description

CDSCO maintains India's official database of approved medicines.

Useful for validating manufacturers, approvals, and regulatory status.

### Integration Assessment

Currently requires scraping or manual extraction.

No official public bulk API exists.

**Recommendation:** Future Integration

---

## Source 4 — NPPA Drug Price Data

| Property | Value |
|----------|-------|
| Provider | National Pharmaceutical Pricing Authority |
| URL | https://www.nppaindia.nic.in |
| Format | Excel / PDF |
| Records | Scheduled Medicines |
| Update Frequency | Periodic |
| Credibility | Very High |

### Description

NPPA publishes official ceiling prices for medicines under price control.

This dataset can strengthen MedSave's pricing engine and improve price validation.

### Integration Assessment

Excel files are relatively easy to process using pandas.

A dedicated source adapter will eventually be required.

**Recommendation:** High Priority

---

## Source 5 — data.gov.in

| Property | Value |
|----------|-------|
| Provider | Government of India |
| URL | https://data.gov.in |
| Format | CSV / JSON / Excel |
| Records | Various |
| Update Frequency | Dataset dependent |
| Credibility | High |

### Description

India's Open Government Data platform hosts various healthcare datasets.

Coverage varies but may provide useful supplementary information.

### Integration Assessment

Most datasets can integrate directly with the existing pipeline.

Each dataset should be evaluated individually before adoption.

**Recommendation:** Medium Priority

---

## Source 6 — WHO Essential Medicines List

| Property | Value |
|----------|-------|
| Provider | World Health Organization |
| URL | https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.01 |
| Format | PDF |
| Records | ~500 medicines |
| Update Frequency | Every two years |
| Credibility | Very High |

### Description

The WHO Essential Medicines List identifies medicines considered globally important for healthcare.

Although not India-specific, it provides an authoritative reference for validating medicine coverage.

### Integration Assessment

Requires PDF extraction.

More valuable as a reference than a primary dataset.

**Recommendation:** Future Reference

---

## Source Priority

| Priority | Source | Purpose |
|----------|--------|---------|
| 1 | Jan Aushadhi (PMBI) | Primary medicine catalogue |
| 2 | NPPA | Official pricing validation |
| 3 | Larger Kaggle datasets | Development & expansion |
| 4 | data.gov.in | Supplementary government data |
| 5 | CDSCO | Regulatory validation |
| 6 | WHO Essential Medicines List | Reference & credibility |

---

## Current Strategy

Current development continues using the existing Kaggle demonstration dataset.

Future milestones should gradually transition toward official Government of India datasets while maintaining compatibility with the existing ETL pipeline.

The architecture should support multiple data sources simultaneously rather than relying on a single provider.

---

## Licensing Considerations

Before integrating any dataset:

- Verify licensing terms.
- Document attribution requirements.
- Ensure educational or project usage is permitted.
- Prefer official government datasets whenever possible.
- Avoid sources with unclear licensing or restricted redistribution.

---

## Final Notes

Reliable software begins with reliable data.

Future MedSave features—including medicine search, generic alternatives, price comparison, analytics, and AI recommendations—depend directly on the quality of the datasets integrated into the pipeline.

For this reason, data source selection should prioritize trustworthiness and maintainability over dataset size alone.
