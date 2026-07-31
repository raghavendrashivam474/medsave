# MedSave Database Setup

This guide explains how to recreate the MedSave PostgreSQL database from scratch.

---

## Prerequisites

- Python 3.13+
- PostgreSQL Database (Supabase recommended)
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
> **Note:** Both the Flask backend and the MedSave Data Engine use the same `DATABASE_URL`. This ensures the ETL pipeline and REST API always operate on the same database.
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

## 7. Seed Initial Data

Run

```bash
python backend/seed_data.py
```

Expected output:

```text
Seeding PostgreSQL database...
Database seeded successfully!
```

---

## 8. Start the Backend

```bash
python backend/app.py
```

Expected output:

```text
Running on http://127.0.0.1:5000
```

---

## 9. Verify Installation

Open

```
http://127.0.0.1:5000/api/search?q=crocin
```
## 10. Verify the Data Engine

Run:

```bash
python -m pipeline.data_engine
```

If the pipeline is configured correctly, it should complete successfully and report the number of medicines and brands processed.

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

# Recovery Checklist

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Create Supabase project
- [ ] Configure `DATABASE_URL`
- [ ] Run `backend/database/schema.sql`
- [ ] Execute `python backend/seed_data.py`
- [ ] Start backend
- [ ] Verify `/api/search`