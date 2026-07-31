# MedSave

### Affordable Medicines. Smarter Choices.

**Medicine Price Comparison & Generic Alternative Discovery Platform**

MedSave is an intelligent healthcare platform that helps users discover affordable generic alternatives to branded medicines, estimate potential savings, and locate nearby Jan Aushadhi Kendras.

Built with the goal of improving medicine affordability and accessibility, MedSave empowers users to make informed healthcare decisions while reducing unnecessary medicine expenditure.

---

## Why MedSave?

For many middle-class families, a medical emergency is not only a health crisis but also a financial one. Medicines often account for a significant portion of treatment costs, while affordable generic alternatives remain underutilized due to limited awareness and accessibility.

MedSave helps users discover cost-effective generic medicines, compare prices, estimate potential savings, and locate nearby Jan Aushadhi Kendras. Our goal is simple: if MedSave can help a family save even ?5,000–?20,000 during a difficult time, we believe it has made a meaningful impact.

## ðŸš€ Setup & Execution Procedure

### 1. Prerequisites
Ensure you have Python installed on your system. You can check this by running:
```bash
python --version
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
If the `database.db` file does not exist or you want to reset the data, run the seed script:
```bash
python backend/seed_data.py
```

### 4. Run the Backend API
Start the Flask server:
```bash
python backend/app.py
```
*The backend will run on `http://127.0.0.1:5000`.*

### 5. Run the Frontend
Since the app uses modern browser features (Geolocation, PWA), it must be served via a web server (not just opened as a file).

Open a **new terminal** and run:
```bash
cd frontend
python -m http.server 8000
```
*The app will then be accessible at `http://localhost:8000`.*

---

## Why MedSave?

For many middle-class families, a medical emergency is not only a health crisis but also a financial one. Medicines often account for a significant portion of treatment costs, while affordable generic alternatives remain underutilized due to limited awareness and accessibility.

MedSave helps users discover cost-effective generic medicines, compare prices, estimate potential savings, and locate nearby Jan Aushadhi Kendras. Our goal is simple: if MedSave can help a family save even ?5,000–?20,000 during a difficult time, we believe it has made a meaningful impact.

## âœ¨ Features
- **Smart Search**: Search by Brand (e.g., Crocin) or Generic (e.g., Paracetamol).
- **Price Analytics**: Visual bar charts comparing Branded vs Generic costs.
- **Interactive Calculator**: Input your dosage to see monthly/yearly savings.
- **Store Locator**: Find Jan Aushadhi stores with integrated Google Maps directions.
- **PWA Ready**: Install the app on your mobile device for pharmacy-ready access.




