# MedSave Data Engine

## Overview

The MedSave Data Engine is a dedicated subsystem responsible for the complete
lifecycle of medicine data from acquisition through to database loading.

It operates independently of the Flask API and frontend.
The Flask API remains completely unaware of the Data Engine.

---

## Architecture

\\\
                 Flask API
                      |
                      v
               PostgreSQL Database
                      ^
                      |
               PostgreSQL Loader
                      ^
                      |
               Validation Layer
                      ^
                      |
             Normalization Layer
                      ^
                      |
                  Parser Layer
                      ^
                      |
                Source Adapters
\\\

Data flows strictly upward through the pipeline.
No layer communicates directly with a layer above it.

---

## Folder Responsibilities

\\\
pipeline/

entities/           Internal data models used throughout the pipeline.
                    Decoupled from the database schema.
                    Medicine and Brand are defined here.

sources/            Data source adapters.
                    Each adapter wraps a single external data source.
                    All adapters inherit from BaseSource.

parsers/            Raw data interpreters.
                    Convert raw source output into pipeline entities.
                    Not yet implemented.

normalizers/        Data normalization logic.
                    Standardize casing, units, naming conventions.
                    Not yet implemented.

validators/         Data validation logic.
                    Enforce business rules before loading.
                    Not yet implemented.

loaders/            Database writers.
                    The only layer permitted to interact with the database.
                    PostgresLoader is defined here.

raw/                Storage for raw downloaded files.
                    Files here are never modified.

processed/          Storage for files after parsing and normalization.

config.py           Loads environment variables.
                    Exposes database URL, raw directory, processed directory.

data_engine.py      Entry point for the Data Engine.
                    Initializes configuration, logging, and pipeline.
\\\

---

## Execution Flow

When the Data Engine is fully implemented the execution flow will be:

\\\
1. Load configuration from environment variables.

2. Source Adapter fetches raw data from external source.
       KaggleSource     -> downloads CSV to pipeline/raw/
       JanAushadhiSource -> scrapes listings to pipeline/raw/

3. Parser interprets raw data into Medicine and Brand entities.

4. Normalizer standardizes entity fields.
       generic_name -> title case
       dosage       -> standardized units
       form         -> controlled vocabulary

5. Validator enforces business rules.
       jan_price must be greater than zero.
       generic_name must not be empty.
       mrp must be greater than jan_price.

6. Loader inserts validated entities into PostgreSQL.
       load_medicines() -> inserts into medicines table.
       load_brands()    -> resolves medicine IDs, inserts into brands table.
\\\

---

## Running the Data Engine

\\\ash
python pipeline/data_engine.py
\\\

Expected output:

\\\
=====================================

  MedSave Data Engine
  Version 0.1

  Pipeline initialized successfully.

=====================================
\\\

---

## Environment Variables

| Variable       | Description                        | Default                      |
|----------------|------------------------------------|------------------------------|
| DATABASE_URL   | PostgreSQL connection string       | sqlite:///backend/medsave.db |
| RAW_DIR        | Directory for raw downloaded files | pipeline/raw                 |
| PROCESSED_DIR  | Directory for processed files      | pipeline/processed           |

---

## Extending the Data Engine

### Adding a New Data Source

1. Create a new file in pipeline/sources/.

\\\
pipeline/sources/jan_aushadhi.py
\\\

2. Inherit from BaseSource.

\\\python
from pipeline.sources.base import BaseSource

class JanAushadhiSource(BaseSource):

    def get_source_name(self) -> str:
        return "jan_aushadhi"

    def fetch(self):
        # implement download or scraping logic
        ...

    def get_metadata(self) -> dict:
        # return source metadata
        ...
\\\

3. Export from pipeline/sources/__init__.py.

\\\python
from pipeline.sources.jan_aushadhi import JanAushadhiSource
\\\

The pipeline orchestrator will pick it up automatically.

---

### Adding a New Loader

1. Create a new file in pipeline/loaders/.

\\\
pipeline/loaders/sqlite_loader.py
\\\

2. Implement load_medicines() and load_brands() methods
   following the same interface as PostgresLoader.

3. Export from pipeline/loaders/__init__.py.

---

## Future Roadmap

| Sprint | Objective                                      |
|--------|------------------------------------------------|
| 2.1    | Data Engine architecture and abstractions      |
| 2.2    | Kaggle source implementation and CSV parser    |
| 2.3    | Normalization and validation layers            |
| 2.4    | PostgreSQL loader implementation               |
| 2.5    | Jan Aushadhi source adapter                   |
| 2.6    | Full pipeline integration and scheduling       |

---

## Design Principles

- Entities are decoupled from the database schema.
- Database IDs belong to the loader, not the entity.
- No layer communicates directly with a layer above it.
- The Flask API is completely unaware of the Data Engine.
- All source adapters inherit from BaseSource.
- Business logic never lives in config.py.
