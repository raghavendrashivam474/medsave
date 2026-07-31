# MedSave

### Affordable Medicines. Smarter Choices.

**Medicine Price Comparison & Generic Alternative Discovery Platform**

MedSave is an intelligent healthcare platform that helps users discover affordable generic alternatives to branded medicines, estimate potential savings, and locate nearby Jan Aushadhi Kendras.

Built with the goal of improving medicine affordability and accessibility, MedSave empowers users to make informed healthcare decisions while reducing unnecessary medicine expenditure.

---

## Why MedSave?

For many middle-class families, a medical emergency is not only a health crisis but also a financial one. Medicines often account for a significant portion of treatment costs, while affordable generic alternatives remain underutilized due to limited awareness and accessibility.

MedSave helps users discover cost-effective generic medicines, compare prices, estimate potential savings, and locate nearby Jan Aushadhi Kendras. Our goal is simple: if MedSave can help a family save even ₹5,000–₹20,000 during a difficult time, we believe it has made a meaningful impact.

## Key Features

- **Smart Search**: Search by Brand (e.g., Crocin) or Generic (e.g., Paracetamol).
- **Price Analytics**: Visual bar charts comparing Branded vs Generic costs.
- **Interactive Calculator**: Input your dosage to see monthly/yearly savings.
- **Store Locator**: Find Jan Aushadhi stores with integrated Google Maps directions.
- **PWA Ready**: Install the app on your mobile device for pharmacy-ready access.

## How MedSave Works

Finding affordable medicines shouldn't require medical expertise or hours of research.
MedSave simplifies the process into a few intuitive steps while handling the complexity behind the scenes.

| What You Do | What MedSave Does |
|-------------|-------------------|
| Search a medicine | Searches the medicine database |
| Explore branded and generic options | Compares medicines and identifies affordable alternatives |
| Review potential savings | Calculates estimated cost savings |
| Find a nearby Jan Aushadhi Kendra | Locates nearby stores for easy access |
| Make an informed decision | Presents clear and actionable insights |

## Built One Layer at a Time

Every layer in MedSave has a single responsibility, working together to transform a medicine search into meaningful healthcare insights.

- **Presentation** — HTML, CSS, JavaScript
- **Application** — Flask
- **Data** — SQLite
- **Insights** — Chart.js
- **Accessibility** — Google Maps API

---

## Project Structure

```text
medsave/
├── backend/          # Flask backend and API
├── frontend/         # Web interface
├── docs/             # Project documentation
├── pipeline/         # Data processing and ETL
├── README.md         # Project overview
└── PHASE_1_PLAN.md   # Phase 1 implementation roadmap
```

The repository is organized with a clear separation of responsibilities. Each directory focuses on a specific aspect of the project, making MedSave easier to understand, maintain, and extend as new features are introduced.

---

## Getting Started

### Prerequisites

Before running MedSave, ensure the following tools are installed:

- Python 3.10 or later
- Git
- A modern web browser (Chrome, Edge, or Firefox)

### Installation

Clone the repository:

```bash
git clone <repository-url>
cd medsave
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Initialize the Database

Populate the local database with sample medicine data:

```bash
python backend/seed_data.py
```

### Run the Backend

Start the Flask development server:

```bash
python backend/app.py
```

The backend will be available at:

```text
http://127.0.0.1:5000
```

### Run the Frontend

Open a new terminal and serve the frontend:

```bash
cd frontend
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

---

## Documentation

Additional project documentation is available in the `docs/` directory.

| Document | Description |
|----------|-------------|
| `PHASE_1_PLAN.md` | Phase 1 development roadmap and implementation plan |
| `SPRINT_2.2_REPORT.md` | Sprint progress and development report |
| `DATABASE_SETUP.md` | Database configuration and setup instructions |

As MedSave evolves, the documentation will continue to expand with architecture guides, API references, deployment instructions, and contributor resources.

---

## Roadmap

### Phase 1 — Foundation
- [x] Medicine search
- [x] Generic medicine discovery
- [x] Price comparison
- [x] Savings calculator
- [x] Jan Aushadhi locator
- [x] Progressive Web App support

### Phase 2 — Intelligence
- [ ] Personalized medicine recommendations
- [ ] Medicine availability prediction
- [ ] AI-powered medicine assistant
- [ ] Advanced analytics dashboard

### Phase 3 — Ecosystem
- [ ] User accounts and saved medicines
- [ ] Prescription management
- [ ] Pharmacy integration
- [ ] Multi-language support

