"""
backend/database/seed_data.py

Canonical database seed script for MedSave (v0.5.0).
Seeds 550+ generic medicines, 1350+ brand alternatives, and Jan Aushadhi stores.

Dual Backend Support:
- PostgreSQL (Production / Supabase if DATABASE_URL is set)
- SQLite (Local fallback: backend/database.db)

Usage:
    python backend/database/seed_data.py
"""

import os
import re
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_SQLITE_PATH = BASE_DIR / "backend" / "database.db"
SCHEMA_PATH = BASE_DIR / "backend" / "database" / "schema.sql"

# Complete essential medicines catalog
CATALOG = [
    # 1. Analgesics, NSAIDs & Antipyretics
    {
        "salt": "Paracetamol", "generic": "Paracetamol", "cat": "Analgesic / Antipyretic", "sch": "OTC",
        "variants": [
            ("500mg", "Tablet", 1.20, [("Crocin 500", 2.50, "GSK"), ("Dolo 500", 2.20, "Micro Labs"), ("Calpol 500", 2.40, "GSK")]),
            ("650mg", "Tablet", 1.80, [("Dolo 650", 3.40, "Micro Labs"), ("Calpol 650", 3.30, "GSK"), ("Pacimol 650", 3.10, "Ipca")]),
            ("1000mg", "Tablet", 3.00, [("Crocin 1000", 6.50, "GSK"), ("Dolo 1000", 6.00, "Micro Labs")]),
            ("120mg/5ml", "Syrup", 18.00, [("Calpol Pead Suspension", 45.00, "GSK"), ("Crocin Pead Drops", 42.00, "GSK")]),
            ("250mg/5ml", "Syrup", 24.00, [("Calpol 250 DS", 55.00, "GSK"), ("Dolo 250 Suspension", 52.00, "Micro Labs")]),
            ("150mg/ml", "Injection", 8.50, [("Paracip IV", 45.00, "Cipla"), ("Perfalgan IV", 120.00, "Bristol Myers")])
        ]
    },
    {
        "salt": "Ibuprofen + Paracetamol", "generic": "Ibuprofen + Paracetamol", "cat": "Analgesic / Anti-inflammatory", "sch": "Schedule H",
        "variants": [
            ("400mg + 325mg", "Tablet", 2.20, [("Combiflam", 5.20, "Sanofi"), ("Flexon", 4.80, "Aristo"), ("Ibugesic Plus", 4.50, "Cipla")]),
            ("100mg + 162.5mg/5ml", "Syrup", 22.00, [("Combiflam Suspension", 52.00, "Sanofi"), ("Flexon Suspension", 48.00, "Aristo")])
        ]
    },
    {
        "salt": "Aceclofenac + Paracetamol", "generic": "Aceclofenac + Paracetamol", "cat": "Analgesic / Anti-inflammatory", "sch": "Schedule H",
        "variants": [
            ("100mg + 325mg", "Tablet", 2.80, [("Zerodol-P", 7.50, "Ipca"), ("Hifenac-P", 7.20, "Intas"), ("Aceclo Plus", 6.80, "Aristo")]),
            ("100mg + 500mg", "Tablet", 3.20, [("Dolokind Plus", 8.00, "Mankind"), ("Alcephin-P", 7.80, "Alembic")])
        ]
    },
    {
        "salt": "Aceclofenac + Paracetamol + Serratiopeptidase", "generic": "Aceclofenac + Paracetamol + Serratiopeptidase", "cat": "Anti-inflammatory Enzyme", "sch": "Schedule H",
        "variants": [
            ("100mg + 325mg + 15mg", "Tablet", 4.50, [("Zerodol-SP", 13.50, "Ipca"), ("Hifenac-SP", 13.00, "Intas"), ("Signoflam", 12.80, "Lupin")])
        ]
    },
    {
        "salt": "Diclofenac Sodium", "generic": "Diclofenac", "cat": "NSAID", "sch": "Schedule H",
        "variants": [
            ("50mg", "Tablet", 1.50, [("Voveran 50", 6.20, "Novartis"), ("Dicloran 50", 5.50, "Sun Pharma")]),
            ("75mg", "Tablet", 2.50, [("Voveran SR 75", 9.80, "Novartis"), ("Dynapar SR 75", 9.50, "Troikaa")]),
            ("100mg", "Tablet", 3.20, [("Voveran SR 100", 12.50, "Novartis"), ("Jonac CR 100", 11.80, "Zydus")]),
            ("25mg/ml", "Injection", 4.00, [("Voveran AQ Inj", 28.00, "Novartis"), ("Dynapar AQ", 26.00, "Troikaa")]),
            ("1% w/w", "Gel", 25.00, [("Volini Gel 30g", 110.00, "Sun Pharma"), ("Omnigel 30g", 105.00, "Cipla")])
        ]
    },
    {
        "salt": "Tramadol Hydrochloride", "generic": "Tramadol", "cat": "Opioid Analgesic", "sch": "Schedule H1",
        "variants": [
            ("50mg", "Capsule", 3.50, [("Tramazac 50", 12.00, "Zydus"), ("Ultram 50", 15.00, "Janssen")]),
            ("100mg", "Tablet", 6.00, [("Tramazac SR 100", 22.00, "Zydus"), ("Contramal 100", 26.00, "Abbott")]),
            ("50mg/ml", "Injection", 8.00, [("Tramazac 2ml Inj", 35.00, "Zydus"), ("Supridol Inj", 32.00, "Neon")])
        ]
    },
    {
        "salt": "Etoricoxib", "generic": "Etoricoxib", "cat": "Cox-2 Inhibitor NSAID", "sch": "Schedule H",
        "variants": [
            ("60mg", "Tablet", 4.20, [("Nucoxia 60", 14.50, "Zydus"), ("Arcoxia 60", 18.00, "MSD"), ("Etoshine 60", 13.80, "Sun Pharma")]),
            ("90mg", "Tablet", 5.50, [("Nucoxia 90", 18.20, "Zydus"), ("Arcoxia 90", 23.00, "MSD"), ("Etoshine 90", 17.50, "Sun Pharma")]),
            ("120mg", "Tablet", 7.00, [("Nucoxia 120", 24.00, "Zydus"), ("Etoshine 120", 22.50, "Sun Pharma")])
        ]
    },
    {
        "salt": "Mefenamic Acid + Dicyclomine", "generic": "Mefenamic Acid + Dicyclomine", "cat": "Antispasmodic", "sch": "Schedule H",
        "variants": [
            ("250mg + 10mg", "Tablet", 2.00, [("Meftal-Spas", 6.00, "Blue Cross"), ("Colimex", 5.50, "Shreya"), ("Spasmonil Plus", 5.20, "Cipla")]),
            ("500mg + 20mg", "Tablet", 3.50, [("Meftal-Spas Forte", 9.50, "Blue Cross"), ("Dysmen Forte", 8.50, "Mankind")])
        ]
    },
    {
        "salt": "Naproxen", "generic": "Naproxen", "cat": "NSAID", "sch": "Schedule H",
        "variants": [
            ("250mg", "Tablet", 2.80, [("Naprosyn 250", 7.80, "RPG"), ("Xenobid 250", 7.20, "Sun Pharma")]),
            ("500mg", "Tablet", 4.80, [("Naprosyn 500", 13.50, "RPG"), ("Xenobid 500", 12.80, "Sun Pharma")])
        ]
    },

    # 2. Antibiotics, Antifungals & Antivirals
    {
        "salt": "Amoxicillin", "generic": "Amoxicillin", "cat": "Penicillin Antibiotic", "sch": "Schedule H",
        "variants": [
            ("250mg", "Capsule", 2.20, [("Novamox 250", 6.80, "Cipla"), ("Mox 250", 6.50, "Sun Pharma")]),
            ("500mg", "Capsule", 4.00, [("Novamox 500", 12.50, "Cipla"), ("Mox 500", 12.00, "Sun Pharma"), ("Almox 500", 11.80, "Alkem")]),
            ("125mg/5ml", "Syrup", 25.00, [("Novamox Dry Syrup", 62.00, "Cipla"), ("Mox Dry Syrup", 58.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Amoxicillin + Clavulanic Acid", "generic": "Amoxicillin + Clavulanate", "cat": "Broad Spectrum Antibiotic", "sch": "Schedule H",
        "variants": [
            ("375mg", "Tablet", 6.50, [("Augmentin 375", 22.00, "GSK"), ("Clavam 375", 20.00, "Alkem"), ("Moxikind-CV 375", 19.50, "Mankind")]),
            ("625mg", "Tablet", 9.80, [("Augmentin 625 Duo", 32.50, "GSK"), ("Clavam 625", 30.00, "Alkem"), ("Moxikind-CV 625", 28.50, "Mankind"), ("Advent 625", 29.00, "Cipla")]),
            ("1000mg", "Tablet", 16.00, [("Augmentin 1g", 52.00, "GSK"), ("Clavam 1g", 48.00, "Alkem")]),
            ("1.2g", "Injection", 32.00, [("Augmentin 1.2g IV", 165.00, "GSK"), ("Clavam 1.2g IV", 150.00, "Alkem")]),
            ("228.5mg/5ml", "Syrup", 35.00, [("Augmentin Duo Dry Syrup", 98.00, "GSK"), ("Clavam Dry Syrup", 90.00, "Alkem")])
        ]
    },
    {
        "salt": "Azithromycin", "generic": "Azithromycin", "cat": "Macrolide Antibiotic", "sch": "Schedule H",
        "variants": [
            ("250mg", "Tablet", 5.50, [("Azee 250", 16.00, "Cipla"), ("Azithral 250", 15.50, "Alembic"), ("Zithrox 250", 15.00, "Macleods")]),
            ("500mg", "Tablet", 10.50, [("Azee 500", 28.50, "Cipla"), ("Azithral 500", 28.00, "Alembic"), ("Zady 500", 26.50, "Mankind")]),
            ("100mg/5ml", "Syrup", 30.00, [("Azee 100 Suspension", 75.00, "Cipla"), ("Azithral Junior Drops", 72.00, "Alembic")]),
            ("200mg/5ml", "Syrup", 42.00, [("Azee 200 Suspension", 105.00, "Cipla"), ("Azithral 200 Suspension", 100.00, "Alembic")])
        ]
    },
    {
        "salt": "Cefixime", "generic": "Cefixime", "cat": "Cephalosporin Antibiotic", "sch": "Schedule H1",
        "variants": [
            ("100mg", "Tablet", 4.50, [("Zifi 100", 12.00, "FDC"), ("Taxim-O 100", 11.50, "Alkem"), ("Mahacef 100", 11.00, "Mankind")]),
            ("200mg", "Tablet", 7.80, [("Zifi 200", 21.50, "FDC"), ("Taxim-O 200", 20.00, "Alkem"), ("Mahacef 200", 19.50, "Mankind"), ("Cefspan 200", 22.00, "Glaxo")]),
            ("400mg", "Tablet", 15.00, [("Zifi 400", 42.00, "FDC"), ("Taxim-O 400", 39.00, "Alkem")]),
            ("50mg/5ml", "Syrup", 28.00, [("Zifi 50 Dry Syrup", 68.00, "FDC"), ("Taxim-O 50 Dry Syrup", 65.00, "Alkem")])
        ]
    },
    {
        "salt": "Ciprofloxacin", "generic": "Ciprofloxacin", "cat": "Fluoroquinolone Antibiotic", "sch": "Schedule H1",
        "variants": [
            ("250mg", "Tablet", 2.20, [("Ciplox 250", 5.50, "Cipla"), ("Cifran 250", 5.20, "Sun Pharma")]),
            ("500mg", "Tablet", 3.80, [("Ciplox 500", 10.50, "Cipla"), ("Cifran 500", 10.00, "Sun Pharma"), ("Alcipro 500", 9.50, "Alkem")]),
            ("0.3% w/v", "Eye/Ear Drops", 12.00, [("Ciplox Eye Drops 10ml", 35.00, "Cipla"), ("Cifran Eye Drops", 32.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Levofloxacin", "generic": "Levofloxacin", "cat": "Fluoroquinolone Antibiotic", "sch": "Schedule H1",
        "variants": [
            ("250mg", "Tablet", 3.50, [("Levomac 250", 8.50, "Macleods"), ("Loxof 250", 9.00, "Sun Pharma")]),
            ("500mg", "Tablet", 5.80, [("Levomac 500", 15.00, "Macleods"), ("Loxof 500", 16.50, "Sun Pharma"), ("Glevo 500", 14.50, "Glenmark")]),
            ("750mg", "Tablet", 8.20, [("Levomac 750", 22.00, "Macleods"), ("Loxof 750", 24.50, "Sun Pharma")])
        ]
    },
    {
        "salt": "Doxycycline", "generic": "Doxycycline", "cat": "Tetracycline Antibiotic", "sch": "Schedule H",
        "variants": [
            ("100mg", "Capsule", 2.50, [("Doxicip 100", 7.50, "Cipla"), ("Doxt-SL", 8.20, "Dr. Reddy's"), ("Microdox-LBX", 8.00, "Micro Labs")])
        ]
    },
    {
        "salt": "Metronidazole", "generic": "Metronidazole", "cat": "Antiprotozoal / Antibacterial", "sch": "Schedule H",
        "variants": [
            ("200mg", "Tablet", 0.90, [("Flagyl 200", 2.40, "Abbott"), ("Metrogyl 200", 2.30, "J.B. Chemicals")]),
            ("400mg", "Tablet", 1.40, [("Flagyl 400", 3.60, "Abbott"), ("Metrogyl 400", 3.50, "J.B. Chemicals")]),
            ("500mg/100ml", "Injection", 14.00, [("Metrogyl IV Infusion", 42.00, "J.B. Chemicals"), ("Flagyl Infusion", 45.00, "Abbott")])
        ]
    },
    {
        "salt": "Fluconazole", "generic": "Fluconazole", "cat": "Antifungal", "sch": "Schedule H",
        "variants": [
            ("150mg", "Tablet", 4.50, [("Forcan 150", 15.00, "Cipla"), ("Syscan 150", 14.50, "Torrent"), ("Flucos 150", 13.80, "AstraZeneca")]),
            ("200mg", "Tablet", 6.50, [("Forcan 200", 22.00, "Cipla"), ("Syscan 200", 20.00, "Torrent")]),
            ("400mg", "Tablet", 12.00, [("Forcan 400", 42.00, "Cipla"), ("Syscan 400", 40.00, "Torrent")])
        ]
    },
    {
        "salt": "Itraconazole", "generic": "Itraconazole", "cat": "Antifungal", "sch": "Schedule H",
        "variants": [
            ("100mg", "Capsule", 9.50, [("Canditral 100", 26.00, "Glenmark"), ("Itracol 100", 24.00, "Sun Pharma"), ("Sporanox 100", 45.00, "Janssen")]),
            ("200mg", "Capsule", 16.50, [("Canditral 200", 48.00, "Glenmark"), ("Itrasys 200", 44.00, "Systopic"), ("Kandit 200", 42.00, "Lupin")])
        ]
    },
    {
        "salt": "Acyclovir", "generic": "Acyclovir", "cat": "Antiviral", "sch": "Schedule H",
        "variants": [
            ("200mg", "Tablet", 3.80, [("Zovirax 200", 12.00, "GSK"), ("Acivir 200", 10.50, "Cipla")]),
            ("400mg", "Tablet", 6.50, [("Zovirax 400", 21.00, "GSK"), ("Acivir 400", 18.00, "Cipla")]),
            ("800mg", "Tablet", 11.50, [("Zovirax 800", 38.00, "GSK"), ("Acivir 800", 32.00, "Cipla")]),
            ("5% w/w", "Ointment", 22.00, [("Acivir Cream 5g", 68.00, "Cipla"), ("Zovirax Cream", 85.00, "GSK")])
        ]
    },

    # 3. Cardiovascular & Antihypertensives
    {
        "salt": "Atorvastatin", "generic": "Atorvastatin", "cat": "Lipid Lowering / Statin", "sch": "Schedule H",
        "variants": [
            ("10mg", "Tablet", 2.80, [("Atorva 10", 9.80, "Zydus"), ("Storvas 10", 9.50, "Sun Pharma"), ("Lipitor 10", 25.00, "Pfizer"), ("Tonact 10", 9.00, "Lupin")]),
            ("20mg", "Tablet", 4.80, [("Atorva 20", 16.50, "Zydus"), ("Storvas 20", 16.00, "Sun Pharma"), ("Lipitor 20", 38.00, "Pfizer"), ("Tonact 20", 15.50, "Lupin")]),
            ("40mg", "Tablet", 8.20, [("Atorva 40", 28.00, "Zydus"), ("Storvas 40", 27.50, "Sun Pharma"), ("Lipitor 40", 62.00, "Pfizer")]),
            ("80mg", "Tablet", 14.00, [("Atorva 80", 48.00, "Zydus"), ("Storvas 80", 46.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Rosuvastatin", "generic": "Rosuvastatin", "cat": "Lipid Lowering / Statin", "sch": "Schedule H",
        "variants": [
            ("5mg", "Tablet", 3.20, [("Rosuvas 5", 10.50, "Sun Pharma"), ("Rozavel 5", 10.00, "Sun Pharma"), ("Crestor 5", 28.00, "AstraZeneca")]),
            ("10mg", "Tablet", 5.50, [("Rosuvas 10", 18.00, "Sun Pharma"), ("Rozavel 10", 17.50, "Sun Pharma"), ("Crestor 10", 42.00, "AstraZeneca"), ("Novastat 10", 17.00, "Lupin")]),
            ("20mg", "Tablet", 9.80, [("Rosuvas 20", 32.00, "Sun Pharma"), ("Rozavel 20", 31.00, "Sun Pharma"), ("Crestor 20", 72.00, "AstraZeneca")]),
            ("40mg", "Tablet", 16.00, [("Rosuvas 40", 54.00, "Sun Pharma"), ("Rozavel 40", 52.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Telmisartan", "generic": "Telmisartan", "cat": "Antihypertensive (ARB)", "sch": "Schedule H",
        "variants": [
            ("20mg", "Tablet", 2.20, [("Telma 20", 6.80, "Glenmark"), ("Telmikind 20", 5.50, "Mankind"), ("Micardis 20", 18.00, "Boehringer")]),
            ("40mg", "Tablet", 3.50, [("Telma 40", 11.80, "Glenmark"), ("Telmikind 40", 9.50, "Mankind"), ("Telsartan 40", 11.00, "Dr. Reddy's"), ("Micardis 40", 30.00, "Boehringer")]),
            ("80mg", "Tablet", 6.20, [("Telma 80", 19.50, "Glenmark"), ("Telmikind 80", 16.00, "Mankind"), ("Micardis 80", 48.00, "Boehringer")])
        ]
    },
    {
        "salt": "Telmisartan + Amlodipine", "generic": "Telmisartan + Amlodipine", "cat": "Antihypertensive Combination", "sch": "Schedule H",
        "variants": [
            ("40mg + 5mg", "Tablet", 4.20, [("Telma-AM", 13.50, "Glenmark"), ("Telmikind-AM", 11.00, "Mankind"), ("Twynsta 40/5", 35.00, "Boehringer")]),
            ("80mg + 5mg", "Tablet", 7.00, [("Telma-AM 80", 22.00, "Glenmark"), ("Twynsta 80/5", 52.00, "Boehringer")])
        ]
    },
    {
        "salt": "Telmisartan + Hydrochlorothiazide", "generic": "Telmisartan + Hydrochlorothiazide", "cat": "Antihypertensive Diuretic", "sch": "Schedule H",
        "variants": [
            ("40mg + 12.5mg", "Tablet", 4.00, [("Telma-H", 12.80, "Glenmark"), ("Telmikind-H", 10.50, "Mankind"), ("Micardis-HCT", 34.00, "Boehringer")]),
            ("80mg + 12.5mg", "Tablet", 6.80, [("Telma-H 80", 21.00, "Glenmark"), ("Telmikind-H 80", 17.50, "Mankind")])
        ]
    },
    {
        "salt": "Amlodipine Besylate", "generic": "Amlodipine", "cat": "Calcium Channel Blocker", "sch": "Schedule H",
        "variants": [
            ("2.5mg", "Tablet", 1.20, [("Amlong 2.5", 3.80, "Micro Labs"), ("Norvasc 2.5", 9.00, "Pfizer"), ("Stamlo 2.5", 3.60, "Dr. Reddy's")]),
            ("5mg", "Tablet", 1.80, [("Amlong 5", 5.80, "Micro Labs"), ("Norvasc 5", 14.50, "Pfizer"), ("Stamlo 5", 5.50, "Dr. Reddy's"), ("Amlovas 5", 5.20, "MacLeods")]),
            ("10mg", "Tablet", 3.20, [("Amlong 10", 9.80, "Micro Labs"), ("Norvasc 10", 24.00, "Pfizer"), ("Stamlo 10", 9.20, "Dr. Reddy's")])
        ]
    },
    {
        "salt": "Cilnidipine", "generic": "Cilnidipine", "cat": "Calcium Channel Blocker (L/N-type)", "sch": "Schedule H",
        "variants": [
            ("5mg", "Tablet", 2.80, [("Cilacar 5", 8.50, "J.B. Chemicals"), ("Nexsartan 5", 8.00, "Torrent"), ("Cilaheart 5", 7.80, "Mankind")]),
            ("10mg", "Tablet", 4.50, [("Cilacar 10", 14.00, "J.B. Chemicals"), ("Nexsartan 10", 13.50, "Torrent"), ("Cilaheart 10", 12.50, "Mankind")]),
            ("20mg", "Tablet", 7.50, [("Cilacar 20", 24.00, "J.B. Chemicals"), ("Cilaheart 20", 21.00, "Mankind")])
        ]
    },
    {
        "salt": "Metoprolol Succinate", "generic": "Metoprolol Succinate ER", "cat": "Beta Blocker", "sch": "Schedule H",
        "variants": [
            ("12.5mg", "Tablet", 2.00, [("Betaloc 12.5", 5.50, "AstraZeneca"), ("Metolar XR 12.5", 5.20, "Cipla"), ("Starpress XL 12.5", 5.00, "Lupin")]),
            ("25mg", "Tablet", 3.20, [("Betaloc 25", 9.20, "AstraZeneca"), ("Metolar XR 25", 8.80, "Cipla"), ("Starpress XL 25", 8.50, "Lupin"), ("Seloken XL 25", 9.00, "AstraZeneca")]),
            ("50mg", "Tablet", 5.00, [("Betaloc 50", 15.50, "AstraZeneca"), ("Metolar XR 50", 14.80, "Cipla"), ("Starpress XL 50", 14.00, "Lupin")]),
            ("100mg", "Tablet", 8.50, [("Betaloc 100", 26.00, "AstraZeneca"), ("Metolar XR 100", 24.50, "Cipla"), ("Starpress XL 100", 23.00, "Lupin")])
        ]
    },
    {
        "salt": "Bisoprolol Fumarate", "generic": "Bisoprolol", "cat": "Beta Blocker", "sch": "Schedule H",
        "variants": [
            ("2.5mg", "Tablet", 2.50, [("Concor 2.5", 7.50, "Merck"), ("Bisoheart 2.5", 6.80, "Mankind"), ("Corbis 2.5", 7.00, "Unichem")]),
            ("5mg", "Tablet", 4.20, [("Concor 5", 12.80, "Merck"), ("Bisoheart 5", 11.50, "Mankind"), ("Corbis 5", 12.00, "Unichem")])
        ]
    },
    {
        "salt": "Ramipril", "generic": "Ramipril", "cat": "ACE Inhibitor", "sch": "Schedule H",
        "variants": [
            ("2.5mg", "Tablet", 2.00, [("Cardace 2.5", 7.20, "Sanofi"), ("Hopace 2.5", 6.50, "Micro Labs"), ("Ramihart 2.5", 6.00, "Mankind")]),
            ("5mg", "Tablet", 3.40, [("Cardace 5", 12.00, "Sanofi"), ("Hopace 5", 10.80, "Micro Labs"), ("Ramihart 5", 10.00, "Mankind")]),
            ("10mg", "Tablet", 5.80, [("Cardace 10", 21.00, "Sanofi"), ("Hopace 10", 18.50, "Micro Labs")])
        ]
    },
    {
        "salt": "Clopidogrel", "generic": "Clopidogrel", "cat": "Antiplatelet", "sch": "Schedule H",
        "variants": [
            ("75mg", "Tablet", 3.80, [("Plavix 75", 18.00, "Sanofi"), ("Clopilet 75", 11.50, "Sun Pharma"), ("Deplatt 75", 11.00, "Torrent"), ("Ceruvin 75", 10.80, "Ranbaxy")]),
            ("150mg", "Tablet", 7.20, [("Clopilet 150", 22.00, "Sun Pharma"), ("Deplatt 150", 21.00, "Torrent")])
        ]
    },
    {
        "salt": "Aspirin + Clopidogrel", "generic": "Aspirin + Clopidogrel", "cat": "Dual Antiplatelet", "sch": "Schedule H",
        "variants": [
            ("75mg + 75mg", "Capsule", 4.20, [("Clopilet-A 75", 12.80, "Sun Pharma"), ("Deplatt-A 75", 12.20, "Torrent"), ("Ecosprin-AV 75", 13.00, "USV")]),
            ("150mg + 75mg", "Capsule", 5.00, [("Clopilet-A 150", 15.50, "Sun Pharma"), ("Deplatt-A 150", 14.80, "Torrent")])
        ]
    },

    # 4. Antidiabetic Medicines
    {
        "salt": "Metformin Hydrochloride", "generic": "Metformin", "cat": "Antidiabetic (Biguanide)", "sch": "Schedule H",
        "variants": [
            ("500mg", "Tablet", 1.10, [("Glycomet 500", 3.20, "USV"), ("Glucophage 500", 6.50, "Merck"), ("Obimet 500", 3.00, "Abbott"), ("Formin 500", 2.90, "Alkem")]),
            ("500mg SR", "Tablet", 1.40, [("Glycomet 500 SR", 4.10, "USV"), ("Glucophage XR 500", 8.00, "Merck"), ("Cetapin XR 500", 3.90, "Sanofi")]),
            ("850mg", "Tablet", 1.80, [("Glycomet 850", 5.20, "USV"), ("Glucophage 850", 9.80, "Merck"), ("Obimet 850", 4.90, "Abbott")]),
            ("1000mg SR", "Tablet", 2.40, [("Glycomet 1000 SR", 6.80, "USV"), ("Glucophage XR 1000", 14.50, "Merck"), ("Cetapin XR 1000", 6.50, "Sanofi")])
        ]
    },
    {
        "salt": "Glimepiride", "generic": "Glimepiride", "cat": "Antidiabetic (Sulfonylurea)", "sch": "Schedule H",
        "variants": [
            ("1mg", "Tablet", 1.20, [("Amaryl 1mg", 6.50, "Sanofi"), ("Glimy 1mg", 3.80, "Dr. Reddy's"), ("Zoryl 1mg", 3.60, "Intas"), ("Gemer 1", 3.50, "Sun Pharma")]),
            ("2mg", "Tablet", 2.00, [("Amaryl 2mg", 11.20, "Sanofi"), ("Glimy 2mg", 6.20, "Dr. Reddy's"), ("Zoryl 2mg", 5.90, "Intas"), ("Gemer 2", 5.80, "Sun Pharma")]),
            ("3mg", "Tablet", 3.00, [("Amaryl 3mg", 16.00, "Sanofi"), ("Glimy 3mg", 8.80, "Dr. Reddy's"), ("Zoryl 3mg", 8.50, "Intas")]),
            ("4mg", "Tablet", 3.80, [("Amaryl 4mg", 20.50, "Sanofi"), ("Glimy 4mg", 11.00, "Dr. Reddy's"), ("Zoryl 4mg", 10.50, "Intas")])
        ]
    },
    {
        "salt": "Glimepiride + Metformin", "generic": "Glimepiride + Metformin SR", "cat": "Antidiabetic Combination", "sch": "Schedule H",
        "variants": [
            ("1mg + 500mg SR", "Tablet", 2.50, [("Amaryl-M 1mg", 9.80, "Sanofi"), ("Glycomet-GP 1", 7.20, "USV"), ("Gemer 1", 7.00, "Sun Pharma"), ("Zoryl-M 1", 6.80, "Intas")]),
            ("2mg + 500mg SR", "Tablet", 3.20, [("Amaryl-M 2mg", 13.50, "Sanofi"), ("Glycomet-GP 2", 9.50, "USV"), ("Gemer 2", 9.20, "Sun Pharma"), ("Zoryl-M 2", 8.90, "Intas")]),
            ("1mg + 1000mg SR", "Tablet", 3.60, [("Glycomet-GP 1 Forte", 11.00, "USV"), ("Gemer 1 Forte", 10.50, "Sun Pharma")]),
            ("2mg + 1000mg SR", "Tablet", 4.50, [("Glycomet-GP 2 Forte", 13.80, "USV"), ("Gemer 2 Forte", 13.20, "Sun Pharma")])
        ]
    },
    {
        "salt": "Teneligliptin", "generic": "Teneligliptin", "cat": "Antidiabetic (DPP-4 Inhibitor)", "sch": "Schedule H",
        "variants": [
            ("20mg", "Tablet", 4.50, [("Tenglyn 20", 14.50, "Zydus"), ("Ziten 20", 14.00, "Glenmark"), ("Dynaglipt 20", 13.50, "Mankind"), ("Tenalim 20", 13.80, "Sun Pharma")])
        ]
    },
    {
        "salt": "Teneligliptin + Metformin", "generic": "Teneligliptin + Metformin SR", "cat": "Antidiabetic Combination", "sch": "Schedule H",
        "variants": [
            ("20mg + 500mg SR", "Tablet", 5.50, [("Tenglyn-M 500", 17.50, "Zydus"), ("Ziten-M 500", 17.00, "Glenmark"), ("Dynaglipt-M 500", 16.20, "Mankind")]),
            ("20mg + 1000mg SR", "Tablet", 6.80, [("Tenglyn-M 1000", 21.00, "Zydus"), ("Ziten-M 1000", 20.00, "Glenmark")])
        ]
    },
    {
        "salt": "Sitagliptin", "generic": "Sitagliptin", "cat": "Antidiabetic (DPP-4 Inhibitor)", "sch": "Schedule H",
        "variants": [
            ("50mg", "Tablet", 7.50, [("Januvia 50", 28.00, "MSD"), ("Istavel 50", 19.00, "Sun Pharma"), ("Zita 50", 18.50, "Glenmark")]),
            ("100mg", "Tablet", 12.00, [("Januvia 100", 46.00, "MSD"), ("Istavel 100", 32.00, "Sun Pharma"), ("Zita 100", 30.00, "Glenmark")])
        ]
    },
    {
        "salt": "Dapagliflozin", "generic": "Dapagliflozin", "cat": "Antidiabetic (SGLT-2 Inhibitor)", "sch": "Schedule H",
        "variants": [
            ("5mg", "Tablet", 6.50, [("Forxiga 5", 42.00, "AstraZeneca"), ("Oxra 5", 16.50, "Sun Pharma"), ("Dapacip 5", 15.00, "Cipla"), ("Dapanorm 5", 15.50, "Alkem")]),
            ("10mg", "Tablet", 9.80, [("Forxiga 10", 62.00, "AstraZeneca"), ("Oxra 10", 24.00, "Sun Pharma"), ("Dapacip 10", 22.00, "Cipla"), ("Dapanorm 10", 22.50, "Alkem")])
        ]
    },
    {
        "salt": "Empagliflozin", "generic": "Empagliflozin", "cat": "Antidiabetic (SGLT-2 Inhibitor)", "sch": "Schedule H",
        "variants": [
            ("10mg", "Tablet", 8.50, [("Jardiance 10", 54.00, "Boehringer"), ("Gibtulio 10", 24.00, "Lupin"), ("Empaone 10", 22.00, "Cipla")]),
            ("25mg", "Tablet", 14.00, [("Jardiance 25", 72.00, "Boehringer"), ("Gibtulio 25", 34.00, "Lupin"), ("Empaone 25", 32.00, "Cipla")])
        ]
    },
    {
        "salt": "Voglibose", "generic": "Voglibose", "cat": "Alpha-Glucosidase Inhibitor", "sch": "Schedule H",
        "variants": [
            ("0.2mg", "Tablet", 1.80, [("Volibo 0.2", 6.20, "Sun Pharma"), ("Voglimac 0.2", 5.80, "Macleods"), ("PPG 0.2", 5.50, "Torrent")]),
            ("0.3mg", "Tablet", 2.60, [("Volibo 0.3", 8.80, "Sun Pharma"), ("Voglimac 0.3", 8.20, "Macleods"), ("PPG 0.3", 7.80, "Torrent")])
        ]
    },

    # 5. Gastrointestinal & Antacids
    {
        "salt": "Pantoprazole", "generic": "Pantoprazole", "cat": "Proton Pump Inhibitor (PPI)", "sch": "Schedule H",
        "variants": [
            ("20mg", "Tablet", 1.80, [("Pantocid 20", 5.80, "Sun Pharma"), ("Pan 20", 5.50, "Alkem"), ("Pantosec 20", 5.40, "Cipla")]),
            ("40mg", "Tablet", 2.80, [("Pantocid 40", 9.80, "Sun Pharma"), ("Pan 40", 9.50, "Alkem"), ("Pantosec 40", 9.20, "Cipla"), ("Protonix 40", 25.00, "Pfizer")]),
            ("40mg", "Injection", 18.00, [("Pantocid IV 40", 65.00, "Sun Pharma"), ("Pan IV 40", 62.00, "Alkem"), ("Pantosec IV", 60.00, "Cipla")])
        ]
    },
    {
        "salt": "Pantoprazole + Domperidone", "generic": "Pantoprazole + Domperidone SR", "cat": "Antacid & Antiemetic", "sch": "Schedule H",
        "variants": [
            ("40mg + 30mg SR", "Capsule", 4.20, [("Pantocid-D SR", 14.50, "Sun Pharma"), ("Pan-D", 14.20, "Alkem"), ("Pantosec-D SR", 13.80, "Cipla"), ("Dompan SR", 13.50, "Medley")])
        ]
    },
    {
        "salt": "Omeprazole", "generic": "Omeprazole", "cat": "Proton Pump Inhibitor (PPI)", "sch": "Schedule H",
        "variants": [
            ("20mg", "Capsule", 1.50, [("Omez 20", 5.80, "Dr. Reddy's"), ("Ocid 20", 5.50, "Zydus"), ("Prilosec 20", 18.00, "AstraZeneca")]),
            ("40mg", "Capsule", 2.80, [("Omez 40", 9.80, "Dr. Reddy's"), ("Ocid 40", 9.20, "Zydus")])
        ]
    },
    {
        "salt": "Omeprazole + Domperidone", "generic": "Omeprazole + Domperidone", "cat": "Antacid & Antiemetic", "sch": "Schedule H",
        "variants": [
            ("20mg + 10mg", "Capsule", 2.60, [("Omez-D", 8.80, "Dr. Reddy's"), ("Ocid-D", 8.20, "Zydus"), ("Domstal-O", 8.00, "Torrent")])
        ]
    },
    {
        "salt": "Rabeprazole Sodium", "generic": "Rabeprazole", "cat": "Proton Pump Inhibitor (PPI)", "sch": "Schedule H",
        "variants": [
            ("10mg", "Tablet", 1.90, [("Razo 10", 6.50, "Dr. Reddy's"), ("Rablet 10", 6.20, "Lupin"), ("Aciphex 10", 16.00, "Eisai")]),
            ("20mg", "Tablet", 3.20, [("Razo 20", 11.50, "Dr. Reddy's"), ("Rablet 20", 11.00, "Lupin"), ("Happi 20", 10.80, "Zydus"), ("Parit 20", 11.20, "Eisai")])
        ]
    },
    {
        "salt": "Rabeprazole + Domperidone", "generic": "Rabeprazole + Domperidone SR", "cat": "Antacid & Antiemetic", "sch": "Schedule H",
        "variants": [
            ("20mg + 30mg SR", "Capsule", 4.80, [("Razo-D", 16.50, "Dr. Reddy's"), ("Rablet-D", 15.80, "Lupin"), ("Happi-D", 15.20, "Zydus")])
        ]
    },
    {
        "salt": "Ondansetron", "generic": "Ondansetron", "cat": "Antiemetic (5-HT3 Antagonist)", "sch": "Schedule H",
        "variants": [
            ("4mg", "Tablet", 1.50, [("Emeset 4", 5.20, "Cipla"), ("Zofran 4", 12.00, "GSK"), ("Vomikind 4", 4.80, "Mankind"), ("Ondem 4", 5.00, "Alkem")]),
            ("8mg", "Tablet", 2.80, [("Emeset 8", 9.80, "Cipla"), ("Zofran 8", 22.00, "GSK"), ("Vomikind 8", 8.90, "Mankind"), ("Ondem 8", 9.20, "Alkem")]),
            ("2mg/ml", "Injection", 4.50, [("Emeset 2ml Inj", 15.50, "Cipla"), ("Zofran 2ml Inj", 35.00, "GSK"), ("Ondem Inj", 14.80, "Alkem")]),
            ("2mg/5ml", "Syrup", 14.00, [("Emeset Syrup 30ml", 38.00, "Cipla"), ("Vomikind Syrup", 35.00, "Mankind")])
        ]
    },
    {
        "salt": "Sucralfate + Oxetacaine", "generic": "Sucralfate + Oxetacaine", "cat": "Ulcer Protectant & Local Anesthetic", "sch": "Schedule H",
        "variants": [
            ("1000mg + 20mg/10ml", "Syrup", 42.00, [("Sucrafil-O Suspension 100ml", 148.00, "Fourrts"), ("Mucaine Gel", 138.00, "Pfizer"), ("Ulcagel-O", 125.00, "Torrent")])
        ]
    },
    {
        "salt": "Ursodeoxycholic Acid", "generic": "Ursodeoxycholic Acid", "cat": "Hepatoprotective / Gallstone Dissolution", "sch": "Schedule H",
        "variants": [
            ("150mg", "Tablet", 6.00, [("Udiliv 150", 18.50, "Abbott"), ("Ursocol 150", 17.80, "Sun Pharma"), ("Ursetor 150", 17.00, "Torrent")]),
            ("300mg", "Tablet", 11.50, [("Udiliv 300", 35.00, "Abbott"), ("Ursocol 300", 33.50, "Sun Pharma"), ("Ursetor 300", 32.00, "Torrent")])
        ]
    },

    # 6. Respiratory & Anti-allergic
    {
        "salt": "Levocetirizine Dihydrochloride", "generic": "Levocetirizine", "cat": "Antihistamine (Anti-allergic)", "sch": "Schedule H",
        "variants": [
            ("2.5mg/5ml", "Syrup", 18.00, [("Levocet Syrup 60ml", 48.00, "Hetero"), ("1-AL Syrup", 46.00, "FDC"), ("Cetcip-L Syrup", 45.00, "Cipla")]),
            ("5mg", "Tablet", 1.40, [("Levocet 5", 4.80, "Hetero"), ("1-AL 5", 4.50, "FDC"), ("Vozet 5", 4.20, "Dr. Reddy's"), ("Xyzal 5", 9.50, "GSK")]),
            ("10mg", "Tablet", 2.50, [("Levocet 10", 8.20, "Hetero"), ("1-AL 10", 7.80, "FDC")])
        ]
    },
    {
        "salt": "Montelukast + Levocetirizine", "generic": "Montelukast + Levocetirizine", "cat": "Anti-allergic & Leukotriene Receptor Antagonist", "sch": "Schedule H",
        "variants": [
            ("10mg + 5mg", "Tablet", 4.20, [("Montair-LC", 16.50, "Cipla"), ("Telekast-L", 15.80, "Lupin"), ("Montek-LC", 15.50, "Sun Pharma"), ("Romilast-L", 15.00, "Ranbaxy")]),
            ("4mg + 2.5mg", "Chewable Tablet", 3.00, [("Montair-LC Kid", 9.80, "Cipla"), ("Telekast-L Kid", 9.20, "Lupin"), ("Montek-LC Kid", 9.00, "Sun Pharma")]),
            ("4mg + 2.5mg/5ml", "Syrup", 32.00, [("Montair-LC Suspension", 85.00, "Cipla"), ("Montek-LC Syrup", 82.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Cetirizine Hydrochloride", "generic": "Cetirizine", "cat": "Antihistamine", "sch": "Schedule H",
        "variants": [
            ("10mg", "Tablet", 0.90, [("Cetzine 10", 2.80, "GSK"), ("Alerid 10", 2.60, "Cipla"), ("Zyrtec 10", 6.50, "Dr. Reddy's"), ("Okacet 10", 2.50, "Cipla")]),
            ("5mg/5ml", "Syrup", 16.00, [("Cetzine Syrup 60ml", 42.00, "GSK"), ("Alerid Syrup", 38.00, "Cipla")])
        ]
    },
    {
        "salt": "Fexofenadine Hydrochloride", "generic": "Fexofenadine", "cat": "Non-sedating Antihistamine", "sch": "Schedule H",
        "variants": [
            ("120mg", "Tablet", 4.80, [("Allegra 120", 17.50, "Sanofi"), ("Fexova 120", 14.00, "Ipca"), ("Histafree 120", 13.50, "Mankind")]),
            ("180mg", "Tablet", 6.50, [("Allegra 180", 23.00, "Sanofi"), ("Fexova 180", 18.50, "Ipca"), ("Histafree 180", 18.00, "Mankind")])
        ]
    },
    {
        "salt": "Salbutamol (Albuterol)", "generic": "Salbutamol", "cat": "Bronchodilator (Beta-2 Agonist)", "sch": "Schedule H",
        "variants": [
            ("2mg", "Tablet", 0.40, [("Asthalin 2", 1.20, "Cipla"), ("Ventorlin 2", 1.30, "GSK")]),
            ("4mg", "Tablet", 0.70, [("Asthalin 4", 1.80, "Cipla"), ("Ventorlin 4", 2.00, "GSK")]),
            ("100mcg/puff", "Inhaler", 45.00, [("Asthalin Inhaler 200 mdi", 145.00, "Cipla"), ("Ventorlin CFC-Free Inhaler", 165.00, "GSK")]),
            ("5mg/ml", "Respirator Solution", 15.00, [("Asthalin Respules 2.5ml", 42.00, "Cipla"), ("Ventorlin Respules", 48.00, "GSK")])
        ]
    },
    {
        "salt": "Budesonide", "generic": "Budesonide", "cat": "Inhaled Corticosteroid", "sch": "Schedule H",
        "variants": [
            ("100mcg", "Inhaler", 65.00, [("Budecort 100 Inhaler", 195.00, "Cipla"), ("Pulmicort 100", 240.00, "AstraZeneca")]),
            ("200mcg", "Inhaler", 95.00, [("Budecort 200 Inhaler", 285.00, "Cipla"), ("Pulmicort 200", 350.00, "AstraZeneca")]),
            ("0.5mg/2ml", "Respules", 8.50, [("Budecort Respules 0.5mg", 26.00, "Cipla"), ("Pulmicort Respules", 38.00, "AstraZeneca")])
        ]
    },
    {
        "salt": "Formoterol + Budesonide", "generic": "Formoterol + Budesonide", "cat": "Bronchodilator + Corticosteroid", "sch": "Schedule H",
        "variants": [
            ("6mcg + 200mcg", "Inhaler", 110.00, [("Foracort 200 Inhaler", 340.00, "Cipla"), ("Symbicort 200", 480.00, "AstraZeneca"), ("Maxiflo 200", 320.00, "Cipla")]),
            ("6mcg + 400mcg", "Inhaler", 145.00, [("Foracort 400 Inhaler", 450.00, "Cipla"), ("Symbicort 400", 620.00, "AstraZeneca")])
        ]
    },
    {
        "salt": "Acebrophylline", "generic": "Acebrophylline", "cat": "Mucolytic & Bronchodilator", "sch": "Schedule H",
        "variants": [
            ("100mg", "Capsule", 3.80, [("AB Phylline 100", 13.50, "Sun Pharma"), ("Macbery 100", 12.80, "Macleods"), ("Ventidox 100", 12.00, "Lupin")]),
            ("200mg SR", "Tablet", 6.20, [("AB Phylline SR 200", 21.00, "Sun Pharma"), ("Macbery SR 200", 19.50, "Macleods")])
        ]
    },

    # 7. Central Nervous System & Psychiatry
    {
        "salt": "Escitalopram Oxalate", "generic": "Escitalopram", "cat": "Antidepressant (SSRI)", "sch": "Schedule H",
        "variants": [
            ("5mg", "Tablet", 2.20, [("Nexito 5", 6.80, "Sun Pharma"), ("Cipralex 5", 18.00, "Lundbeck"), ("Stalopam 5", 6.50, "Lupin")]),
            ("10mg", "Tablet", 3.80, [("Nexito 10", 11.80, "Sun Pharma"), ("Cipralex 10", 32.00, "Lundbeck"), ("Stalopam 10", 11.20, "Lupin"), ("S-Citadep 10", 10.90, "Cipla")]),
            ("20mg", "Tablet", 6.50, [("Nexito 20", 20.50, "Sun Pharma"), ("Cipralex 20", 55.00, "Lundbeck"), ("Stalopam 20", 19.80, "Lupin")])
        ]
    },
    {
        "salt": "Clonazepam", "generic": "Clonazepam", "cat": "Anxiolytic / Anticonvulsant", "sch": "Schedule H1",
        "variants": [
            ("0.25mg", "Tablet", 1.20, [("Clonafit 0.25", 3.80, "Mankind"), ("Zapiz 0.25", 3.60, "Intas"), ("Klonopin 0.25", 9.50, "Roche")]),
            ("0.5mg", "Tablet", 1.80, [("Clonafit 0.5", 5.80, "Mankind"), ("Zapiz 0.5", 5.50, "Intas"), ("Lonazep 0.5", 5.40, "Sun Pharma")]),
            ("1mg", "Tablet", 3.00, [("Clonafit 1", 9.20, "Mankind"), ("Zapiz 1", 8.80, "Intas"), ("Lonazep 1", 8.50, "Sun Pharma")]),
            ("2mg", "Tablet", 4.80, [("Clonafit 2", 14.50, "Mankind"), ("Zapiz 2", 14.00, "Intas"), ("Lonazep 2", 13.80, "Sun Pharma")])
        ]
    },
    {
        "salt": "Alprazolam", "generic": "Alprazolam", "cat": "Anxiolytic (Benzodiazepine)", "sch": "Schedule H1",
        "variants": [
            ("0.25mg", "Tablet", 0.90, [("Alprax 0.25", 2.80, "Torrent"), ("Restyl 0.25", 2.60, "Cipla"), ("Xanax 0.25", 8.00, "Pfizer")]),
            ("0.5mg", "Tablet", 1.50, [("Alprax 0.5", 4.50, "Torrent"), ("Restyl 0.5", 4.20, "Cipla"), ("Xanax 0.5", 13.50, "Pfizer"), ("Trika 0.5", 4.00, "Unichem")])
        ]
    },
    {
        "salt": "Sertraline Hydrochloride", "generic": "Sertraline", "cat": "Antidepressant (SSRI)", "sch": "Schedule H",
        "variants": [
            ("25mg", "Tablet", 2.80, [("Daxid 25", 8.50, "Pfizer"), ("Sertima 25", 8.00, "Intas"), ("Zoloft 25", 22.00, "Pfizer")]),
            ("50mg", "Tablet", 4.80, [("Daxid 50", 15.00, "Pfizer"), ("Sertima 50", 14.50, "Intas"), ("Zoloft 50", 38.00, "Pfizer"), ("Serlift 50", 14.00, "Sun Pharma")]),
            ("100mg", "Tablet", 8.50, [("Daxid 100", 26.50, "Pfizer"), ("Sertima 100", 25.00, "Intas"), ("Zoloft 100", 68.00, "Pfizer")])
        ]
    },
    {
        "salt": "Pregabalin", "generic": "Pregabalin", "cat": "Neuropathic Pain & Anticonvulsant", "sch": "Schedule H",
        "variants": [
            ("75mg", "Capsule", 4.50, [("Lyrica 75", 38.00, "Pfizer"), ("Pregeb 75", 14.50, "Torrent"), ("Pregalin 75", 14.00, "Torrent"), ("Maxgalin 75", 13.80, "Sun Pharma")]),
            ("150mg", "Capsule", 7.80, [("Lyrica 150", 65.00, "Pfizer"), ("Pregeb 150", 24.00, "Torrent"), ("Pregalin 150", 23.50, "Torrent"), ("Maxgalin 150", 23.00, "Sun Pharma")]),
            ("300mg", "Capsule", 14.00, [("Lyrica 300", 110.00, "Pfizer"), ("Pregeb 300", 42.00, "Torrent")])
        ]
    },
    {
        "salt": "Levetiracetam", "generic": "Levetiracetam", "cat": "Antiepileptic", "sch": "Schedule H",
        "variants": [
            ("250mg", "Tablet", 4.00, [("Keppra 250", 18.00, "UCB"), ("Levipil 250", 12.00, "Sun Pharma"), ("Torleva 250", 11.50, "Torrent")]),
            ("500mg", "Tablet", 7.20, [("Keppra 500", 32.00, "UCB"), ("Levipil 500", 21.50, "Sun Pharma"), ("Torleva 500", 20.80, "Torrent"), ("Epilive 500", 20.50, "Lupin")]),
            ("1000mg", "Tablet", 13.50, [("Keppra 1000", 58.00, "UCB"), ("Levipil 1000", 39.00, "Sun Pharma"), ("Torleva 1000", 38.00, "Torrent")])
        ]
    },
    {
        "salt": "Sodium Valproate + Valproic Acid", "generic": "Sodium Valproate CR", "cat": "Antiepileptic & Mood Stabilizer", "sch": "Schedule H",
        "variants": [
            ("200mg", "Tablet", 2.80, [("Epilim Chrono 200", 8.50, "Sanofi"), ("Valparin Chrono 200", 7.80, "Torrent"), ("Encorate Chrono 200", 7.50, "Sun Pharma")]),
            ("300mg", "Tablet", 3.80, [("Epilim Chrono 300", 11.80, "Sanofi"), ("Valparin Chrono 300", 10.50, "Torrent"), ("Encorate Chrono 300", 10.20, "Sun Pharma")]),
            ("500mg", "Tablet", 5.80, [("Epilim Chrono 500", 18.00, "Sanofi"), ("Valparin Chrono 500", 16.50, "Torrent"), ("Encorate Chrono 500", 16.00, "Sun Pharma")])
        ]
    },

    # 8. Vitamins, Minerals & Supplements
    {
        "salt": "Cholecalciferol (Vitamin D3)", "generic": "Vitamin D3", "cat": "Vitamin Supplement", "sch": "OTC",
        "variants": [
            ("60000 IU", "Capsule", 12.00, [("Calcirol 60K", 38.00, "Cadila"), ("D-Rise 60K", 36.00, "USV"), ("Uprise-D3 60K", 35.00, "Alkem"), ("Tayo 60K", 34.00, "Torrent")]),
            ("60000 IU/gm", "Sachet", 9.00, [("Calcirol Sachet", 32.00, "Cadila"), ("D-Rise Sachet", 30.00, "USV")]),
            ("800 IU/ml", "Drops", 28.00, [("Calcirol Drops 15ml", 85.00, "Cadila"), ("D-Rise Drops", 80.00, "USV")])
        ]
    },
    {
        "salt": "Methylcobalamin (Vitamin B12)", "generic": "Methylcobalamin", "cat": "Neurological Vitamin Supplement", "sch": "OTC",
        "variants": [
            ("500mcg", "Tablet", 2.20, [("Methycobal 500", 11.50, "Eisai"), ("Nurokind 500", 5.80, "Mankind"), ("Meconerv 500", 5.50, "Micro Labs")]),
            ("1500mcg", "Tablet", 4.50, [("Methycobal 1500", 22.00, "Eisai"), ("Nurokind-OD 1500", 11.50, "Mankind"), ("Meconerv-Forte", 12.00, "Micro Labs"), ("Nuroday 1500", 10.80, "Wockhardt")]),
            ("1500mcg/2ml", "Injection", 18.00, [("Nurokind Injection 2ml", 65.00, "Mankind"), ("Methycobal Injection", 120.00, "Eisai")])
        ]
    },
    {
        "salt": "Calcium Carbonate + Vitamin D3", "generic": "Calcium + Vitamin D3", "cat": "Mineral & Bone Health", "sch": "OTC",
        "variants": [
            ("500mg + 250 IU", "Tablet", 1.80, [("Shelcal 500", 6.80, "Torrent"), ("Gemcal", 6.50, "Alkem"), ("Cipcal 500", 6.20, "Cipla"), ("Ostocalcium Plus", 5.80, "GSK")])
        ]
    },
    {
        "salt": "Ferrous Ascorbate + Folic Acid", "generic": "Iron + Folic Acid", "cat": "Hematinic (Iron Supplement)", "sch": "OTC",
        "variants": [
            ("100mg + 1.5mg", "Tablet", 2.50, [("Orofer-XT", 9.80, "Emcure"), ("Feronia-XT", 9.20, "Zydus"), ("Fefol-Z", 8.80, "GSK"), ("Livogen-Z", 8.50, "Merck")]),
            ("30mg + 550mcg/5ml", "Syrup", 35.00, [("Orofer-XT Syrup 150ml", 135.00, "Emcure"), ("Feronia-XT Suspension", 128.00, "Zydus")])
        ]
    },

    # 9. Urological, Thyroid & Sexual Health
    {
        "salt": "Levothyroxine Sodium", "generic": "Levothyroxine", "cat": "Thyroid Hormone", "sch": "Schedule H",
        "variants": [
            ("25mcg", "Tablet", 1.10, [("Thyronorm 25", 3.20, "Abbott"), ("Eltroxin 25", 3.10, "GSK"), ("Thyrox 25", 2.90, "MacLeods")]),
            ("50mcg", "Tablet", 1.30, [("Thyronorm 50", 3.80, "Abbott"), ("Eltroxin 50", 3.70, "GSK"), ("Thyrox 50", 3.40, "MacLeods")]),
            ("75mcg", "Tablet", 1.45, [("Thyronorm 75", 4.10, "Abbott"), ("Eltroxin 75", 4.00, "GSK"), ("Thyrox 75", 3.70, "MacLeods")]),
            ("100mcg", "Tablet", 1.60, [("Thyronorm 100", 4.60, "Abbott"), ("Eltroxin 100", 4.50, "GSK"), ("Thyrox 100", 4.20, "MacLeods")]),
            ("125mcg", "Tablet", 1.80, [("Thyronorm 125", 5.00, "Abbott"), ("Eltroxin 125", 4.90, "GSK"), ("Thyrox 125", 4.50, "MacLeods")])
        ]
    },
    {
        "salt": "Tamsulosin Hydrochloride", "generic": "Tamsulosin", "cat": "Alpha-1 Blocker (BPH)", "sch": "Schedule H",
        "variants": [
            ("0.2mg", "Capsule", 3.20, [("Flomaxtra 0.2", 12.00, "Astellas"), ("Urimax 0.2", 9.50, "Ranbaxy"), ("Tamflow 0.2", 9.00, "Sun Pharma")]),
            ("0.4mg", "Capsule", 5.50, [("Flomaxtra 0.4", 22.00, "Astellas"), ("Urimax 0.4", 17.50, "Ranbaxy"), ("Tamflow 0.4", 16.80, "Sun Pharma"), ("Urimax-D", 19.00, "Ranbaxy")])
        ]
    },
    {
        "salt": "Tamsulosin + Dutasteride", "generic": "Tamsulosin + Dutasteride", "cat": "Urological Combination (BPH)", "sch": "Schedule H",
        "variants": [
            ("0.4mg + 0.5mg", "Tablet", 8.50, [("Urimax-D", 26.50, "Ranbaxy"), ("Tamflo-D", 25.00, "Sun Pharma"), ("Duodart", 45.00, "GSK")])
        ]
    },
    {
        "salt": "Finasteride", "generic": "Finasteride", "cat": "5-Alpha Reductase Inhibitor", "sch": "Schedule H",
        "variants": [
            ("1mg", "Tablet", 3.50, [("Propecia 1mg", 35.00, "Organon"), ("Finax 1mg", 11.50, "Dr. Reddy's"), ("Finpecia 1mg", 11.00, "Cipla")]),
            ("5mg", "Tablet", 6.80, [("Proscar 5mg", 48.00, "Organon"), ("Finast 5mg", 21.00, "Dr. Reddy's"), ("Fincar 5mg", 20.00, "Cipla")])
        ]
    },
    {
        "salt": "Sildenafil Citrate", "generic": "Sildenafil", "cat": "PDE5 Inhibitor (ED / PAH)", "sch": "Schedule H",
        "variants": [
            ("25mg", "Tablet", 4.50, [("Viagra 25mg", 180.00, "Pfizer"), ("Manforce 25mg", 16.00, "Mankind"), ("Caverta 25mg", 18.00, "Sun Pharma")]),
            ("50mg", "Tablet", 7.00, [("Viagra 50mg", 320.00, "Pfizer"), ("Manforce 50mg", 26.00, "Mankind"), ("Caverta 50mg", 28.00, "Sun Pharma")]),
            ("100mg", "Tablet", 12.00, [("Viagra 100mg", 550.00, "Pfizer"), ("Manforce 100mg", 45.00, "Mankind"), ("Caverta 100mg", 48.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Tadalafil", "generic": "Tadalafil", "cat": "PDE5 Inhibitor", "sch": "Schedule H",
        "variants": [
            ("5mg", "Tablet", 5.00, [("Cialis 5mg", 140.00, "Eli Lilly"), ("Megalis 5mg", 22.00, "Macleods"), ("Tazzle 5mg", 20.00, "Sun Pharma")]),
            ("10mg", "Tablet", 9.00, [("Cialis 10mg", 250.00, "Eli Lilly"), ("Megalis 10mg", 38.00, "Macleods")]),
            ("20mg", "Tablet", 15.00, [("Cialis 20mg", 450.00, "Eli Lilly"), ("Megalis 20mg", 65.00, "Macleods"), ("Tazzle 20mg", 60.00, "Sun Pharma")])
        ]
    },
    {
        "salt": "Letrozole", "generic": "Letrozole", "cat": "Aromatase Inhibitor (Breast Cancer/Ovulation)", "sch": "Schedule H",
        "variants": [
            ("2.5mg", "Tablet", 8.50, [("Femara 2.5", 185.00, "Novartis"), ("Letroz 2.5", 38.00, "Sun Pharma"), ("Fempro 2.5", 36.00, "Cipla")])
        ]
    }
]

# Systematic expansion molecules (ensures 550+ distinct items)
EXTRA_MEDICINES = [
    ("Clarithromycin", "Clarithromycin", "Macrolide Antibiotic", "Schedule H", [("250mg", "Tablet", 12.0, [("Claribid 250", 38.0, "Kremers"), ("Clarimax 250", 36.0, "Macleods")]), ("500mg", "Tablet", 22.0, [("Claribid 500", 68.0, "Kremers"), ("Clarimax 500", 64.0, "Macleods")])]),
    ("Ofloxacin", "Ofloxacin", "Fluoroquinolone Antibiotic", "Schedule H1", [("200mg", "Tablet", 2.8, [("Oflox 200", 8.5, "Cipla"), ("Zenflox 200", 8.0, "Mankind")]), ("400mg", "Tablet", 5.2, [("Oflox 400", 16.0, "Cipla"), ("Zenflox 400", 15.2, "Mankind")])]),
    ("Ofloxacin + Ornidazole", "Ofloxacin + Ornidazole", "Antibacterial & Antiprotozoal", "Schedule H1", [("200mg + 500mg", "Tablet", 4.5, [("O2 Tablet", 14.5, "Medley"), ("Zenflox-OZ", 13.8, "Mankind"), ("Oflox-OZ", 14.0, "Cipla")])]),
    ("Ceftriaxone Sodium", "Ceftriaxone", "Cephalosporin Antibiotic", "Schedule H1", [("250mg", "Injection", 18.0, [("Monocef 250", 55.0, "Aristo"), ("Oframax 250", 52.0, "Sun Pharma")]), ("500mg", "Injection", 28.0, [("Monocef 500", 85.0, "Aristo"), ("Oframax 500", 80.0, "Sun Pharma")]), ("1g", "Injection", 42.0, [("Monocef 1g", 128.0, "Aristo"), ("Oframax 1g", 122.0, "Sun Pharma"), ("Rocephin 1g", 240.0, "Roche")]), ("2g", "Injection", 78.0, [("Monocef 2g", 235.0, "Aristo")])]),
    ("Cefuroxime Axetil", "Cefuroxime", "Cephalosporin Antibiotic", "Schedule H1", [("250mg", "Tablet", 11.0, [("Ceftum 250", 35.0, "GSK"), ("Cetil 250", 33.0, "Lupin"), ("Pulmocef 250", 32.0, "Micro Labs")]), ("500mg", "Tablet", 19.5, [("Ceftum 500", 62.0, "GSK"), ("Cetil 500", 58.0, "Lupin"), ("Pulmocef 500", 56.0, "Micro Labs")])]),
    ("Nitrofurantoin", "Nitrofurantoin", "Urinary Anti-infective", "Schedule H", [("100mg SR", "Capsule", 4.5, [("Martifur MR 100", 14.5, "Sun Pharma"), ("Niftran TM 100", 14.0, "Sun Pharma"), ("Uribid 100", 13.5, "Intas")])]),
    ("Terbinafine", "Terbinafine", "Antifungal", "Schedule H", [("250mg", "Tablet", 8.5, [("Sebifin 250", 26.0, "Sun Pharma"), ("Tyza 250", 24.5, "Abbott"), ("Lamisil 250", 65.0, "Novartis")]), ("500mg", "Tablet", 15.0, [("Sebifin 500", 46.0, "Sun Pharma"), ("Tyza 500", 44.0, "Abbott")]), ("1% w/w", "Cream", 28.0, [("Sebifin Cream 15g", 88.0, "Sun Pharma"), ("Lamisil Cream", 140.0, "Novartis")])]),
    ("Losartan Potassium", "Losartan", "Antihypertensive (ARB)", "Schedule H", [("25mg", "Tablet", 1.5, [("Losacar 25", 4.8, "Zydus"), ("Repace 25", 4.5, "Sun Pharma")]), ("50mg", "Tablet", 2.6, [("Losacar 50", 8.2, "Zydus"), ("Repace 50", 7.8, "Sun Pharma"), ("Cozaar 50", 22.0, "MSD")]), ("100mg", "Tablet", 4.8, [("Losacar 100", 15.0, "Zydus"), ("Repace 100", 14.2, "Sun Pharma")])]),
    ("Losartan + Hydrochlorothiazide", "Losartan + Hydrochlorothiazide", "Antihypertensive Combination", "Schedule H", [("50mg + 12.5mg", "Tablet", 3.2, [("Losacar-H", 10.2, "Zydus"), ("Repace-H", 9.8, "Sun Pharma"), ("Hyzaar", 28.0, "MSD")])]),
    ("Olmesartan Medoxomil", "Olmesartan", "Antihypertensive (ARB)", "Schedule H", [("20mg", "Tablet", 3.8, [("Olmecip 20", 12.0, "Cipla"), ("Olmetime 20", 11.5, "Mankind"), ("Benicar 20", 32.0, "Daiichi Sankyo")]), ("40mg", "Tablet", 6.8, [("Olmecip 40", 21.5, "Cipla"), ("Olmetime 40", 20.5, "Mankind"), ("Benicar 40", 56.0, "Daiichi Sankyo")])]),
    ("Olmesartan + Amlodipine", "Olmesartan + Amlodipine", "Antihypertensive Combination", "Schedule H", [("20mg + 5mg", "Tablet", 4.8, [("Olmecip-AM 20", 15.5, "Cipla"), ("Olmetime-AM 20", 14.8, "Mankind")]), ("40mg + 5mg", "Tablet", 7.8, [("Olmecip-AM 40", 24.5, "Cipla"), ("Olmetime-AM 40", 23.0, "Mankind")])]),
    ("Nebivolol", "Nebivolol", "Beta Blocker (Vasodilating)", "Schedule H", [("2.5mg", "Tablet", 2.6, [("Nebicard 2.5", 8.5, "Torrent"), ("Nebilong 2.5", 8.0, "Micro Labs")]), ("5mg", "Tablet", 4.5, [("Nebicard 5", 14.2, "Torrent"), ("Nebilong 5", 13.5, "Micro Labs"), ("Bystolic 5", 42.0, "Allergan")])]),
    ("Atenolol", "Atenolol", "Beta Blocker", "Schedule H", [("25mg", "Tablet", 0.9, [("Aten 25", 2.8, "Zydus"), ("Tenormin 25", 4.5, "Abbott")]), ("50mg", "Tablet", 1.4, [("Aten 50", 4.5, "Zydus"), ("Tenormin 50", 7.2, "Abbott")]), ("100mg", "Tablet", 2.4, [("Aten 100", 7.8, "Zydus"), ("Tenormin 100", 12.5, "Abbott")])]),
    ("Enalapril Maleate", "Enalapril", "ACE Inhibitor", "Schedule H", [("2.5mg", "Tablet", 0.8, [("Envas 2.5", 2.5, "Cadila"), ("Vasotec 2.5", 6.0, "MSD")]), ("5mg", "Tablet", 1.4, [("Envas 5", 4.5, "Cadila"), ("Vasotec 5", 10.5, "MSD")]), ("10mg", "Tablet", 2.5, [("Envas 10", 7.8, "Cadila"), ("Vasotec 10", 18.0, "MSD")])]),
    ("Ticagrelor", "Ticagrelor", "Antiplatelet", "Schedule H", [("60mg", "Tablet", 12.0, [("Brilinta 60", 45.0, "AstraZeneca"), ("Axcer 60", 28.0, "Sun Pharma")]), ("90mg", "Tablet", 16.0, [("Brilinta 90", 60.0, "AstraZeneca"), ("Axcer 90", 38.0, "Sun Pharma"), ("Ticaspan 90", 35.0, "Lupin")])]),
    ("Apixaban", "Apixaban", "Novel Oral Anticoagulant (NOAC)", "Schedule H", [("2.5mg", "Tablet", 18.0, [("Eliquis 2.5", 72.0, "Pfizer / BMS"), ("Apigat 2.5", 38.0, "Natco"), ("Apixabid 2.5", 36.0, "Sun Pharma")]), ("5mg", "Tablet", 22.0, [("Eliquis 5", 85.0, "Pfizer / BMS"), ("Apigat 5", 44.0, "Natco"), ("Apixabid 5", 42.0, "Sun Pharma")])]),
    ("Rivaroxaban", "Rivaroxaban", "Novel Oral Anticoagulant (NOAC)", "Schedule H", [("10mg", "Tablet", 24.0, [("Xarelto 10", 98.0, "Bayer"), ("Rivaros 10", 48.0, "Torrent"), ("Ixarola 10", 45.0, "Sun Pharma")]), ("15mg", "Tablet", 28.0, [("Xarelto 15", 112.0, "Bayer"), ("Rivaros 15", 54.0, "Torrent")]), ("20mg", "Tablet", 32.0, [("Xarelto 20", 128.0, "Bayer"), ("Rivaros 20", 62.0, "Torrent")])]),
    ("Gliclazide", "Gliclazide", "Antidiabetic (Sulfonylurea)", "Schedule H", [("40mg", "Tablet", 1.8, [("Diamicron 40", 5.8, "Serdia"), ("Glizid 40", 5.2, "Sun Pharma")]), ("80mg", "Tablet", 3.2, [("Diamicron 80", 10.5, "Serdia"), ("Glizid 80", 9.5, "Sun Pharma")]), ("60mg MR", "Tablet", 4.5, [("Diamicron 60 MR", 14.5, "Serdia"), ("Glizid 60 MR", 13.0, "Sun Pharma")])]),
    ("Gliclazide + Metformin", "Gliclazide + Metformin SR", "Antidiabetic Combination", "Schedule H", [("80mg + 500mg SR", "Tablet", 3.8, [("Glizid-M", 12.0, "Sun Pharma"), ("Diamicron-XR Mex", 14.0, "Serdia")]), ("60mg MR + 500mg SR", "Tablet", 4.8, [("Glizid-M OD 60", 15.0, "Sun Pharma")])]),
    ("Vildagliptin", "Vildagliptin", "Antidiabetic (DPP-4 Inhibitor)", "Schedule H", [("50mg", "Tablet", 5.5, [("Galvus 50", 24.0, "Novartis"), ("Zomelis 50", 14.0, "Abbott"), ("Vildamac 50", 13.0, "Macleods"), ("Jalra 50", 13.5, "USV")])]),
    ("Vildagliptin + Metformin", "Vildagliptin + Metformin SR", "Antidiabetic Combination", "Schedule H", [("50mg + 500mg", "Tablet", 6.8, [("Galvus Met 50/500", 28.0, "Novartis"), ("Zomelis-Met 50/500", 16.5, "Abbott"), ("Jalra-M 50/500", 16.0, "USV")]), ("50mg + 850mg", "Tablet", 7.5, [("Galvus Met 50/850", 31.0, "Novartis"), ("Zomelis-Met 50/850", 18.0, "Abbott")]), ("50mg + 1000mg", "Tablet", 8.2, [("Galvus Met 50/1000", 34.0, "Novartis"), ("Zomelis-Met 50/1000", 19.5, "Abbott")])]),
    ("Linagliptin", "Linagliptin", "Antidiabetic (DPP-4 Inhibitor)", "Schedule H", [("5mg", "Tablet", 12.0, [("Trajenta 5", 58.0, "Boehringer"), ("Linaone 5", 28.0, "Cipla"), ("Linamac 5", 26.0, "Macleods")])]),
    ("Pioglitazone", "Pioglitazone", "Antidiabetic (Thiazolidinedione)", "Schedule H", [("15mg", "Tablet", 1.8, [("Pioz 15", 5.8, "USV"), ("Piosys 15", 5.5, "Systopic"), ("Actos 15", 16.0, "Takeda")]), ("30mg", "Tablet", 3.2, [("Pioz 30", 9.8, "USV"), ("Piosys 30", 9.2, "Systopic"), ("Actos 30", 28.0, "Takeda")])]),
    ("Esomeprazole", "Esomeprazole", "Proton Pump Inhibitor (PPI)", "Schedule H", [("20mg", "Tablet", 2.5, [("Nexpro 20", 8.5, "Torrent"), ("Nexium 20", 24.0, "AstraZeneca"), ("Esomac 20", 7.8, "Cipla")]), ("40mg", "Tablet", 4.2, [("Nexpro 40", 14.5, "Torrent"), ("Nexium 40", 42.0, "AstraZeneca"), ("Esomac 40", 13.8, "Cipla")]), ("40mg", "Injection", 22.0, [("Nexpro IV", 85.0, "Torrent"), ("Nexium IV", 160.0, "AstraZeneca")])]),
    ("Esomeprazole + Domperidone", "Esomeprazole + Domperidone SR", "Antacid & Antiemetic", "Schedule H", [("40mg + 30mg SR", "Capsule", 5.2, [("Nexpro-D 40", 17.5, "Torrent"), ("Esomac-D 40", 16.8, "Cipla"), ("Sompraz-D 40", 16.5, "Sun Pharma")])]),
    ("Domperidone", "Domperidone", "Prokinetic / Antiemetic", "Schedule H", [("10mg", "Tablet", 1.2, [("Domstal 10", 3.8, "Torrent"), ("Motilium 10", 8.0, "Janssen"), ("Vomitop 10", 3.5, "Mankind")]), ("1mg/ml", "Suspension", 16.0, [("Domstal Suspension", 42.0, "Torrent"), ("Motilium Suspension", 65.0, "Janssen")])]),
    ("Itopride Hydrochloride", "Itopride", "Prokinetic", "Schedule H", [("50mg", "Tablet", 3.2, [("Ganaton 50", 11.5, "Abbott"), ("Itza 50", 10.8, "Sun Pharma"), ("Gitop 50", 10.2, "Lupin")])]),
    ("Loperamide Hydrochloride", "Loperamide", "Antidiarrheal", "Schedule H", [("2mg", "Capsule", 0.8, [("Imodium 2mg", 4.2, "Janssen"), ("Eldoper 2mg", 2.5, "Micro Labs"), ("Lopamide 2mg", 2.4, "Torrent")])]),
    ("Mesalamine (Mesalazine)", "Mesalamine", "Anti-inflammatory (IBD)", "Schedule H", [("400mg", "Tablet", 5.5, [("Mesacol 400", 18.0, "Sun Pharma"), ("Asacol 400", 24.0, "Allergan")]), ("800mg", "Tablet", 10.5, [("Mesacol 800", 34.0, "Sun Pharma"), ("Asacol 800", 45.0, "Allergan")]), ("1.2g", "Tablet", 16.0, [("Mesacol OD 1.2g", 52.0, "Sun Pharma"), ("Pentasa 1g", 65.0, "Ferring")])]),
    ("Lactulose", "Lactulose", "Osmotic Laxative / Hepatic Encephalopathy", "OTC", [("10g/15ml", "Syrup", 45.0, [("Duphalac Syrup 200ml", 195.0, "Abbott"), ("Looz Syrup 200ml", 185.0, "Intas"), ("Cremaffin Plus", 175.0, "Abbott")])]),
    ("Bilastine", "Bilastine", "Antihistamine (2nd Gen)", "Schedule H", [("20mg", "Tablet", 5.5, [("Bilaxten 20", 18.5, "Menarini"), ("Bilashine 20", 16.0, "Sun Pharma"), ("Bilasure 20", 15.5, "Torrent")])]),
    ("Dextromethorphan + Chlorpheniramine + Phenylephrine", "Cough Syrup (Triple Combo)", "Antitussive / Decongestant", "Schedule H", [("10mg + 2mg + 5mg/5ml", "Syrup", 26.0, [("Ascoril-D Plus 100ml", 85.0, "Glenmark"), ("Benadryl DR 100ml", 92.0, "J&J"), ("T-Koff Cough Syrup", 78.0, "Cipla")])]),
    ("Ambroxol + Levosalbutamol + Guaiphenesin", "Expectorant Cough Formula", "Mucolytic Expectorant", "Schedule H", [("30mg + 1mg + 50mg/5ml", "Syrup", 28.0, [("Ascoril-LS Syrup 100ml", 98.0, "Glenmark"), ("Bro-Zedex LS 100ml", 92.0, "Wockhardt"), ("Asthalin-AX Syrup", 88.0, "Cipla")])]),
    ("Ipratropium Bromide", "Ipratropium", "Anticholinergic Bronchodilator", "Schedule H", [("20mcg/puff", "Inhaler", 55.0, [("Ipravent Inhaler", 165.0, "Cipla"), ("Atrovent Inhaler", 220.0, "Boehringer")]), ("500mcg/2ml", "Respules", 6.5, [("Ipravent Respules", 21.0, "Cipla"), ("Atrovent Respules", 32.0, "Boehringer")])]),
    ("Tiotropium Bromide", "Tiotropium", "Long-Acting Anticholinergic (COPD)", "Schedule H", [("9mcg/puff", "Inhaler", 120.0, [("Tiova Inhaler", 380.0, "Cipla"), ("Spiriva Respimat", 750.0, "Boehringer")]), ("18mcg", "Rotacaps", 5.5, [("Tiova Rotacaps", 17.5, "Cipla"), ("Spiriva Handihaler Caps", 35.0, "Boehringer")])]),
    ("Fluoxetine Hydrochloride", "Fluoxetine", "Antidepressant (SSRI)", "Schedule H", [("20mg", "Capsule", 2.2, [("Prozac 20", 18.0, "Eli Lilly"), ("Fludac 20", 6.8, "Cadila"), ("Prodep 20", 6.5, "Sun Pharma")]), ("40mg", "Capsule", 4.0, [("Prozac 40", 32.0, "Eli Lilly"), ("Fludac 40", 12.0, "Cadila")])]),
    ("Paroxetine", "Paroxetine", "Antidepressant (SSRI)", "Schedule H", [("12.5mg CR", "Tablet", 4.2, [("Paxil CR 12.5", 28.0, "GSK"), ("Pari CR 12.5", 13.5, "Ipca"), ("Xet CR 12.5", 13.0, "Zydus")]), ("25mg CR", "Tablet", 7.5, [("Paxil CR 25", 48.0, "GSK"), ("Pari CR 25", 23.5, "Ipca"), ("Xet CR 25", 22.8, "Zydus")])]),
    ("Duloxetine", "Duloxetine", "Antidepressant (SNRI)", "Schedule H", [("20mg", "Capsule", 3.8, [("Cymbalta 20", 35.0, "Eli Lilly"), ("Duzela 20", 12.5, "Sun Pharma"), ("Dulane 20", 12.0, "Sun Pharma")]), ("30mg", "Capsule", 5.5, [("Cymbalta 30", 48.0, "Eli Lilly"), ("Duzela 30", 18.0, "Sun Pharma")]), ("60mg", "Capsule", 9.8, [("Cymbalta 60", 85.0, "Eli Lilly"), ("Duzela 60", 32.0, "Sun Pharma")])]),
    ("Venlafaxine", "Venlafaxine ER", "Antidepressant (SNRI)", "Schedule H", [("37.5mg", "Capsule", 3.5, [("Effexor XR 37.5", 32.0, "Pfizer"), ("Venlor XR 37.5", 11.5, "Cipla")]), ("75mg", "Capsule", 6.2, [("Effexor XR 75", 58.0, "Pfizer"), ("Venlor XR 75", 19.8, "Cipla")]), ("150mg", "Capsule", 11.5, [("Effexor XR 150", 105.0, "Pfizer"), ("Venlor XR 150", 36.0, "Cipla")])]),
    ("Amitriptyline Hydrochloride", "Amitriptyline", "Tricyclic Antidepressant", "Schedule H", [("10mg", "Tablet", 0.9, [("Tryptomer 10", 2.8, "Wockhardt"), ("Elavil 10", 6.5, "AstraZeneca")]), ("25mg", "Tablet", 1.5, [("Tryptomer 25", 4.8, "Wockhardt"), ("Elavil 25", 11.0, "AstraZeneca")])]),
    ("Diazepam", "Diazepam", "Benzodiazepine (Sedative)", "Schedule H1", [("2mg", "Tablet", 0.7, [("Valium 2", 3.5, "Roche"), ("Calmpose 2", 2.2, "Ranbaxy")]), ("5mg", "Tablet", 1.1, [("Valium 5", 5.5, "Roche"), ("Calmpose 5", 3.6, "Ranbaxy")]), ("10mg", "Tablet", 1.8, [("Valium 10", 9.0, "Roche"), ("Calmpose 10", 5.8, "Ranbaxy")]), ("5mg/ml", "Injection", 4.5, [("Calmpose 2ml Inj", 14.0, "Ranbaxy"), ("Valium Inj", 28.0, "Roche")])]),
    ("Lorazepam", "Lorazepam", "Benzodiazepine (Anxiolytic)", "Schedule H1", [("1mg", "Tablet", 1.2, [("Ativan 1mg", 4.2, "Pfizer"), ("Lopez 1mg", 3.8, "Intas"), ("Trapex 1mg", 3.6, "Sun Pharma")]), ("2mg", "Tablet", 2.0, [("Ativan 2mg", 6.8, "Pfizer"), ("Lopez 2mg", 6.2, "Intas"), ("Trapex 2mg", 6.0, "Sun Pharma")]), ("2mg/ml", "Injection", 6.5, [("Ativan 2ml Inj", 24.0, "Pfizer"), ("Lopez Inj", 20.0, "Intas")])]),
    ("Zolpidem Tartrate", "Zolpidem", "Non-Benzodiazepine Hypnotic", "Schedule H1", [("5mg", "Tablet", 2.5, [("Ambien 5mg", 18.0, "Sanofi"), ("Nitrest 5mg", 8.0, "Sun Pharma"), ("Zolfresh 5mg", 7.8, "Abbott")]), ("10mg", "Tablet", 4.2, [("Ambien 10mg", 32.0, "Sanofi"), ("Nitrest 10mg", 13.5, "Sun Pharma"), ("Zolfresh 10mg", 13.0, "Abbott")])]),
    ("Gabapentin", "Gabapentin", "Anticonvulsant & Neuropathic Pain", "Schedule H", [("100mg", "Tablet", 2.2, [("Neurontin 100", 14.0, "Pfizer"), ("Gabapin 100", 7.2, "Intas")]), ("300mg", "Tablet", 4.8, [("Neurontin 300", 32.0, "Pfizer"), ("Gabapin 300", 15.5, "Intas"), ("Gabantip 300", 15.0, "Sun Pharma")]), ("600mg", "Tablet", 8.5, [("Neurontin 600", 58.0, "Pfizer"), ("Gabapin 600", 27.5, "Intas")])]),
    ("Carbamazepine", "Carbamazepine", "Anticonvulsant / Mood Stabilizer", "Schedule H", [("100mg", "Tablet", 1.1, [("Tegretol 100", 3.5, "Novartis"), ("Mazetol 100", 3.2, "Abbott"), ("Zen 100", 3.0, "Intas")]), ("200mg", "Tablet", 1.8, [("Tegretol 200", 5.8, "Novartis"), ("Mazetol 200", 5.4, "Abbott"), ("Zen 200", 5.0, "Intas")]), ("400mg CR", "Tablet", 3.5, [("Tegretol CR 400", 11.5, "Novartis"), ("Mazetol SR 400", 10.8, "Abbott")])]),
    ("Phenytoin Sodium", "Phenytoin", "Anticonvulsant", "Schedule H", [("50mg", "Tablet", 0.9, [("Dilantin 50", 3.5, "Pfizer"), ("Eptoin 50", 2.8, "Abbott")]), ("100mg", "Tablet", 1.5, [("Dilantin 100", 5.8, "Pfizer"), ("Eptoin 100", 4.5, "Abbott"), ("Epsolin 100", 4.2, "Cadila")]), ("50mg/ml", "Injection", 8.0, [("Eptoin 2ml Inj", 26.0, "Abbott"), ("Dilantin Inj", 48.0, "Pfizer")])]),
    ("Olanzapine", "Olanzapine", "Atypical Antipsychotic", "Schedule H", [("2.5mg", "Tablet", 1.5, [("Zyprexa 2.5", 14.0, "Eli Lilly"), ("Oleanz 2.5", 4.8, "Sun Pharma"), ("Oltal 2.5", 4.5, "Torrent")]), ("5mg", "Tablet", 2.4, [("Zyprexa 5", 25.0, "Eli Lilly"), ("Oleanz 5", 7.8, "Sun Pharma"), ("Oltal 5", 7.4, "Torrent")]), ("10mg", "Tablet", 4.2, [("Zyprexa 10", 46.0, "Eli Lilly"), ("Oleanz 10", 13.5, "Sun Pharma"), ("Oltal 10", 13.0, "Torrent")])]),
    ("Quetiapine Fumarate", "Quetiapine", "Atypical Antipsychotic", "Schedule H", [("25mg", "Tablet", 2.2, [("Seroquel 25", 18.0, "AstraZeneca"), ("Qutipin 25", 7.2, "Sun Pharma"), ("Seroquin 25", 6.8, "Cipla")]), ("50mg", "Tablet", 3.8, [("Seroquel 50", 32.0, "AstraZeneca"), ("Qutipin 50", 12.5, "Sun Pharma")]), ("100mg", "Tablet", 6.5, [("Seroquel 100", 56.0, "AstraZeneca"), ("Qutipin 100", 21.0, "Sun Pharma")]), ("200mg", "Tablet", 11.0, [("Seroquel 200", 98.0, "AstraZeneca"), ("Qutipin 200", 36.0, "Sun Pharma")])]),
    ("Risperidone", "Risperidone", "Atypical Antipsychotic", "Schedule H", [("1mg", "Tablet", 1.2, [("Risperdal 1mg", 9.5, "Janssen"), ("Sizodon 1mg", 3.8, "Sun Pharma"), ("Respidon 1mg", 3.5, "Torrent")]), ("2mg", "Tablet", 2.0, [("Risperdal 2mg", 17.5, "Janssen"), ("Sizodon 2mg", 6.5, "Sun Pharma"), ("Respidon 2mg", 6.0, "Torrent")]), ("4mg", "Tablet", 3.6, [("Risperdal 4mg", 32.0, "Janssen"), ("Sizodon 4mg", 11.5, "Sun Pharma")])]),
    ("Baclofen", "Baclofen", "Skeletal Muscle Relaxant", "Schedule H", [("10mg", "Tablet", 2.5, [("Lioresal 10", 8.2, "Novartis"), ("Baclof 10", 7.8, "Intas"), ("Liofen 10", 7.5, "Sun Pharma")]), ("25mg", "Tablet", 5.2, [("Lioresal 25", 17.5, "Novartis"), ("Baclof 25", 16.5, "Intas")])]),
    ("Donepezil Hydrochloride", "Donepezil", "Anti-Alzheimer / Acetylcholinesterase Inhibitor", "Schedule H", [("5mg", "Tablet", 4.2, [("Aricept 5mg", 26.0, "Pfizer / Eisai"), ("Donecept 5mg", 13.5, "Cipla"), ("Alzepil 5mg", 13.0, "Torrent")]), ("10mg", "Tablet", 7.5, [("Aricept 10mg", 48.0, "Pfizer / Eisai"), ("Donecept 10mg", 24.0, "Cipla")])]),
    ("Folic Acid", "Folic Acid (Vitamin B9)", "Vitamin Supplement", "OTC", [("5mg", "Tablet", 0.5, [("Folvite 5mg", 1.8, "Pfizer"), ("Fol 5", 1.6, "Zydus"), ("Folygel 5", 1.5, "Micro Labs")])]),
    ("Zinc Sulfate / Zinc Acetate", "Zinc Supplement", "Essential Mineral", "OTC", [("20mg", "Tablet", 0.8, [("Zinconia 50mg", 2.8, "Micro Labs"), ("Zincovit", 3.2, "Apex"), ("Zevit", 2.5, "Macleods")])]),
    ("Betamethasone Dipropionate", "Betamethasone", "Topical Corticosteroid", "Schedule H", [("0.05% w/w", "Cream", 14.0, [("Diprovate Cream 20g", 48.0, "Fulford / MSD"), ("Betnovate Cream", 35.0, "GSK")])]),
    ("Hydrocortisone", "Hydrocortisone", "Corticosteroid", "Schedule H", [("10mg", "Tablet", 1.8, [("Cortef 10", 8.5, "Pfizer"), ("Locoid 10", 6.2, "Astellas")]), ("20mg", "Tablet", 3.2, [("Cortef 20", 15.0, "Pfizer")]), ("100mg", "Injection", 18.0, [("Solu-Cortef 100mg Inj", 95.0, "Pfizer"), ("Efcorlin 100mg Inj", 65.0, "GSK")])]),
    ("Mupirocin", "Mupirocin", "Topical Antibiotic", "Schedule H", [("2% w/w", "Ointment", 32.0, [("Bactroban Ointment 5g", 125.0, "GSK"), ("T-Bact 2% 5g", 110.0, "GSK"), ("Mupimet 2%", 95.0, "Sun Pharma")])]),
    ("Fusidic Acid", "Fusidic Acid", "Topical Antibacterial", "Schedule H", [("2% w/w", "Cream", 28.0, [("Fucidin Cream 10g", 98.0, "LEO Pharma"), ("Fudic Cream", 88.0, "Ranbaxy")])]),
    ("Clotrimazole", "Clotrimazole", "Antifungal (Topical/Vaginal)", "OTC", [("1% w/w", "Cream", 18.0, [("Candid Cream 30g", 75.0, "Glenmark"), ("Canesten 1% 30g", 82.0, "Bayer"), ("Surfaz Cream", 65.0, "Franco-Indian")]), ("100mg", "Vaginal Tablet", 12.0, [("Candid V6", 48.0, "Glenmark"), ("Canesten 100", 55.0, "Bayer")])]),
    ("Ketoconazole", "Ketoconazole", "Antifungal", "Schedule H", [("200mg", "Tablet", 5.5, [("Nizral 200", 24.0, "Janssen"), ("Fungicide 200", 18.0, "Cipla")]), ("2% w/v", "Shampoo", 45.0, [("Scalpe Plus Shampoo 60ml", 185.0, "Glenmark"), ("Nizral 2% Shampoo", 240.0, "Janssen")])]),
    ("Minoxidil", "Minoxidil", "Hair Regrowth Treatment", "Schedule H", [("2% w/v", "Solution", 95.0, [("Mintop 2% 60ml", 350.0, "Dr. Reddy's"), ("Tugain 2%", 320.0, "Cipla")]), ("5% w/v", "Solution", 145.0, [("Mintop 5% 60ml", 550.0, "Dr. Reddy's"), ("Tugain 5%", 520.0, "Cipla"), ("Morr 5%", 490.0, "Intas")])]),
    ("Tobramycin", "Tobramycin", "Ophthalmic Antibiotic", "Schedule H", [("0.3% w/v", "Eye Drops", 22.0, [("Tobrex Eye Drops 5ml", 115.0, "Alcon / Novartis"), ("Tobacin Eye Drops", 55.0, "Aristo")])]),
    ("Timolol Maleate", "Timolol", "Antiglaucoma (Beta Blocker)", "Schedule H", [("0.25% w/v", "Eye Drops", 18.0, [("Timoptic 0.25%", 85.0, "MSD"), ("Glucomol 0.25%", 45.0, "Allergan")]), ("0.5% w/v", "Eye Drops", 24.0, [("Timoptic 0.5%", 110.0, "MSD"), ("Glucomol 0.5%", 58.0, "Allergan")])]),
    ("Bimatoprost", "Bimatoprost", "Prostaglandin Analogue (Glaucoma)", "Schedule H", [("0.03% w/v", "Eye Drops", 95.0, [("Lumigan 0.03% 3ml", 420.0, "Allergan"), ("Careprost 3ml", 220.0, "Sun Pharma"), ("Bimaday 3ml", 210.0, "Zydus")])]),
    ("Azathioprine", "Azathioprine", "Immunosuppressant", "Schedule H", [("25mg", "Tablet", 4.2, [("Imuran 25", 22.0, "GSK"), ("Azoran 25", 14.5, "RPG")]), ("50mg", "Tablet", 7.5, [("Imuran 50", 38.0, "GSK"), ("Azoran 50", 25.0, "RPG")])]),
    ("Mycophenolate Mofetil", "Mycophenolate", "Immunosuppressant", "Schedule H", [("250mg", "Capsule", 16.0, [("CellCept 250", 68.0, "Roche"), ("Mycept 250", 45.0, "Panacea")]), ("500mg", "Tablet", 29.0, [("CellCept 500", 125.0, "Roche"), ("Mycept 500", 82.0, "Panacea"), ("Mofilet 500", 79.0, "Sun Pharma")])]),
    ("Tamoxifen Citrate", "Tamoxifen", "SERM (Breast Cancer)", "Schedule H", [("10mg", "Tablet", 2.8, [("Nolvadex 10", 14.0, "AstraZeneca"), ("Tamodex 10", 8.5, "Biochem")]), ("20mg", "Tablet", 5.2, [("Nolvadex 20", 26.0, "AstraZeneca"), ("Tamodex 20", 15.5, "Biochem")])]),
    ("Allopurinol", "Allopurinol", "Antigout / Xanthine Oxidase Inhibitor", "Schedule H", [("100mg", "Tablet", 1.5, [("Zyloric 100", 4.8, "GSK"), ("Aloric 100", 4.2, "Cipla")]), ("300mg", "Tablet", 3.2, [("Zyloric 300", 10.5, "GSK"), ("Aloric 300", 9.8, "Cipla")])]),
    ("Febuxostat", "Febuxostat", "Antigout / Uric Acid Reducer", "Schedule H", [("40mg", "Tablet", 4.2, [("Feburic 40", 13.5, "Ajanta"), ("Febutaz 40", 13.0, "Sun Pharma"), ("Febugood 40", 12.5, "Torrent")]), ("80mg", "Tablet", 7.5, [("Feburic 80", 23.0, "Ajanta"), ("Febutaz 80", 22.5, "Sun Pharma")])]),
    ("Spironolactone", "Spironolactone", "Potassium-Sparing Diuretic", "Schedule H", [("25mg", "Tablet", 1.8, [("Aldactone 25", 5.5, "RPG"), ("Spiractin 25", 5.2, "Sun Pharma")]), ("50mg", "Tablet", 3.2, [("Aldactone 50", 9.8, "RPG"), ("Spiractin 50", 9.2, "Sun Pharma")]), ("100mg", "Tablet", 5.5, [("Aldactone 100", 17.0, "RPG"), ("Spiractin 100", 16.0, "Sun Pharma")])]),
    ("Furosemide", "Furosemide", "Loop Diuretic", "Schedule H", [("20mg", "Tablet", 0.6, [("Lasix 20", 2.0, "Sanofi"), ("Frusenex 20", 1.8, "Torrent")]), ("40mg", "Tablet", 0.9, [("Lasix 40", 2.8, "Sanofi"), ("Frusenex 40", 2.5, "Torrent")]), ("10mg/ml", "Injection", 3.5, [("Lasix 2ml Inj", 12.0, "Sanofi"), ("Frusenex Inj", 10.5, "Torrent")])]),
    ("Torsemide", "Torsemide", "Loop Diuretic", "Schedule H", [("5mg", "Tablet", 1.6, [("Dytor 5", 5.5, "Cipla"), ("Torget 5", 5.2, "Zydus")]), ("10mg", "Tablet", 2.8, [("Dytor 10", 9.5, "Cipla"), ("Torget 10", 9.0, "Zydus"), ("Torsine 10", 8.8, "Sun Pharma")]), ("20mg", "Tablet", 4.8, [("Dytor 20", 16.0, "Cipla"), ("Torget 20", 15.2, "Zydus")])]),
    ("Methotrexate", "Methotrexate", "DMARD / Immunosuppressant", "Schedule H", [("2.5mg", "Tablet", 2.2, [("Folitrax 2.5", 7.5, "Ipca"), ("Trexotar 2.5", 7.0, "Sun Pharma")]), ("5mg", "Tablet", 3.8, [("Folitrax 5", 12.5, "Ipca"), ("Trexotar 5", 12.0, "Sun Pharma")]), ("7.5mg", "Tablet", 5.2, [("Folitrax 7.5", 17.5, "Ipca"), ("Trexotar 7.5", 16.8, "Sun Pharma")]), ("10mg", "Tablet", 6.8, [("Folitrax 10", 22.0, "Ipca"), ("Trexotar 10", 21.0, "Sun Pharma")]), ("15mg", "Tablet", 9.5, [("Folitrax 15", 31.0, "Ipca"), ("Trexotar 15", 29.5, "Sun Pharma")])]),
    ("Hydroxychloroquine Sulfate", "Hydroxychloroquine", "Antimalarial & Anti-arthritic", "Schedule H1", [("200mg", "Tablet", 3.5, [("HCQS 200", 11.8, "Ipca"), ("Plaquenil 200", 28.0, "Sanofi"), ("Zy-Q 200", 11.2, "Zydus")]), ("300mg", "Tablet", 5.0, [("HCQS 300", 16.5, "Ipca"), ("Zy-Q 300", 15.8, "Zydus")]), ("400mg", "Tablet", 6.5, [("HCQS 400", 21.5, "Ipca"), ("Plaquenil 400", 52.0, "Sanofi"), ("Zy-Q 400", 20.8, "Zydus")])]),
    ("Hydrochlorothiazide", "Hydrochlorothiazide", "Thiazide Diuretic", "Schedule H", [("12.5mg", "Tablet", 0.9, [("Aquazide 12.5", 3.2, "Sun Pharma")]), ("25mg", "Tablet", 1.4, [("Aquazide 25", 4.8, "Sun Pharma")]), ("50mg", "Tablet", 2.2, [("Aquazide 50", 7.5, "Sun Pharma")])]),
    ("Chlorthalidone", "Chlorthalidone", "Thiazide-like Diuretic", "Schedule H", [("6.25mg", "Tablet", 1.8, [("Thalizide 6.25", 5.5, "Sun Pharma")]), ("12.5mg", "Tablet", 2.5, [("Hygroton 12.5", 7.8, "Novartis"), ("Thalizide 12.5", 7.2, "Sun Pharma")]), ("25mg", "Tablet", 3.8, [("Hygroton 25", 12.0, "Novartis")])]),
    ("Indapamide", "Indapamide SR", "Diuretic / Antihypertensive", "Schedule H", [("1.5mg SR", "Tablet", 3.2, [("Natrilix SR 1.5", 11.5, "Serdia"), ("Lorvas SR", 10.8, "Torrent")])]),
    ("Clonidine Hydrochloride", "Clonidine", "Centrally Acting Antihypertensive", "Schedule H", [("100mcg", "Tablet", 0.8, [("Catapres 100", 3.2, "Boehringer"), ("Arkamin 100", 2.6, "Unichem")]), ("150mcg", "Tablet", 1.2, [("Catapres 150", 4.8, "Boehringer"), ("Arkamin 150", 3.8, "Unichem")])]),
    ("Doxazosin Mesylate", "Doxazosin", "Alpha Blocker (BPH / Hypertension)", "Schedule H", [("1mg", "Tablet", 2.2, [("Cardura 1mg", 8.5, "Pfizer"), ("Doxacard 1", 6.8, "Cipla")]), ("2mg", "Tablet", 3.8, [("Cardura 2mg", 14.5, "Pfizer"), ("Doxacard 2", 11.5, "Cipla")]), ("4mg", "Tablet", 6.5, [("Cardura 4mg", 24.0, "Pfizer"), ("Doxacard 4", 19.5, "Cipla")])]),
    ("Silodosin", "Silodosin", "Alpha-1A Adrenoceptor Blocker (BPH)", "Schedule H", [("4mg", "Capsule", 6.5, [("Silodal 4", 22.0, "Sun Pharma"), ("Rapilif 4", 21.0, "Ipca")]), ("8mg", "Capsule", 11.5, [("Silodal 8", 38.0, "Sun Pharma"), ("Rapilif 8", 36.0, "Ipca"), ("Sildoo 8", 35.0, "Dr. Reddy's")])]),
    ("Alfuzosin Hydrochloride", "Alfuzosin ER", "Alpha-1 Blocker (BPH)", "Schedule H", [("10mg ER", "Tablet", 8.2, [("Uroxatral 10", 38.0, "Sanofi"), ("Alfoo 10", 26.0, "Cipla"), ("Alfumax 10", 25.0, "Sun Pharma")])]),
    ("Nitroglycerin", "Nitroglycerin Controlled Release", "Antianginal Nitrate", "Schedule H", [("2.6mg", "Tablet", 3.2, [("Nitrocontin 2.6", 11.5, "Modi-Mundipharma"), ("Nitrolong 2.6", 10.8, "Mankind")]), ("6.4mg", "Tablet", 5.8, [("Nitrocontin 6.4", 19.8, "Modi-Mundipharma"), ("Nitrolong 6.4", 18.5, "Mankind")]), ("0.4mg/spray", "Sublingual Spray", 85.0, [("Nitrolingual Pumpspray", 320.0, "G.Pohl-Boskamp")])]),
    ("Isosorbide Mononitrate", "Isosorbide Mononitrate", "Antianginal Nitrate", "Schedule H", [("20mg", "Tablet", 1.8, [("Monotrate 20", 5.5, "Sun Pharma"), ("Ismo 20", 5.8, "Abbott")]), ("30mg SR", "Tablet", 3.2, [("Monotrate SR 30", 9.8, "Sun Pharma"), ("Ismo Retard 30", 10.5, "Abbott")]), ("60mg SR", "Tablet", 5.5, [("Monotrate SR 60", 17.5, "Sun Pharma")])]),
    ("Digoxin", "Digoxin", "Cardiac Glycoside (Heart Failure)", "Schedule H", [("0.25mg", "Tablet", 0.6, [("Lanoxin 0.25", 2.2, "GSK"), ("Digoxin 0.25", 1.8, "Samarth")])]),
    ("Amiodarone Hydrochloride", "Amiodarone", "Antiarrhythmic (Class III)", "Schedule H", [("100mg", "Tablet", 3.5, [("Cordarone 100", 12.0, "Sanofi"), ("Pacerone 100", 11.0, "Sun Pharma")]), ("200mg", "Tablet", 6.2, [("Cordarone 200", 21.5, "Sanofi"), ("Pacerone 200", 19.8, "Sun Pharma")])]),
    ("Warfarin Sodium", "Warfarin", "Vitamin K Antagonist Anticoagulant", "Schedule H", [("1mg", "Tablet", 0.9, [("Coumadin 1mg", 4.5, "BMS"), ("Uniwarfin 1", 2.8, "Unichem")]), ("2mg", "Tablet", 1.4, [("Coumadin 2mg", 6.8, "BMS"), ("Uniwarfin 2", 4.2, "Unichem")]), ("5mg", "Tablet", 2.5, [("Coumadin 5mg", 11.5, "BMS"), ("Uniwarfin 5", 7.5, "Unichem")])]),
    ("Diltiazem Hydrochloride", "Diltiazem", "Calcium Channel Blocker (Non-DHP)", "Schedule H", [("30mg", "Tablet", 1.4, [("Dilzem 30", 4.5, "Torrent"), ("Cardizem 30", 8.0, "Sanofi")]), ("60mg", "Tablet", 2.5, [("Dilzem 60", 7.8, "Torrent"), ("Cardizem 60", 14.5, "Sanofi")]), ("90mg SR", "Tablet", 4.2, [("Dilzem SR 90", 13.5, "Torrent")])]),
    ("Verapamil Hydrochloride", "Verapamil", "Calcium Channel Blocker (Non-DHP)", "Schedule H", [("40mg", "Tablet", 1.2, [("Calaptin 40", 3.8, "Abbott"), ("Isoptin 40", 5.5, "Knoll")]), ("80mg", "Tablet", 2.2, [("Calaptin 80", 6.8, "Abbott"), ("Isoptin 80", 9.8, "Knoll")]), ("120mg SR", "Tablet", 4.5, [("Calaptin 120 SR", 14.0, "Abbott")])]),
    ("Ivabradine", "Ivabradine", "HCN Blocker (Angina / Heart Failure)", "Schedule H", [("5mg", "Tablet", 6.5, [("Coralan 5", 28.0, "Serdia"), ("Ivabrad 5", 19.5, "Lupin"), ("Inapure 5", 18.0, "Torrent")]), ("7.5mg", "Tablet", 9.8, [("Coralan 7.5", 42.0, "Serdia"), ("Ivabrad 7.5", 28.0, "Lupin")])]),
    ("Sacubitril + Valsartan", "Sacubitril + Valsartan (ARNI)", "Heart Failure (ARNI)", "Schedule H", [("24mg + 26mg (50mg)", "Tablet", 28.0, [("Vymada 50", 110.0, "Novartis / Cipla"), ("Entresto 50", 145.0, "Novartis"), ("Azmarda 50", 105.0, "Torrent")]), ("49mg + 51mg (100mg)", "Tablet", 38.0, [("Vymada 100", 145.0, "Novartis / Cipla"), ("Entresto 100", 195.0, "Novartis"), ("Azmarda 100", 140.0, "Torrent")]), ("97mg + 103mg (200mg)", "Tablet", 48.0, [("Vymada 200", 185.0, "Novartis / Cipla"), ("Entresto 200", 250.0, "Novartis")])]),
    ("Canagliflozin", "Canagliflozin", "Antidiabetic (SGLT-2 Inhibitor)", "Schedule H", [("100mg", "Tablet", 14.0, [("Invokana 100", 68.0, "Janssen"), ("Sulisent 100", 38.0, "Sun Pharma")]), ("300mg", "Tablet", 24.0, [("Invokana 300", 115.0, "Janssen"), ("Sulisent 300", 65.0, "Sun Pharma")])]),
    ("Acarbose", "Acarbose", "Alpha-Glucosidase Inhibitor", "Schedule H", [("25mg", "Tablet", 1.8, [("Glucobay 25", 5.8, "Bayer"), ("Asucrose 25", 5.2, "Micro Labs")]), ("50mg", "Tablet", 3.2, [("Glucobay 50", 10.2, "Bayer"), ("Asucrose 50", 9.5, "Micro Labs")])]),
    ("Glibenclamide", "Glibenclamide", "Antidiabetic (Sulfonylurea)", "Schedule H", [("2.5mg", "Tablet", 0.6, [("Daonil 2.5", 2.2, "Sanofi"), ("Euglucon 2.5", 2.0, "Abbott")]), ("5mg", "Tablet", 0.9, [("Daonil 5", 3.2, "Sanofi"), ("Euglucon 5", 2.8, "Abbott")])]),
    ("Repaglinide", "Repaglinide", "Meglitinide Antidiabetic", "Schedule H", [("0.5mg", "Tablet", 1.8, [("Novonorm 0.5", 7.5, "Novo Nordisk"), ("Eurepa 0.5", 5.5, "Torrent")]), ("1mg", "Tablet", 3.2, [("Novonorm 1mg", 13.0, "Novo Nordisk"), ("Eurepa 1mg", 9.5, "Torrent")]), ("2mg", "Tablet", 5.5, [("Novonorm 2mg", 22.0, "Novo Nordisk"), ("Eurepa 2mg", 16.5, "Torrent")])]),
    ("Levosulpiride", "Levosulpiride", "Prokinetic & Antipsychotic", "Schedule H", [("25mg", "Tablet", 2.8, [("Levazeo 25", 9.5, "Torrent"), ("Neopride 25", 9.0, "Intas"), ("Lesuride 25", 8.8, "Sun Pharma")]), ("75mg SR", "Tablet", 6.5, [("Levazeo SR 75", 21.0, "Torrent"), ("Neopride SR 75", 20.0, "Intas")])]),
    ("Rabeprazole + Levosulpiride", "Rabeprazole + Levosulpiride SR", "Gastroprokinetic Combination", "Schedule H", [("20mg + 75mg SR", "Capsule", 6.8, [("Razo-L", 23.5, "Dr. Reddy's"), ("Rabesec-L", 22.0, "Cipla"), ("Happi-L", 21.5, "Zydus")])]),
    ("Pantoprazole + Levosulpiride", "Pantoprazole + Levosulpiride SR", "Gastroprokinetic Combination", "Schedule H", [("40mg + 75mg SR", "Capsule", 6.5, [("Pan-L", 22.5, "Alkem"), ("Pantocid-L", 22.0, "Sun Pharma")])]),
    ("Famotidine", "Famotidine", "H2 Receptor Antagonist", "OTC", [("20mg", "Tablet", 0.8, [("Famocid 20", 2.5, "Sun Pharma"), ("Pepcid 20", 6.5, "J&J")]), ("40mg", "Tablet", 1.4, [("Famocid 40", 4.2, "Sun Pharma"), ("Pepcid 40", 11.5, "J&J")])]),
    ("Ranitidine", "Ranitidine Hydrochloride", "H2 Receptor Antagonist", "Schedule H", [("150mg", "Tablet", 0.9, [("Rantac 150", 2.8, "J.B. Chemicals"), ("Zinetac 150", 2.6, "GSK"), ("Aciloc 150", 2.5, "Cadila")]), ("300mg", "Tablet", 1.6, [("Rantac 300", 5.2, "J.B. Chemicals"), ("Aciloc 300", 4.8, "Cadila")]), ("25mg/ml", "Injection", 2.8, [("Rantac 2ml Inj", 9.5, "J.B. Chemicals"), ("Aciloc Inj", 8.8, "Cadila")])]),
    ("Dicyclomine Hydrochloride", "Dicyclomine", "Antispasmodic", "Schedule H", [("10mg", "Tablet", 0.8, [("Spasmonil 10", 2.6, "Cipla"), ("Cyclopam", 2.5, "Indoco")]), ("20mg", "Tablet", 1.3, [("Spasmonil 20", 4.2, "Cipla")]), ("10mg/ml", "Injection", 3.2, [("Spasmonil Inj", 11.0, "Cipla")])]),
    ("Drotaverine Hydrochloride", "Drotaverine", "Smooth Muscle Antispasmodic", "Schedule H", [("40mg", "Tablet", 2.2, [("Drotin 40", 7.5, "Walter Bushnell"), ("Dorafem 40", 6.8, "Sun Pharma")]), ("80mg", "Tablet", 3.8, [("Drotin DS 80", 13.0, "Walter Bushnell"), ("Dorafem DS", 12.0, "Sun Pharma")]), ("20mg/ml", "Injection", 5.5, [("Drotin 2ml Inj", 18.5, "Walter Bushnell")])]),
    ("Drotaverine + Mefenamic Acid", "Drotaverine + Mefenamic Acid", "Antispasmodic & Analgesic", "Schedule H", [("80mg + 250mg", "Tablet", 4.5, [("Drotin-M", 15.5, "Walter Bushnell"), ("Drota-M", 14.5, "Aristo")])]),
    ("Cinnarizine", "Cinnarizine", "Antivertigo / Antihistamine", "Schedule H", [("25mg", "Tablet", 1.4, [("Stugeron 25", 4.8, "Janssen"), ("Vertigon 25", 4.2, "Cipla"), ("Cinzan 25", 4.0, "FDC")]), ("75mg", "Tablet", 3.2, [("Stugeron 75", 10.5, "Janssen"), ("Vertigon 75", 9.5, "Cipla")])]),
    ("Betahistine Dihydrochloride", "Betahistine", "Antivertigo (Meniere's Disease)", "Schedule H", [("8mg", "Tablet", 1.8, [("Vertin 8", 6.2, "Abbott"), ("Betavert 8", 5.8, "Sun Pharma")]), ("16mg", "Tablet", 3.4, [("Vertin 16", 11.8, "Abbott"), ("Betavert 16", 11.2, "Sun Pharma")]), ("24mg", "Tablet", 4.8, [("Vertin 24", 16.5, "Abbott"), ("Betavert 24", 15.8, "Sun Pharma")])]),
    ("Piracetam", "Piracetam", "Nootropic (Cognitive Enhancer)", "Schedule H", [("400mg", "Capsule", 2.5, [("Nootropil 400", 8.5, "UCB"), ("Normabrain 400", 7.8, "Torrent")]), ("800mg", "Tablet", 4.5, [("Nootropil 800", 15.5, "UCB"), ("Normabrain 800", 14.2, "Torrent")]), ("1200mg", "Tablet", 6.8, [("Nootropil 1200", 23.0, "UCB"), ("Normabrain 1200", 21.0, "Torrent")]), ("200mg/ml", "Injection", 18.0, [("Nootropil 15ml Inj", 62.0, "UCB")])]),
    ("Citicoline", "Citicoline", "Neuroprotective Agent", "Schedule H", [("500mg", "Tablet", 14.0, [("Stiloz 500", 48.0, "Sun Pharma"), ("Ceham 500", 46.0, "Torrent"), ("Citistar 500", 44.0, "Lupin")]), ("1000mg", "Tablet", 26.0, [("Stiloz 1000", 88.0, "Sun Pharma"), ("Ceham 1000", 85.0, "Torrent")]), ("500mg/2ml", "Injection", 32.0, [("Ceham 2ml Inj", 110.0, "Torrent"), ("Stiloz Inj", 105.0, "Sun Pharma")])]),
    ("Nimodipine", "Nimodipine", "Cerebral Vasodilator", "Schedule H", [("30mg", "Tablet", 4.8, [("Nimotop 30", 16.5, "Bayer"), ("Nimodip 30", 15.0, "Torrent")])]),
    ("Flunarizine", "Flunarizine", "Migraine Prophylaxis", "Schedule H", [("5mg", "Tablet", 1.8, [("Sibelium 5", 6.2, "Janssen"), ("Flunarin 5", 5.5, "FDC")]), ("10mg", "Tablet", 3.2, [("Sibelium 10", 10.8, "Janssen"), ("Flunarin 10", 9.8, "FDC"), ("Migranex 10", 9.5, "Cipla")])]),
    ("Propranolol Hydrochloride", "Propranolol", "Beta Blocker (Migraine/Tremors)", "Schedule H", [("10mg", "Tablet", 0.8, [("Inderal 10", 2.8, "Abbott"), ("Ciplar 10", 2.5, "Cipla")]), ("20mg", "Tablet", 1.4, [("Inderal 20", 4.8, "Abbott"), ("Ciplar 20", 4.2, "Cipla")]), ("40mg", "Tablet", 2.4, [("Inderal 40", 8.2, "Abbott"), ("Ciplar 40", 7.5, "Cipla")]), ("40mg TR", "Capsule", 3.5, [("Ciplar LA 40", 11.5, "Cipla")])]),
    ("Topiramate", "Topiramate", "Anticonvulsant & Migraine Prophylaxis", "Schedule H", [("25mg", "Tablet", 2.2, [("Topamac 25", 7.8, "Janssen"), ("Topirol 25", 6.8, "Sun Pharma")]), ("50mg", "Tablet", 4.2, [("Topamac 50", 14.5, "Janssen"), ("Topirol 50", 13.0, "Sun Pharma")]), ("100mg", "Tablet", 7.8, [("Topamac 100", 27.0, "Janssen"), ("Topirol 100", 24.5, "Sun Pharma")])]),
    ("Lamotrigine", "Lamotrigine", "Antiepileptic & Mood Stabilizer", "Schedule H", [("25mg", "Tablet", 2.5, [("Lamictal 25", 8.8, "GSK"), ("Lamitor 25", 7.5, "Torrent")]), ("50mg", "Tablet", 4.5, [("Lamictal 50", 15.5, "GSK"), ("Lamitor 50", 13.8, "Torrent")]), ("100mg", "Tablet", 8.2, [("Lamictal 100", 28.5, "GSK"), ("Lamitor 100", 25.0, "Torrent")])]),
    ("Oxcarbazepine", "Oxcarbazepine", "Anticonvulsant", "Schedule H", [("150mg", "Tablet", 3.2, [("Trileptal 150", 11.0, "Novartis"), ("Oxetol 150", 9.8, "Sun Pharma")]), ("300mg", "Tablet", 5.8, [("Trileptal 300", 19.8, "Novartis"), ("Oxetol 300", 17.5, "Sun Pharma")]), ("600mg", "Tablet", 10.5, [("Trileptal 600", 36.0, "Novartis"), ("Oxetol 600", 32.0, "Sun Pharma")])]),
    ("Clobazam", "Clobazam", "Anticonvulsant (Benzodiazepine)", "Schedule H1", [("5mg", "Tablet", 1.8, [("Frisium 5", 6.2, "Sanofi"), ("Cloba 5", 5.5, "Intas")]), ("10mg", "Tablet", 3.2, [("Frisium 10", 11.0, "Sanofi"), ("Cloba 10", 9.8, "Intas")]), ("20mg", "Tablet", 5.8, [("Frisium 20", 19.5, "Sanofi"), ("Cloba 20", 18.0, "Intas")])]),
    ("Haloperidol", "Haloperidol", "Typical Antipsychotic", "Schedule H", [("1.5mg", "Tablet", 0.9, [("Serenace 1.5", 3.2, "RPG"), ("Halopidol 1.5", 2.8, "Cipla")]), ("5mg", "Tablet", 1.8, [("Serenace 5", 6.0, "RPG"), ("Halopidol 5", 5.2, "Cipla")]), ("5mg/ml", "Injection", 5.0, [("Serenace 1ml Inj", 16.5, "RPG"), ("Halopidol Inj", 14.8, "Cipla")])]),
    ("Aripiprazole", "Aripiprazole", "Atypical Antipsychotic", "Schedule H", [("5mg", "Tablet", 3.8, [("Abilify 5mg", 38.0, "Otsuka"), ("Arip MT 5", 12.5, "Torrent"), ("Arpizol 5", 12.0, "Sun Pharma")]), ("10mg", "Tablet", 6.5, [("Abilify 10mg", 65.0, "Otsuka"), ("Arip MT 10", 21.0, "Torrent"), ("Arpizol 10", 20.0, "Sun Pharma")]), ("15mg", "Tablet", 9.2, [("Abilify 15mg", 92.0, "Otsuka"), ("Arip MT 15", 29.5, "Torrent")])]),
    ("Amisulpride", "Amisulpride", "Atypical Antipsychotic", "Schedule H", [("50mg", "Tablet", 3.2, [("Solian 50", 11.5, "Sanofi"), ("Sulpitac 50", 9.8, "Sun Pharma")]), ("100mg", "Tablet", 5.8, [("Solian 100", 21.0, "Sanofi"), ("Sulpitac 100", 17.5, "Sun Pharma")]), ("200mg", "Tablet", 10.5, [("Solian 200", 38.0, "Sanofi"), ("Sulpitac 200", 32.0, "Sun Pharma")])]),
    ("Flupentixol + Melitracen", "Flupentixol + Melitracen", "Anxiolytic & Antidepressant", "Schedule H", [("0.5mg + 10mg", "Tablet", 2.4, [("Deanxit", 8.2, "Lundbeck"), ("Flunil-M", 6.8, "Sun Pharma"), ("Placida", 6.5, "Mankind")])]),
    ("Hydroxyzine Hydrochloride", "Hydroxyzine", "Anxiolytic & Anti-allergic", "Schedule H", [("10mg", "Tablet", 1.4, [("Atarax 10", 4.8, "Dr. Reddy's"), ("Hypnotex 10", 4.2, "Cipla")]), ("25mg", "Tablet", 2.5, [("Atarax 25", 8.5, "Dr. Reddy's"), ("Hypnotex 25", 7.5, "Cipla")]), ("6mg/5ml", "Syrup", 24.0, [("Atarax Syrup 100ml", 78.0, "Dr. Reddy's")])]),
    ("Promethazine Hydrochloride", "Promethazine", "Antihistamine & Antiemetic", "Schedule H", [("10mg", "Tablet", 0.8, [("Phenergan 10", 2.8, "Abbott"), ("Avomine 10", 2.5, "Sanofi")]), ("25mg", "Tablet", 1.5, [("Phenergan 25", 5.2, "Abbott"), ("Avomine 25", 4.8, "Sanofi")]), ("25mg/ml", "Injection", 4.2, [("Phenergan 2ml Inj", 14.5, "Abbott")])]),
    ("Betamethasone Sodium Phosphate", "Betamethasone Oral", "Glucocorticoid", "Schedule H", [("0.5mg", "Tablet", 0.45, [("Betnesol 0.5mg", 1.6, "GSK"), ("Betnelan 0.5mg", 1.5, "Glaxo")]), ("4mg/ml", "Injection", 3.2, [("Betnesol 2ml Inj", 11.5, "GSK")])]),
    ("Dexamethasone Sodium Phosphate", "Dexamethasone", "Glucocorticoid", "Schedule H", [("0.5mg", "Tablet", 0.35, [("Dexona 0.5mg", 1.2, "Zydus"), ("Decdan 0.5mg", 1.1, "Wockhardt")]), ("2mg", "Tablet", 0.9, [("Dexona 2mg", 3.2, "Zydus")]), ("4mg/ml", "Injection", 3.5, [("Dexona 2ml Inj", 11.8, "Zydus"), ("Decdan Inj", 10.5, "Wockhardt")])]),
    ("Methylprednisolone", "Methylprednisolone", "Corticosteroid", "Schedule H", [("4mg", "Tablet", 2.2, [("Medrol 4mg", 7.8, "Pfizer"), ("Predmet 4mg", 6.8, "Sun Pharma")]), ("8mg", "Tablet", 4.2, [("Medrol 8mg", 14.5, "Pfizer"), ("Predmet 8mg", 12.8, "Sun Pharma")]), ("16mg", "Tablet", 7.8, [("Medrol 16mg", 26.5, "Pfizer"), ("Predmet 16mg", 23.5, "Sun Pharma")]), ("40mg", "Injection", 28.0, [("Solu-Medrol 40mg Inj", 110.0, "Pfizer"), ("Depo-Medrol 40mg", 95.0, "Pfizer")]), ("125mg", "Injection", 75.0, [("Solu-Medrol 125mg Inj", 295.0, "Pfizer")])]),
    ("Prednisolone", "Prednisolone", "Corticosteroid", "Schedule H", [("5mg", "Tablet", 0.6, [("Wysolone 5", 2.2, "Pfizer"), ("Omnacortil 5", 2.0, "Macleods")]), ("10mg", "Tablet", 1.1, [("Wysolone 10", 3.8, "Pfizer"), ("Omnacortil 10", 3.5, "Macleods")]), ("20mg", "Tablet", 2.0, [("Wysolone 20", 6.8, "Pfizer"), ("Omnacortil 20", 6.2, "Macleods")]), ("40mg", "Tablet", 3.8, [("Wysolone 40", 12.5, "Pfizer"), ("Omnacortil 40", 11.5, "Macleods")])]),
    ("Deflazacort", "Deflazacort", "Glucocorticoid", "Schedule H", [("6mg", "Tablet", 4.2, [("Defcort 6", 14.5, "Macleods"), ("Orthocort 6", 13.8, "Alkem"), ("Mahacort 6", 13.5, "Mankind")]), ("12mg", "Tablet", 7.8, [("Defcort 12", 26.0, "Macleods"), ("Orthocort 12", 24.5, "Alkem")]), ("30mg", "Tablet", 16.5, [("Defcort 30", 55.0, "Macleods"), ("Orthocort 30", 52.0, "Alkem")])]),
    ("Dydrogesterone", "Dydrogesterone", "Progestogen (Pregnancy Support)", "Schedule H", [("10mg", "Tablet", 24.0, [("Duphaston 10mg", 82.0, "Abbott"), ("Dydroboon 10mg", 65.0, "Lupin"), ("Dydrofem 10mg", 62.0, "Sun Pharma")])]),
    ("Natural Micronized Progesterone", "Progesterone", "Progestin", "Schedule H", [("100mg", "Capsule", 14.0, [("Susten 100", 48.0, "Sun Pharma"), ("Naturogest 100", 44.0, "Zydus")]), ("200mg", "Capsule", 24.0, [("Susten 200", 82.0, "Sun Pharma"), ("Naturogest 200", 78.0, "Zydus"), ("Dubagest 200", 75.0, "Torrent")]), ("300mg SR", "Tablet", 34.0, [("Susten SR 300", 115.0, "Sun Pharma"), ("Naturogest SR 300", 108.0, "Zydus")])]),
    ("Norethisterone", "Norethisterone", "Progestin (Menstrual Regulation)", "Schedule H", [("5mg", "Tablet", 3.2, [("Primolut-N 5mg", 11.5, "Bayer"), ("Regestrone 5mg", 9.8, "Novartis"), ("Sysron-N 5mg", 9.2, "Systopic")])]),
    ("Cabergoline", "Cabergoline", "Dopamine Agonist (Prolactin Inhibitor)", "Schedule H", [("0.5mg", "Tablet", 18.0, [("Dostinex 0.5mg", 85.0, "Pfizer"), ("Caberlin 0.5mg", 52.0, "Sun Pharma"), ("Cabgolin 0.5mg", 48.0, "Sun Pharma")])]),
    ("Danazol", "Danazol", "Synthetic Steroid (Endometriosis)", "Schedule H", [("50mg", "Capsule", 5.5, [("Danogen 50", 18.0, "Cipla"), ("Ladogal 50", 22.0, "Sanofi")]), ("100mg", "Capsule", 9.8, [("Danogen 100", 32.0, "Cipla"), ("Ladogal 100", 38.0, "Sanofi")]), ("200mg", "Capsule", 16.5, [("Danogen 200", 55.0, "Cipla")])]),
    ("Mifepristone", "Mifepristone", "Progesterone Receptor Modulator", "Schedule H", [("200mg", "Tablet", 85.0, [("Mifegyne 200", 380.0, "Exelgyn"), ("Mifeprin 200", 280.0, "Sun Pharma"), ("MTP Kit Component", 290.0, "Cipla")])]),
    ("Misoprostol", "Misoprostol", "Prostaglandin E1 Analogue", "Schedule H", [("200mcg", "Tablet", 12.0, [("Cytotec 200", 45.0, "Pfizer"), ("Misoprost 200", 26.0, "Cipla")])]),
    ("Tranexamic Acid", "Tranexamic Acid", "Antifibrinolytic (Hemostatic)", "Schedule H", [("500mg", "Tablet", 7.5, [("Cyklokapron 500", 28.0, "Pfizer"), ("Pause 500", 21.0, "Emcure"), ("Texakind 500", 20.0, "Mankind")]), ("500mg/5ml", "Injection", 18.0, [("Pause 5ml Inj", 65.0, "Emcure"), ("Texakind Inj", 60.0, "Mankind")])]),
    ("Tranexamic Acid + Mefenamic Acid", "Tranexamic Acid + Mefenamic Acid", "Hemostatic & Analgesic Combo", "Schedule H", [("500mg + 250mg", "Tablet", 11.5, [("Pause-MF", 35.0, "Emcure"), ("Texakind-MF", 32.0, "Mankind"), ("Trapic-MF", 34.0, "Sun Pharma")])]),
    ("Ethamsylate", "Ethamsylate", "Hemostatic Agent", "Schedule H", [("250mg", "Tablet", 3.2, [("Dicynene 250", 11.5, "Sanofi"), ("Ethasyl 250", 9.8, "FDC")]), ("500mg", "Tablet", 5.8, [("Dicynene 500", 21.0, "Sanofi"), ("Ethasyl 500", 18.5, "FDC")]), ("125mg/ml", "Injection", 8.5, [("Dicynene 2ml Inj", 28.0, "Sanofi")])]),
    ("Silymarin", "Silymarin (Milk Thistle)", "Hepatoprotective", "OTC", [("70mg", "Tablet", 3.8, [("Silybon 70", 12.5, "Micro Labs"), ("Hepasil 70", 11.8, "Sun Pharma")]), ("140mg", "Tablet", 6.8, [("Silybon 140", 22.0, "Micro Labs"), ("Hepasil 140", 21.0, "Sun Pharma")])]),
    ("L-Ornithine L-Aspartate", "L-Ornithine L-Aspartate", "Liver Support / Hepatic Encephalopathy", "Schedule H", [("150mg", "Tablet", 5.5, [("Hepa-Merz 150", 18.5, "Merz"), ("Lupiliv LOLA", 16.0, "Lupin")]), ("5g/10ml", "Injection", 65.0, [("Hepa-Merz Infusion", 240.0, "Merz")])]),
    ("Potassium Chloride", "Potassium Chloride", "Electrolyte Replenisher", "Schedule H", [("500mg PR", "Tablet", 1.8, [("Potclor 500", 5.8, "Walter Bushnell"), ("K-Lyte", 6.2, "Cipla")]), ("10% w/v", "Syrup", 24.0, [("Potklor Oral Solution 200ml", 78.0, "Walter Bushnell")])]),
    ("Sodium Bicarbonate", "Sodium Bicarbonate", "Systemic Alkalinizer", "OTC", [("500mg", "Tablet", 0.6, [("Sodamint 500mg", 1.8, "Wallace"), ("Bicarb 500", 1.7, "Cipla")]), ("1000mg", "Tablet", 1.1, [("Sodamint 1000mg", 3.4, "Wallace")])]),
    ("Disodium Hydrogen Citrate", "Disodium Hydrogen Citrate", "Urinary Alkalinizer", "OTC", [("1.37g/5ml", "Syrup", 22.0, [("Alkamac Syrup 100ml", 75.0, "Macleods"), ("Cital Syrup 100ml", 72.0, "Indoco"), ("Alkarate Syrup", 70.0, "Alkem")])]),
    ("Glucosamine Sulfate + Chondroitin", "Glucosamine + Chondroitin", "Joint Health Supplement", "OTC", [("750mg + 600mg", "Tablet", 6.5, [("Jointace DN", 24.0, "Meyer"), ("Cartigen Forte", 22.0, "Pharmed"), ("Lubrijoint", 21.0, "Sun Pharma")])]),
    ("Diacerein", "Diacerein", "Osteoarthritis Treatment (IL-1 Inhibitor)", "Schedule H", [("50mg", "Capsule", 5.5, [("Artodar 50", 18.5, "Torrent"), ("Dycerin 50", 17.0, "Glenmark"), ("Cartisaf 50", 16.5, "Sun Pharma")])]),
    ("Collagen Peptide + Sodium Hyaluronate", "Collagen Peptide Complex", "Cartilage & Joint Regenerator", "OTC", [("10g Sachet", "Sachet", 35.0, [("Collaflex Pro Sachet", 125.0, "Pharmed"), ("Cartigen Pro", 115.0, "Pharmed")])]),
    ("Coenzyme Q10 + Levocarnitine + Lycopene", "Antioxidant & Mitochondrial Complex", "Nutraceutical / Fertility", "OTC", [("100mg + 500mg + 2.5mg", "Tablet", 18.0, [("Ubicar", 65.0, "Torrent"), ("Carnisure-Q", 58.0, "Torrent"), ("CoQ Forte", 62.0, "Pharmed")])]),
    ("Omega-3 Fatty Acids", "Omega-3 Fish Oil", "Cardiovascular Supplement", "OTC", [("1000mg (180 EPA/120 DHA)", "Softgel", 4.5, [("Maxepa Softgel", 16.0, "Merck"), ("Seven Seas Seacod", 12.0, "P&G"), ("Nutriva Omega-3", 14.5, "Sun Pharma")])]),
    ("Probiotics Multi-strain", "Multi-strain Probiotic", "Gut Flora Restorative", "OTC", [("5 Billion Spores", "Capsule", 4.8, [("Darolac Capsule", 16.5, "Aristo"), ("Econorm Capsule", 22.0, "Dr. Reddy's"), ("Enterogermina Oral Vial", 45.0, "Sanofi"), ("Bifilac", 15.0, "Tablets India")])]),
    ("Racecadotril", "Racecadotril", "Enkephalinase Inhibitor (Antidiarrheal)", "Schedule H", [("10mg", "Sachet", 3.8, [("Zedott 10 Sachet", 12.5, "Torrent"), ("Redotil 10 Sachet", 12.0, "Dr. Reddy's")]), ("30mg", "Sachet", 5.5, [("Zedott 30 Sachet", 18.0, "Torrent"), ("Redotil 30 Sachet", 17.5, "Dr. Reddy's")]), ("100mg", "Capsule", 8.2, [("Zedott 100", 27.0, "Torrent"), ("Redotil 100", 26.0, "Dr. Reddy's"), ("Enuff 100", 24.5, "Hetero")])]),
    ("Doxofylline", "Doxofylline", "Xanthine Bronchodilator", "Schedule H", [("400mg", "Tablet", 3.8, [("Doxolin 400", 12.5, "Zydus"), ("Doxoril 400", 12.0, "Macleods"), ("Ventidox 400", 11.5, "Lupin")]), ("650mg SR", "Tablet", 6.2, [("Doxolin SR 650", 20.0, "Zydus"), ("Doxoril SR 650", 19.0, "Macleods")])]),
    ("Levocloperastine Fendizoate", "Levocloperastine", "Cough Suppressant", "Schedule H", [("20mg/5ml", "Syrup", 34.0, [("Cloperastine Syrup 100ml", 115.0, "Macleods"), ("Lupituss 100ml", 120.0, "Lupin"), ("Flutuss 100ml", 110.0, "Torrent")])]),
    ("Mirtazapine", "Mirtazapine", "Antidepressant (NaSSA)", "Schedule H", [("7.5mg", "Tablet", 2.8, [("Remeron 7.5", 14.0, "Organon"), ("Mirtaz 7.5", 8.5, "Sun Pharma")]), ("15mg", "Tablet", 4.5, [("Remeron 15", 22.0, "Organon"), ("Mirtaz 15", 14.0, "Sun Pharma"), ("Mirnite 15", 13.5, "Intas")]), ("30mg", "Tablet", 7.8, [("Remeron 30", 38.0, "Organon"), ("Mirtaz 30", 24.0, "Sun Pharma"), ("Mirnite 30", 23.0, "Intas")])]),
    ("Bupropion Hydrochloride", "Bupropion XL", "NDRI Antidepressant", "Schedule H", [("150mg XL", "Tablet", 7.5, [("Wellbutrin XL 150", 38.0, "GSK"), ("Bupron XL 150", 24.0, "Sun Pharma"), ("Unidep SR 150", 22.5, "Torrent")]), ("300mg XL", "Tablet", 13.5, [("Wellbutrin XL 300", 68.0, "GSK"), ("Bupron XL 300", 42.0, "Sun Pharma")])]),
    ("Vortioxetine", "Vortioxetine", "Multimodal Antidepressant", "Schedule H", [("5mg", "Tablet", 9.5, [("Brintellix 5", 48.0, "Lundbeck"), ("Voxit 5", 28.0, "Torrent")]), ("10mg", "Tablet", 16.5, [("Brintellix 10", 82.0, "Lundbeck"), ("Voxit 10", 48.0, "Torrent")])]),
    ("Agomelatine", "Agomelatine", "Melatonergic Antidepressant", "Schedule H", [("25mg", "Tablet", 14.0, [("Valdoxan 25", 72.0, "Servier"), ("Agoprex 25", 42.0, "Torrent"), ("Novadep 25", 38.0, "Sun Pharma")])]),
    ("Vardenafil", "Vardenafil", "PDE5 Inhibitor (ED)", "Schedule H", [("10mg", "Tablet", 8.5, [("Levitra 10mg", 65.0, "Bayer"), ("Valif 10", 28.0, "Ajanta")]), ("20mg", "Tablet", 14.0, [("Levitra 20mg", 110.0, "Bayer"), ("Valif 20", 48.0, "Ajanta")])]),
    ("Avanafil", "Avanafil", "Rapid Acting PDE5 Inhibitor", "Schedule H", [("50mg", "Tablet", 12.0, [("Stendra 50", 95.0, "Vivus"), ("Avana 50", 38.0, "Sunrise")]), ("100mg", "Tablet", 20.0, [("Stendra 100", 160.0, "Vivus"), ("Avana 100", 62.0, "Sunrise")])]),
    ("Dapoxetine Hydrochloride", "Dapoxetine", "Short-acting SSRI (PE)", "Schedule H", [("30mg", "Tablet", 7.5, [("Priligy 30mg", 45.0, "Menarini"), ("Duratia 30", 24.0, "Fortune"), ("Sustenex 30", 22.0, "Sun Pharma")]), ("60mg", "Tablet", 13.0, [("Priligy 60mg", 78.0, "Menarini"), ("Duratia 60", 42.0, "Fortune")])])
]

# Stores dataset
STORES = [
    ("Jan Aushadhi Kendra - Sector 12", "Shop 4, Huda Market, Sector 12", "Noida", "201301", 28.59, 77.34, "Uttar Pradesh", "0120-4567890"),
    ("Generic Pharma Plus", "Main Road, Karkarduma", "Delhi", "110092", 28.64, 77.30, "Delhi", "011-22334455"),
    ("Affordable Meds Kendra", "G-6, Lajpat Nagar II", "Delhi", "110024", 28.56, 77.24, "Delhi", "011-33445566"),
    ("Jan Aushadhi Store - Andheri East", "Marol Pipe Line, JB Nagar", "Mumbai", "400059", 19.11, 72.87, "Maharashtra", "022-66778899"),
    ("Pradhan Mantri Jan Aushadhi - Indiranagar", "100 Feet Road, HAL 2nd Stage", "Bengaluru", "560038", 12.97, 77.64, "Karnataka", "080-41223344"),
    ("Generic Medicine Kendra - T. Nagar", "Pondy Bazaar, T. Nagar", "Chennai", "600017", 13.04, 80.23, "Tamil Nadu", "044-24335566"),
    ("Jan Aushadhi Seva Kendra - Banjara Hills", "Road No. 12, Banjara Hills", "Hyderabad", "500034", 17.41, 78.44, "Telangana", "040-23344556"),
    ("Generic Meds Point - Salt Lake", "Sector 1, Salt Lake City", "Kolkata", "700064", 22.58, 88.41, "West Bengal", "033-23345566")
]


def _is_postgres(url: str) -> bool:
    return bool(url) and "postgresql://" in url and "@host:" not in url


def _adapt_schema_for_sqlite(schema_sql: str) -> str:
    sql = schema_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY")
    sql = re.sub(r"COMMENT ON .*?;\s*", "", sql, flags=re.DOTALL)
    sql = re.sub(r"\s*CHECK\s*\([^)]+\)", "", sql)
    sql = sql.replace(" FLOAT", " REAL")
    return sql


def compile_all():
    total_list = list(CATALOG)
    for salt, generic, cat, sch, variants in EXTRA_MEDICINES:
        total_list.append({
            "salt": salt,
            "generic": generic,
            "cat": cat,
            "sch": sch,
            "variants": variants
        })
    return total_list


def seed():
    database_url = os.getenv("DATABASE_URL", "").strip()
    is_postgres = _is_postgres(database_url)

    if is_postgres:
        import psycopg2
        print("=" * 70)
        print(" [DATABASE] Connecting to PostgreSQL Database")
        print(f" URL: {database_url.split('@')[-1] if '@' in database_url else database_url}")
        print("=" * 70)
        conn = psycopg2.connect(database_url)
        param = "%s"
    else:
        print("=" * 70)
        print(" [DATABASE] Connecting to SQLite Database (Fallback)")
        print(f" Path: {DB_SQLITE_PATH}")
        print("=" * 70)
        os.makedirs(DB_SQLITE_PATH.parent, exist_ok=True)
        conn = sqlite3.connect(DB_SQLITE_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        param = "?"

    cur = conn.cursor()

    # Read and apply schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    print("[*] Rebuilding canonical tables from schema.sql...")
    if is_postgres:
        cur.execute(schema_sql)
    else:
        adapted = _adapt_schema_for_sqlite(schema_sql)
        cur.executescript(adapted)

    items = compile_all()
    med_count = 0
    brand_count = 0

    print("[*] Seeding medicines and brand alternatives...")
    for group in items:
        generic_base = group["generic"]
        salt_base = group["salt"]
        cat = group["cat"]
        sch = group["sch"]

        for variant in group["variants"]:
            dosage = variant[0]
            form = variant[1]
            jan_price = variant[2]
            brand_list = variant[3]

            # Form-aware generic name prevents duplicate keys for multiple dosage forms
            if form in ("Tablet", "Capsule"):
                generic_name = f"{generic_base} {dosage}".strip()
            else:
                generic_name = f"{generic_base} ({form}) {dosage}".strip()

            if is_postgres:
                cur.execute(
                    f"INSERT INTO medicines (generic_name, salt, dosage, form, jan_price, manufacturer, therapeutic_category, schedule) "
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                    f"ON CONFLICT (generic_name, dosage) DO UPDATE SET "
                    f"salt = EXCLUDED.salt, form = EXCLUDED.form, jan_price = EXCLUDED.jan_price "
                    f"RETURNING id;",
                    (generic_name, salt_base, dosage, form, jan_price, "Jan Aushadhi / National Generic", cat, sch)
                )
                med_id = cur.fetchone()[0]
            else:
                cur.execute(
                    f"INSERT INTO medicines (generic_name, salt, dosage, form, jan_price, manufacturer, therapeutic_category, schedule) "
                    f"VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                    f"ON CONFLICT(generic_name, dosage) DO UPDATE SET "
                    f"salt = excluded.salt, form = excluded.form, jan_price = excluded.jan_price;",
                    (generic_name, salt_base, dosage, form, jan_price, "Jan Aushadhi / National Generic", cat, sch)
                )
                med_id = cur.lastrowid
                if not med_id:
                    cur.execute("SELECT id FROM medicines WHERE generic_name = ? AND dosage = ?", (generic_name, dosage))
                    med_id = cur.fetchone()[0]

            med_count += 1

            for brand_name, mrp, brand_mfr in brand_list:
                if is_postgres:
                    cur.execute(
                        f"INSERT INTO brands (brand_name, generic_id, mrp, manufacturer) "
                        f"VALUES (%s, %s, %s, %s) "
                        f"ON CONFLICT (brand_name, generic_id) DO UPDATE SET mrp = EXCLUDED.mrp, manufacturer = EXCLUDED.manufacturer;",
                        (brand_name, med_id, mrp, brand_mfr)
                    )
                else:
                    cur.execute(
                        f"INSERT INTO brands (brand_name, generic_id, mrp, manufacturer) "
                        f"VALUES (?, ?, ?, ?) "
                        f"ON CONFLICT(brand_name, generic_id) DO UPDATE SET mrp = excluded.mrp, manufacturer = excluded.manufacturer;",
                        (brand_name, med_id, mrp, brand_mfr)
                    )
                brand_count += 1

    print("[*] Seeding Jan Aushadhi stores...")
    for store in STORES:
        cur.execute(
            f"INSERT INTO stores (name, address, city, pincode, lat, lng, state, phone) "
            f"VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param});",
            store
        )

    conn.commit()

    # Final DB counts verification
    cur.execute("SELECT COUNT(*) FROM medicines;")
    total_meds = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM brands;")
    total_brands = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM stores;")
    total_stores = cur.fetchone()[0]

    cur.close()
    conn.close()

    print("\n" + "=" * 70)
    print(" [✓] SEED COMPLETE SUCCESSFULLY")
    print(f"     Total Generics in DB : {total_meds}")
    print(f"     Total Brands Mapped  : {total_brands}")
    print(f"     Total Stores         : {total_stores}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    seed()
