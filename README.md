# QA Automation Showcase

A multi-layer API testing and data validation framework demonstrating real-world QA engineering practices. Built around the [OpenBreweryDB](https://www.openbrewerydb.org/) public REST API.

![CI Status](https://github.com/jensenmd/qa-automation-showcase/actions/workflows/qa-suite.yml/badge.svg)

Built by **Michael D. Jensen** — Senior QA Engineer with 15+ years of enterprise testing experience, currently re-entering the field with a focus on API testing, automation, and CI/CD-integrated quality practices.

🔗 [LinkedIn](https://www.linkedin.com/in/michael-jensen-751b59294/) | 📧 jensen.md@gmail.com

---

## What This Project Demonstrates

| Layer | Tool | What It Tests |
|-------|------|---------------|
| API Test Suite | Python / pytest | Status codes, response schema, business rules, query parameters, edge cases |
| Data Validation | Python / pandas | Data completeness, type integrity, uniqueness, value set constraints, volume checks |
| API Collections | Postman + JavaScript | Request chaining, schema assertions, enum validation, error handling |
| CI/CD Pipeline | GitHub Actions | Automated test execution on push, pull request, and nightly schedule |

This project was built to demonstrate current, working automation skills — not just claim them. The three layers (pytest, pandas, Postman) reflect the testing disciplines used in real enterprise QA work: validating API behavior, verifying data integrity, and ensuring coverage runs automatically without manual intervention.

---

## Project Structure

```
qa-automation-showcase/
├── tests/
│   ├── conftest.py               # Shared fixtures and session setup
│   └── test_api.py               # Full pytest API test suite
├── data/
│   └── validate_brewery_data.py  # Data validation using pandas
├── postman/
│   └── openbrewerydb_collection.json  # Importable Postman collection
├── reports/                      # Generated test output (gitignored)
├── .github/
│   └── workflows/
│       └── qa-suite.yml          # GitHub Actions CI pipeline
├── pytest.ini                    # pytest configuration
├── requirements.txt              # Python dependencies
└── README.md
```

---

## Test Coverage

### pytest API Suite (`tests/test_api.py`)

**Status Code & Response Format**
- GET /breweries returns HTTP 200
- Response Content-Type is application/json
- GET /breweries/{id} returns 200 for valid ID
- GET /breweries/{id} returns 404 for invalid ID
- Search endpoint returns 200

**Response Schema**
- Response body is a JSON array
- Every brewery object contains all required fields
- ID and name fields are non-empty strings
- Single brewery endpoint returns an object, not an array

**Business Rules**
- `brewery_type` is one of 10 valid enum values
- `country` field is never null or empty
- IDs are unique across the response
- Website URLs are properly formatted when present

**Query Parameters**
- `by_type` filter returns only matching types
- `by_state=colorado` returns only Colorado breweries
- `per_page` parameter is respected
- Pagination returns distinct records per page
- Search returns relevant results

**Edge Cases**
- Empty search query handled gracefully
- Response time under 3 seconds
- Random brewery endpoint returns a single result

### Data Validation (`data/validate_brewery_data.py`)

Fetches 200 brewery records and validates:
- Required columns are present
- Critical fields have no null values
- IDs are unique (no duplicates)
- Data types are correct
- `brewery_type` values are in the valid enum set
- Website URLs are properly formatted
- Record volume is within expected bounds
- No empty brewery names

The pandas validation layer mirrors the SQL-based data integrity work done in enterprise QA — systematically checking field presence, type correctness, value constraints, and volume against known expectations rather than just eyeballing output.

### Postman Collection (`postman/openbrewerydb_collection.json`)

7 requests demonstrating:
- **Request chaining** — extracts brewery ID from list response, passes to single-record request
- **JavaScript test scripts** — inline assertions on status, schema, and business rules
- **Collection variables** — environment-agnostic base URL configuration
- **Error scenario testing** — explicit 404 validation for invalid IDs
- **Performance assertion** — response time threshold check

---

## Why OpenBreweryDB?

- Free, public REST API — no authentication required
- Real, meaningful data with defined business rules (brewery types, locations)
- Supports filtering, searching, pagination, and random endpoints
- Stable enough for regression testing, interesting enough to write meaningful assertions
- Nightly CI run catches upstream API changes automatically — a real-world concern when your tests depend on an external service

---

## CI/CD Pipeline

GitHub Actions runs automatically on:
- Every push to `main`
- Every pull request targeting `main`
- Nightly at 6:00 AM UTC (to catch upstream API changes)

Test reports are uploaded as workflow artifacts after each run.

---

## Running Locally

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
git clone https://github.com/jensenmd/qa-automation-showcase.git
cd qa-automation-showcase
pip install -r requirements.txt
```

### Run pytest suite
```bash
pytest
```

### Run with HTML report
```bash
pytest --html=reports/pytest_report.html --self-contained-html
```

### Run data validation
```bash
python data/validate_brewery_data.py
```

### Run Postman collection
Import `postman/openbrewerydb_collection.json` into Postman and run the collection.

---

## Relationship to Other Portfolio Projects

This project is part of a three-project QA portfolio demonstrating complementary skills:

| Project | Focus | Stack |
|---|---|---|
| [pharmacy-spend-etl-qa](https://github.com/jensenmd/pharmacy-spend-etl-qa) | ETL pipeline validation, SQL-driven data integrity testing | Python / pytest / SQLite / pandas |
| **qa-automation-showcase** (this repo) | REST API testing, data validation, CI/CD integration | Python / pytest / Postman / GitHub Actions |
| [restful-booker-qa](https://github.com/jensenmd/restful-booker-qa) | Full-stack layered testing — API + UI automation | Postman / Newman / Playwright / GitHub Actions |

Together they demonstrate backend data validation, API testing, and UI automation — the core layers of a modern QA engineering practice.

---

## Author

**Michael D. Jensen** — Senior QA Engineer
15+ years of enterprise software testing experience across healthcare IT, financial systems, telecommunications, and cybersecurity. Deep background in REST API validation, ETL pipeline testing, SQL-based data integrity verification, and full-stack manual testing in Agile environments.

Currently re-entering the field with active focus on Python/pytest automation, Playwright UI testing, and CI/CD-integrated quality practices.

🔗 [LinkedIn](https://www.linkedin.com/in/michael-jensen-751b59294/) | 🐙 [GitHub Profile](https://github.com/jensenmd) | 📧 jensen.md@gmail.com
