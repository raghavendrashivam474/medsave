"""
backend/services

Business logic layer for the MedSave backend.

Services sit between the API layer (backend/api/) and the database
layer (backend/database/). They encapsulate query logic and data
transformation so that API routes remain thin.

This layer is currently a placeholder. As the backend grows, search
logic, store logic, and future recommendation logic will be extracted
into dedicated service modules here.

Planned services:
    MedicineSearchService  — medicine search and filtering logic.
    StoreService           — store lookup and proximity calculations.
    RecommendationService  — AI-powered medicine recommendations (future).
"""
