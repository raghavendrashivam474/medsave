# Frontend v2 — Discovery Report

**Phase:** Discovery (Phase 1 of 5)
**Version:** 2.0
**Status:** Open (Phase 1 active — accepting findings)
**Framework:** [Frontend Refinement Framework v1.1](./Framework.md)

---

# Purpose

This document captures the collective observations about the current
state of the MedSave frontend following the completion of Frontend v1.

Discovery is the foundation of every refinement phase.

Its purpose is not to criticize the product, but to understand it.

Every observation recorded here should be based on evidence that can be
demonstrated, reproduced, or explained.

If an issue cannot be observed, it does not yet belong in this report.

---

# Scope

This Discovery Report covers the current implementation of:

- Homepage
- Search Results
- Medicine Details
- Trust Passport
- Shared Design System
- Responsive Behaviour
- Accessibility
- Performance
- Overall Product Consistency

This report intentionally excludes:

- Feature requests
- Backend improvements
- New product ideas
- Architecture proposals unrelated to refinement
- Future roadmap discussions

Those belong in separate planning documents.

---

# Discovery Principles

While contributing to this report, every contributor should remember:

- Observe before suggesting solutions.
- Record evidence instead of opinions.
- Focus on the current product, not future ideas.
- Avoid duplicate findings.
- Prioritize clarity over quantity.

The goal of Discovery is understanding — not problem solving.

---

# Contribution Model

Discovery is a collective engineering activity.

Every contributor views the product through a different lens.

Discovery runs in **five sequential rounds**, one perspective per round.

| Round | Perspective | Primary Focus | Contributor | Status |
|---|---|---|---|---|
| 1 | **Product Vision** | Alignment with the product's original intent and purpose | Raghav | Pending |
| 2 | **User Experience** | User flow, hesitations, moments of friction | Raghav | Pending |
| 3 | **Visual Design** | Alignment, spacing, hierarchy, visual consistency | Claude | Blocked (waits for Round 2) |
| 4 | **Engineering** | Code-level quality, duplication, quiet bugs, maintainability | Claude | Blocked (waits for Round 3) |
| 5 | **Architecture** | Structural consistency, coupling, hidden complexity | Claude | Blocked (waits for Round 4) |

## Independence Rule

Per **Framework v1.1**, each round completes its observations
**independently** before reading findings from earlier rounds.

> The value of multiple perspectives comes from their independence,
> not their sum. Whoever contributes first shapes what everyone else
> notices. Perspectives merge in the Discovery Report, not in each
> other's heads.

A contributor for a later round should not read earlier rounds' findings
until their own round is complete and submitted. Only after all rounds
close does anyone read the full report end-to-end.

Discovery concludes only when every round has been completed.

---

# Finding Structure

Every observation must follow the same format.

Consistency makes Planning significantly easier.

---

## Template

**Finding ID**

F-001

**Title**

Short descriptive title

**Observation**

A concise statement describing what was observed.

**Location**

Page, component, file, or workflow.

**Impact**

High / Medium / Low

**Confidence**

High / Medium / Low

**Perspective**

Product Vision / User Experience / Visual Design / Engineering / Architecture

**Suggested Owner**

Workstream most suited to address the finding.

**Theme**

Leave blank during Discovery.

Assigned during Planning.

**Notes**

Optional screenshots, references, recordings, or additional context.

---

## Interpretation Guide

### Impact

How significantly the observation affects:

- User experience
- Product trust
- Maintainability
- Performance
- Consistency

---

### Confidence

How certain the contributor is that the observation represents a genuine issue.

High confidence findings should generally require no further investigation.

Low confidence findings may require validation before Planning.

---

# Findings

---

## Round 1 — Product Vision

*Findings contributed from the product vision perspective.*

*(Empty. Awaiting Round 1 contribution.)*

---

## Round 2 — User Experience

*Findings contributed from UX review.*

*(Empty. Blocked until Round 1 closes.)*

---

## Round 3 — Visual Design

*Findings contributed from UI review.*

*(Empty. Blocked until Round 2 closes.)*

---

## Round 4 — Engineering

*Findings contributed from engineering and implementation review.*

*(Empty. Blocked until Round 3 closes.)*

---

## Round 5 — Architecture

*Findings contributed from the architectural perspective.*

*(Empty. Blocked until Round 4 closes.)*

---

# Discovery Health Checklist

Before Discovery can be closed, confirm the following:

- [ ] Every round has been completed.
- [ ] The independence rule was respected (each round written before reading earlier rounds).
- [ ] Duplicate findings have been consolidated.
- [ ] Every finding includes all required fields.
- [ ] Findings describe observations rather than solutions.
- [ ] Contributors confirm no additional major findings remain.

Only after completing this checklist should Planning begin.

---

# Deferred Observations

Observations discovered after Discovery has officially closed are **not**
added to this report.

Instead, they are recorded here as candidates for the next refinement
cycle.

This protects the current refinement scope while preserving valuable
future observations.

*(Empty at the beginning of every refinement phase.)*

---

# Closing Discovery

When Discovery concludes:

- Update **Status** from **Open** to **Closed**.
- Record the closing date.
- Record the contributors.
- Lock the document.
- Begin Phase 2 — Planning.

Once closed, this report becomes a permanent historical artifact
describing the product exactly as it existed before refinement began.

---

*This document is a living artifact throughout Phase 1 and becomes immutable once Planning begins.*
