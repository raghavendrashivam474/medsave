# MedSave — Milestone 6 (Part 1)
# Backend Enhancement Sprint
#
# Sprint   : Aug 2 – Aug 3
# Owner    : Backend Developer
# Status   : In Progress
#
# Deliverables
# ------------
# GET /api/medicine/<id>   Medicine Details API          [NEW]
# GET /api/search          Enhanced Search API           [ENHANCED]
# GET /api/health          Pre-existing — not modified
# GET /api/stores          Pre-existing — not modified
#
# Key decisions recorded here
# ----------------------------
# 1. medicine.py goes in backend/api/ to match existing structure.
# 2. Medicine Details uses success/message/error envelope (new endpoint,
#    no existing consumers, safe to standardize).
# 3. Search keeps bare-list response for backward compatibility.
#    New fields (medicine_id, match_type) are additive — not breaking.
# 4. Row access is always by column name (row["col"]) because
#    connection.py sets row_factory=sqlite3.Row and RealDictCursor.
# 5. medicine.py uses try/except/finally — errors caught and returned
#    as JSON 500, never as unhandled exceptions.
# 6. No schema changes. No seed data changes. No migration changes.
#
# See full brief in project management system.
