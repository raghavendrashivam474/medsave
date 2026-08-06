# Sprint 2 Completion Report

**Project:** MedSave  
**Sprint:** Phase 1 · Sprint 2 — Backend Capability Integration  
**Report Type:** Sprint Completion Report  
**Prepared By:** Backend Team  
**Status:** ✅ Complete  
**Date:** 07 August 2026

---

# 1. Executive Summary

Sprint 2 has been completed successfully.

Building upon the Hybrid Decision Engine introduced in Sprint 1, this sprint transitioned MedSave from architectural readiness to functional backend intelligence.

The Decision Engine is now the active execution path for recommendation-related functionality. Six deterministic, database-backed rules have been implemented, a dedicated Recommendations API has been introduced, and the backend remains fully backward compatible.

The complete automated regression suite now contains **227 tests**, all passing successfully without failures.

---

# 2. Sprint Objective

The objective of Sprint 2 was to transform the Decision Engine from an isolated architectural component into an operational backend capability.

The sprint focused on:

- Integrating the Decision Engine into backend workflows.
- Implementing deterministic recommendation logic.
- Exposing recommendation capabilities through stable APIs.
- Preserving existing backend behaviour.
- Maintaining complete regression stability.

---

# 3. Scope Delivered

## Backend Intelligence

- ✅ Decision Engine reconstructed and finalized
- ✅ Rule Provider expanded with production-ready logic
- ✅ AI Provider Interface preserved
- ✅ Recommendation routing operational

## Recommendation API

- ✅ POST `/api/recommendations`
- ✅ GET `/api/recommendations/health`

## Backend

- ✅ Recommendation blueprint registered
- ✅ Existing APIs preserved
- ✅ No breaking changes introduced

## Testing

- ✅ Decision Engine integration tests
- ✅ Recommendation API tests
- ✅ Full backend regression suite

---

# 4. Architecture

Sprint 1 established the architecture.

Sprint 2 operationalized it.

```
Client

↓

Recommendations API

↓

Decision Engine

↓

Rule Provider

↓

Database

↓

Recommendation Response
```

The architecture itself remains unchanged.

Only the implementation inside the architecture has evolved.

---

# 5. Module Structure

```
backend/

decision_engine/
│
├── engine.py
├── __init__.py
└── providers/
    ├── ai_provider.py
    ├── rule_provider.py
    └── __init__.py

api/
└── recommendations.py

tests/
└── test_decision_engine.py
```

---

# 6. Rule Provider

Sprint 2 expands the Rule Provider into six deterministic database-backed rules.

| Rule | Request Type | Purpose |
|------|--------------|---------|
| Cheapest Alternative | `cheapest_alternative` | Finds lowest MRP branded alternative |
| Best Savings | `best_savings` | Finds highest savings percentage |
| Generic Available | `generic_check` | Confirms generic medicine availability |
| Stock Check | `stock_check` | Uses brand count as stock proxy |
| Brand Alternatives | `brand_alternatives` | Lists all branded alternatives |
| Recommendation Score | `recommendation_score` | Scores and ranks brands (0–100) |

### Shared Backend Helpers

All rules share common database helpers for:

- Medicine lookup
- Brand retrieval
- Savings calculation

Each helper:

- Opens a database connection
- Executes the required query
- Closes the connection safely
- Supports both SQLite and PostgreSQL

---

# 7. Recommendation API

## POST `/api/recommendations`

Routes recommendation requests through the Decision Engine and returns deterministic results.

Supported request types:

- `cheapest_alternative`
- `best_savings`
- `generic_check`
- `stock_check`
- `brand_alternatives`
- `recommendation_score`

---

## GET `/api/recommendations/health`

Returns Decision Engine health information including:

- Engine status
- Current execution mode
- Registered rule count

---

# 8. Decision Engine

The Decision Engine remains architecturally identical to Sprint 1.

Execution modes:

```
Rule Mode

↓

Rules

AI Mode

↓

AI Provider

Hybrid Mode

↓

Rules First

↓

AI Fallback (when required)
```

Every response includes:

- `source`
- `mode`

allowing both frontend and monitoring systems to identify the execution path.

---

# 9. AI Provider Interface

The AI abstraction layer remains unchanged.

Current implementation includes:

- `AIProviderBase`
- `UnreachableAIProvider`

No external AI providers were implemented during this sprint.

Future providers such as Ollama, OpenAI, or Gemini can be added by implementing the provider interface without modifying the Decision Engine.

---

# 10. Testing

## Regression Results

```
227 tests passed

Execution Time:
2.03 seconds

Failures:
0

Errors:
0

Warnings:
0
```

### Test Distribution

| Suite | Result |
|------|--------|
| Existing Backend Tests | 114 / 114 |
| Decision Engine Tests | 113 / 113 |
| Total | 227 / 227 |

No regressions were introduced.

---

# 11. Files Delivered

## New Files

```
backend/decision_engine/

backend/api/recommendations.py

backend/tests/test_decision_engine.py
```

## Modified Files

```
backend/app.py
```

Only additive changes were made.

Existing backend modules remain unchanged.

---

# 12. Out of Scope

The following items were intentionally excluded:

- OpenAI integration
- Gemini integration
- Ollama integration
- API keys
- Prompt engineering
- Chatbot functionality
- Multi-agent systems
- Docker / deployment
- Frontend changes
- Architectural redesign

---

# 13. Known Limitations

Current implementation intentionally uses:

- Brand count as a stock availability proxy.
- Fixed recommendation scoring weights (70% savings, 30% price).
- Location context without store-level filtering.
- AI provider interface without concrete implementations.

These are acknowledged implementation boundaries rather than defects.

---

# 14. Acceptance Criteria

| Requirement | Status |
|------|--------|
| Existing backend stable | ✅ |
| Existing APIs unchanged | ✅ |
| Decision Engine integrated | ✅ |
| Rule Provider expanded | ✅ |
| Recommendation flow deterministic | ✅ |
| Frontend compatibility maintained | ✅ |
| Regression suite passing | ✅ |

---

# 15. Definition of Done

Sprint 2 is complete because:

- The Decision Engine is integrated into backend execution.
- Recommendation logic is deterministic and database-backed.
- Recommendation APIs are operational.
- Existing backend functionality remains stable.
- All automated regression tests pass.

---

# 16. Sprint Outcome

Sprint 2 establishes MedSave's first production-ready backend intelligence layer.

Recommendation capabilities are now:

- Deterministic
- Database-backed
- Fully testable
- Provider-agnostic

The backend is now capable of serving intelligent recommendation workflows without relying on external AI services.

Future AI providers can extend the system by implementing the provider interface alone, requiring no architectural redesign.

---

# Sprint Summary

| Area | Status |
|------|--------|
| Decision Engine | ✅ |
| Recommendation API | ✅ |
| Rule Provider | ✅ |
| Backend Integration | ✅ |
| Regression Testing | ✅ |
| Architecture Stability | ✅ |

---

**Sprint Status:** ✅ Complete

**Next Sprint:** Sprint 3 — Frontend Integration, Validation & System Stabilization