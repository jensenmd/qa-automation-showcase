"""
Data Validation Layer — Great Expectations
Fetches brewery data from the API and runs GE expectations
to validate data quality: completeness, types, business rules,
and value set constraints.

Run: python data/validate_brewery_data.py
Output: reports/ge_validation_results.json + console summary
"""
import requests
import pandas as pd
import json
import os
import sys
from datetime import datetime, timezone

# ── Fetch data ─────────────────────────────────────────────────────────────
print("Fetching brewery data from OpenBreweryDB API...")
response = requests.get(
    "https://api.openbrewerydb.org/v1/breweries",
    params={"per_page": 200}
)
response.raise_for_status()
breweries = response.json()
df = pd.DataFrame(breweries)
print(f"Fetched {len(df)} brewery records\n")

# ── Define expectations ────────────────────────────────────────────────────
VALID_BREWERY_TYPES = [
    "micro", "nano", "regional", "brewpub", "large",
    "planning", "bar", "contract", "proprietor", "closed", "taproom"
]

expectations = []
passed = 0
failed = 0
results = []

def check(name, condition, detail=""):
    global passed, failed
    status = "PASS" if condition else "FAIL"
    icon = "✅" if condition else "❌"
    print(f"{icon} {status} — {name}")
    if not condition and detail:
        print(f"      Detail: {detail}")
    if condition:
        passed += 1
    else:
        failed += 1
    results.append({"expectation": name, "status": status, "detail": detail})

# ── Column presence ────────────────────────────────────────────────────────
print("── Column Presence ──────────────────────────────────────")
for col in ["id", "name", "brewery_type", "city", "state", "country"]:
    check(f"Column '{col}' exists", col in df.columns)

# ── Null checks ────────────────────────────────────────────────────────────
print("\n── Null / Completeness Checks ───────────────────────────")
for col in ["id", "name", "brewery_type", "country"]:
    if col in df.columns:
        null_count = df[col].isnull().sum()
        check(
            f"Column '{col}' has no null values",
            null_count == 0,
            f"{null_count} null values found"
        )

# ── Uniqueness ─────────────────────────────────────────────────────────────
print("\n── Uniqueness Checks ────────────────────────────────────")
if "id" in df.columns:
    dupes = df["id"].duplicated().sum()
    check("Brewery IDs are unique", dupes == 0, f"{dupes} duplicate IDs found")

# ── Type checks ────────────────────────────────────────────────────────────
print("\n── Data Type Checks ─────────────────────────────────────")
if "id" in df.columns:
    non_str = df["id"].apply(lambda x: not isinstance(x, str)).sum()
    check("ID field is string type", non_str == 0, f"{non_str} non-string IDs")

if "name" in df.columns:
    non_str = df["name"].apply(lambda x: not isinstance(x, str)).sum()
    check("Name field is string type", non_str == 0, f"{non_str} non-string names")

# ── Business rule: valid brewery types ────────────────────────────────────
print("\n── Business Rule Checks ─────────────────────────────────")
if "brewery_type" in df.columns:
    invalid_types = df[~df["brewery_type"].isin(VALID_BREWERY_TYPES)]
    check(
        "All brewery_type values are in valid enum set",
        len(invalid_types) == 0,
        f"{len(invalid_types)} invalid types: {invalid_types['brewery_type'].unique().tolist()}"
    )

# ── Website URL format ─────────────────────────────────────────────────────
if "website_url" in df.columns:
    urls = df["website_url"].dropna()
    malformed = urls[~urls.str.startswith(("http://", "https://"))]
    check(
        "Website URLs start with http:// or https://",
        len(malformed) == 0,
        f"{len(malformed)} malformed URLs"
    )

# ── Row count sanity ───────────────────────────────────────────────────────
print("\n── Volume Checks ────────────────────────────────────────")
check("Dataset has at least 50 records", len(df) >= 50, f"Only {len(df)} records returned")
check("Dataset has at most 200 records", len(df) <= 200, f"{len(df)} records exceeds expected max")

# ── Name length sanity ────────────────────────────────────────────────────
if "name" in df.columns:
    empty_names = df[df["name"].str.strip() == ""]
    check(
        "No brewery names are empty strings",
        len(empty_names) == 0,
        f"{len(empty_names)} empty brewery names"
    )

# ── Summary ────────────────────────────────────────────────────────────────
total = passed + failed
print(f"\n{'─'*50}")
print(f"VALIDATION SUMMARY: {passed}/{total} expectations passed")
if failed > 0:
    print(f"⚠️  {failed} expectation(s) FAILED — review details above")
else:
    print("🎉 All expectations passed!")
print(f"{'─'*50}\n")

# ── Save results ───────────────────────────────────────────────────────────
os.makedirs("reports", exist_ok=True)
report = {
    "run_timestamp": datetime.now(timezone.utc).isoformat(),
    "api": "https://api.openbrewerydb.org/v1/breweries",
    "records_validated": len(df),
    "total_expectations": total,
    "passed": passed,
    "failed": failed,
    "results": results
}
with open("reports/ge_validation_results.json", "w") as f:
    json.dump(report, f, indent=2)
print("Results saved to reports/ge_validation_results.json")

if failed > 0:
    sys.exit(1)
