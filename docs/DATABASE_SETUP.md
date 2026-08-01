# MedSave Database Setup

**Version:** 2.0  
**Schema Version:** v0.5.0  
**Last Updated:** 2026-08-01

This guide explains how to set up and maintain the MedSave database for both fresh installations and future schema upgrades.

---

## Prerequisites

- Python 3.13+
- PostgreSQL database (Supabase recommended)
- SQLite is also supported for local development
- Git
- Virtual Environment

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/medsave.git
cd medsave
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it.

### Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create a Supabase Project

1. Create a new Supabase project.
2. Open **Connect**.
3. Select **Session Pooler**.
4. Copy the PostgreSQL connection string.

Example:

```text
postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

---

## 5. Configure Environment Variables

Create a `.env` file inside the `backend` directory.

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

> **Note:** Both the Flask backend and the MedSave Data Engine use the same `DATABASE_URL`. This ensures the ETL pipeline and REST API always operate on the same database. When configured with SQLite, the same workflow continues to function for local development.

---

## 6. Create Database Schema

Open the Supabase Dashboard.

```
SQL Editor
```

Create a new query.

Copy the contents of:

```
backend/database/schema.sql
```

Paste them into the SQL Editor and click **Run**.

---

## 7. Database Schema

The canonical database schema is maintained in:

```text
backend/database/schema.sql
```

As of **v0.5.0**, the schema has been strengthened with additional constraints, indexes, and expansion-ready columns while preserving compatibility with the existing backend and Data Engine.

Future schema modifications should always be documented in:

```text
docs/data/SCHEMA_CHANGELOG.md
```

---

## 8. Seed Initial Data

Run

```bash
python backend/seed_data.py
```

The seed script creates the required tables (if they do not already exist) and populates the database with demonstration data compatible with the current schema version.

Expected output:

```text
Seeding PostgreSQL database...
Database seeded successfully!
```

---

## 9. Start the Backend

```bash
python backend/app.py
```

Expected output:

```text
Running on http://127.0.0.1:5000
```

---

## 10. Verify Installation

Open

```
http://127.0.0.1:5000/api/search?q=crocin
```

---

## 11. Verify the Data Engine

Run:

```bash
python -m pipeline.data_engine
```

If the pipeline is configured correctly, it should complete successfully and ingest validated medicine data into the configured database. The pipeline is designed to work alongside the Flask backend using the shared `DATABASE_URL`.

Expected response

```json
[
  {
    "brand_name": "Crocin",
    "generic_name": "Paracetamol",
    "salt": "Paracetamol",
    "dosage": "500mg",
    "form": "Tablet",
    "brand_price": 35.0,
    "generic_price": 10.0,
    "savings_percent": 71.4
  }
]
```

---

# Troubleshooting

## relation "brands" does not exist

The database schema has not been created.

Run `backend/database/schema.sql` using the Supabase SQL Editor.

---

## Authentication Failed

Verify that:

- `DATABASE_URL` is correct
- Database password is correct
- Session Pooler connection string is being used

---

## Connection Timeout

Use the **Session Pooler** connection string instead of the Direct Connection.

---

## ModuleNotFoundError

Install dependencies again.

```bash
pip install -r requirements.txt
```

---

# Project Structure

```
medsave/
├── backend/
│   ├── app.py
│   ├── database/
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── requirements.txt
│   ├── seed_data.py
│   └── .env
├── pipeline/
├── frontend/
└── docs/
    └── DATABASE_SETUP.md
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/data/SCHEMA_CHANGELOG.md` | Authoritative history of database schema evolution |
| `docs/data/FUTURE_DATA_EXPANSION.md` | Long-term data expansion roadmap |
| `docs/data/PIPELINE_ARCHITECTURE.md` | ETL architecture |
| `pipeline/README.md` | MedSave Data Engine |

> **Note:** `SCHEMA_CHANGELOG.md` serves as the authoritative record of database evolution and should be updated whenever structural schema changes are introduced.

---

# Recovery Checklist

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Create Supabase project
- [ ] Configure `DATABASE_URL`
- [ ] Run `backend/database/schema.sql`
- [ ] Review `docs/data/SCHEMA_CHANGELOG.md` (when upgrading an existing database)
- [ ] Execute `python backend/seed_data.py`
- [ ] Start backend
- [ ] Verify backend (`/api/search`)
- [ ] Verify Data Engine (`python -m pipeline.data_engine`)

