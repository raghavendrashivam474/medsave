<div align="center">

# 💊 MedSave

### Affordable Medicines. Smarter Choices.

**Medicine Price Comparison & Generic Alternative Discovery Platform**

Helping users discover affordable generic medicines, compare prices, estimate savings, and locate nearby Jan Aushadhi Kendras.

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Google Maps](https://img.shields.io/badge/Google%20Maps-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white)

<br>

![Status](https://img.shields.io/badge/Status-Backend%20Complete-success?style=flat-square)
![Milestone](https://img.shields.io/badge/Milestone-MS7%20Current-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Version](https://img.shields.io/badge/Version-v0.6.0-orange?style=flat-square)

</div>

> *Helping families make informed healthcare decisions while reducing medicine costs.*

MedSave is an intelligent healthcare platform that helps users discover affordable generic alternatives to branded medicines, compare prices, estimate potential savings, and locate nearby Jan Aushadhi Kendras through a reliable, API-driven healthcare platform.

The project now features a feature-complete backend for Phase 1, a structured healthcare data pipeline, and a scalable database foundation. With the backend stabilized after Milestone 6, development is currently focused on building the Phase 1 frontend experience while maintaining a clean separation between the data pipeline, backend services, and user interface.

---

## 🚦 Project Status

**Current Milestone:** Milestone 7 — Frontend MVP

| Component | Status |
|-----------|--------|
| Backend APIs | ✅ Complete |
| Database Schema (v0.5.0) | ✅ Stable |
| Data Pipeline | ✅ Operational |
| Frontend | 🚧 In Progress |
| Hybrid Data Ingestion | 📋 Planned (MS9) |
| Internal Hackathon | 🎯 Phase 1 |

---

## 🎯 Why MedSave?

For many middle-class families, a medical emergency is not only a health crisis but also a financial one. Medicines often account for a significant portion of treatment costs, while affordable generic alternatives remain underutilized due to limited awareness and accessibility.

MedSave helps users discover cost-effective generic medicines, compare prices, estimate potential savings, and locate nearby Jan Aushadhi Kendras.

Our goal is simple: if MedSave can help a family save even **₹5,000–₹20,000** during a difficult time, we believe it has made a meaningful impact.

---

## 🏗️ Architecture Overview

```text
Frontend (HTML/CSS/JavaScript)
            │
            ▼
      Flask REST API
            │
            ▼
 PostgreSQL / SQLite
            ▲
            │
   MedSave Data Engine
            │
            ▼
 Trusted Healthcare Sources
```

---


## ✨ Key Features

- 🔍 **Smart Medicine Search** — Search by brand name or generic medicine with fast API-powered results.
- 💊 **Medicine Details & Comparison** — Explore medicine information, compare branded and generic alternatives, and estimate potential savings.
- 💰 **Savings Estimation** — Calculate expected cost savings by choosing affordable generic medicines.
- 📍 **Store Discovery** — Locate nearby Jan Aushadhi Kendras, filter by location, and view detailed store information.
- 🔄 **Healthcare Data Engine** — Dedicated ETL pipeline with validation, normalization, and expansion-ready hybrid ingestion architecture.
- 🗄️ **Scalable Data Platform** — PostgreSQL for production with SQLite support for local development.
- 🧩 **Modular Backend Architecture** — Stable REST APIs with standardized contracts, comprehensive testing, and clean separation between pipeline, backend, and frontend.

---

## 🔌 Available APIs

- Health API (`/api/health`)
- Medicine Search API (`/api/search`)
- Medicine Details API (`/api/medicine/<id>`)
- Store Listing API (`/api/stores`)
- Store Details API (`/api/stores/<id>`)

---

## 📸 Screenshots

> Screenshots coming soon.

---

## 🔄 How MedSave Works

Finding affordable medicines shouldn't require medical expertise or hours of research. MedSave simplifies the process into a few intuitive steps while handling the complexity behind the scenes.

| What You Do | What MedSave Does |
|-------------|-------------------|
| Search a medicine | Searches the medicine database |
| Explore branded and generic options | Compares medicines and identifies affordable alternatives |
| Review potential savings | Calculates estimated cost savings |
| Find a nearby Jan Aushadhi Kendra | Locates nearby stores for easy access |
| Make an informed decision | Presents clear and actionable insights |

---

## 📖 Documentation Overview

- Phase 1 Plan
- Database Setup
- Pipeline Architecture
- Frontend Guide
- Data Strategy
- Schema Changelog

---

## 🏗️ Built One Layer at a Time

Every layer in MedSave has a single responsibility, working together to transform a medicine search into meaningful healthcare insights.

| Layer | Technology |
|-------|------------|
| 🎨 Frontend | HTML • CSS • JavaScript |
| ⚙️ Backend | Flask (Modular Architecture) |
| 🗄️ Database | PostgreSQL • SQLite |
| 🔄 Data Engine | Custom ETL Pipeline |
| 📊 Visualization | Chart.js |
| 📍 Maps | Google Maps API |

---

## 📂 Project Structure

```text
medsave/
├── backend/
│   ├── api/
│   ├── database/
│   ├── middleware/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── main.js
│   ├── manifest.json
│   └── sw.js
│
├── pipeline/
│   ├── entities/
│   ├── sources/
│   ├── parsers/
│   ├── normalizers/
│   ├── validators/
│   ├── loaders/
│   ├── raw/
│   ├── processed/
│   ├── data_engine.py
│   └── README.md
│
├── docs/
│   ├── data/
│   ├── frontend/
│   └── DATABASE_SETUP.md
│
├── scripts/
├── .gitignore
├── PHASE_1_PLAN.md
└── README.md
```

The repository follows a modular architecture with clear separation of concerns:

- **backend/** — Flask REST API, business logic, and database integration.
- **frontend/** — Progressive Web App (PWA) interface.
- **pipeline/** — Independent ETL Data Engine for acquisition, normalization, validation, and loading.
- **docs/** — Project architecture, planning, database, frontend, and data documentation.
- **scripts/** — Development and utility scripts.

---

## 🚀 Getting Started

### Prerequisites

Before running MedSave, ensure you have:

- Python 3.10 or later
- Git
- PostgreSQL (recommended)
- A modern web browser
- (Optional) A Python virtual environment

---

### Installation

Clone the repository:

```bash
git clone https://github.com/raghavendrashivam474/medsave.git
cd medsave
```

---

### Create a Virtual Environment

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Configure the Database

Create a `.env` file inside the `backend/` directory.

```env
DATABASE_URL=your_database_connection_string
```

---

### Initialize the Database

Create the schema and seed the initial data.

```bash
python backend/database/seed_data.py
```

---

### Run the Data Engine

The Data Engine imports, normalizes, validates and loads medicine data into the database.

```bash
python -m pipeline.data_engine
```

---

### Run the Backend

```bash
python backend/app.py
```

The backend will be available at:

```text
http://127.0.0.1:5000
```

---

### Run the Frontend

Open another terminal:

```bash
cd frontend
python -m http.server 8000
```

Open:

```text
http://localhost:8000
```

---

## 📚 Documentation

MedSave follows a documentation-first approach. Design decisions, architecture, sprint reports, and implementation guides are maintained alongside the source code to make the project easy to understand and continue.

| Document / Directory | Purpose |
|----------------------|---------|
| `PHASE_1_PLAN.md` | Master roadmap and execution plan for Phase 1 |
| `docs/planning/` | Planning documents, milestones, and checklists |
| `docs/development/` | Sprint reports and development logs |
| `docs/frontend/` | Frontend implementation guides and UI planning |
| `docs/data/` | Comprehensive data engineering documentation including architecture, data flow, strategy, source evaluation,     audits, limitations, and expansion roadmap |
| `docs/DATABASE_SETUP.md` | Database configuration and setup guide |
| `pipeline/README.md` | Overview of the MedSave Data Engine architecture, pipeline layers, and extension guidelines |

### Data Documentation

The `docs/data/` directory contains dedicated documentation for the complete data engineering workflow, including:

- Data Strategy
- Data Flow
- Pipeline Architecture
- Data Sources Evaluation
- Dataset Audit
- Dataset Limitations
- Future Data Expansion Roadmap

Together, these documents describe how medicine data is acquired, processed, validated, stored, and expanded over time.

As MedSave evolves, this documentation will continue to grow with API references, deployment guides, architectural decisions, and contributor resources.

---

## 🚀 Future Vision

MedSave is being designed as a long-term healthcare platform rather than a single-purpose medicine search application.

Future milestones will introduce:

- Hybrid healthcare data ingestion
- Automated dataset synchronization
- Price history and trend tracking
- AI-assisted medicine discovery
- Enhanced location intelligence
- Expanded healthcare datasets

---

## 🛣️ Roadmap

### 🟢 Phase 1 — Engineering Foundation *(~31% Complete)*

- [x] Repository Foundation
- [x] Repository Architecture
- [x] Modular Backend Architecture
- [x] Database Connectivity
- [x] ETL Pipeline Foundation
- [x] Data Normalization
- [x] Data Validation Layer
- [x] Data Strategy & Documentation
- [ ] Database Evolution
- [ ] Backend Expansion
- [ ] Frontend Modernization
- [ ] Integration Testing
- [ ] SIH Phase 1 Submission

---

### 🟡 Phase 2 — Product Expansion

- [ ] Official Jan Aushadhi Dataset Integration
- [ ] Real Pharmacy Dataset
- [ ] Maps & Navigation
- [ ] Authentication
- [ ] User Accounts
- [ ] Favorites & Saved Medicines
- [ ] Notifications

---

### 🔵 Phase 3 — Intelligent Healthcare Platform

- [ ] AI Medicine Assistant
- [ ] Medicine Recommendations
- [ ] Prescription Management
- [ ] Pharmacy Integration
- [ ] Analytics Dashboard
- [ ] Multi-language Support
- [ ] Production Deployment

---

---

## 🤝 Contributing

Contributions, suggestions, and constructive feedback are always welcome.

If you'd like to contribute:

1. Fork the repository.
2. Create a new feature branch.
3. Make your changes with clear, focused commits.
4. Submit a pull request with a concise description of your improvements.

Please ensure new features are documented and follow the existing project structure whenever possible.

---

## 👥 Team

MedSave is being built by a team of engineering students passionate about making healthcare information more affordable and accessible.

Together, we combine software engineering, research, UI/UX design, and data-driven thinking to build practical solutions that create meaningful social impact.

---

## 📄 License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software in accordance with the terms of the license. See the `LICENSE` file for more information.

---

<div align="center">

Made with ❤️ to make healthcare more affordable.

</div>


