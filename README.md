# MedSave | Medicine Price & Savings Checker

MedSave is a modern utility that helps users identify cheaper generic alternatives to branded medicines, calculate potential savings based on their prescriptions, and locate nearby Jan Aushadhi stores.

## Project Structure
- **/backend**: Flask API, SQLite database, and seed data.
- **/frontend**: Vanilla HTML/CSS/JS frontend with Chart.js and PWA support.

---

## 🚀 Setup & Execution Procedure

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

## ✨ Features
- **Smart Search**: Search by Brand (e.g., Crocin) or Generic (e.g., Paracetamol).
- **Price Analytics**: Visual bar charts comparing Branded vs Generic costs.
- **Interactive Calculator**: Input your dosage to see monthly/yearly savings.
- **Store Locator**: Find Jan Aushadhi stores with integrated Google Maps directions.
- **PWA Ready**: Install the app on your mobile device for pharmacy-ready access.
