import json
from collections import Counter
from pathlib import Path


RAW_DIR = Path("data/raw")
COLLECTION_DATE = "2026-08-17"

total = 0
india = 0

source_counts = Counter()
company_counts = Counter()


def load_jobs(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if file_path.parent.name == "lever":
        return data

    return data["jobs"]


for file_path in RAW_DIR.rglob("*.json"):

    # Only today's final collection
    if COLLECTION_DATE not in file_path.name:
        continue

    source = file_path.parent.name
    company = file_path.stem.replace(f"_{COLLECTION_DATE}", "")

    jobs = load_jobs(file_path)

    source_counts[source] += len(jobs)
    company_counts[company] += len(jobs)

    for job in jobs:
        total += 1

        if source == "lever":
            location = job.get("categories", {}).get("location") or ""
            country = job.get("country") or ""
        else:
            location = job.get("location", {}).get("name") or ""
            country = location

        location_text = f"{location} {country}".lower()

        if "india" in location_text:
            india += 1


print("\n========== PHASE 1 STATISTICS ==========")

print(f"Collection date: {COLLECTION_DATE}")
print(f"Total postings: {total}")
print(f"India postings: {india}")

print("\n--- By Source ---")

for source, count in sorted(source_counts.items()):
    print(f"{source:15} | {count}")

print("\n--- By Company ---")

for company, count in sorted(company_counts.items()):
    print(f"{company:20} | {count}")

print("\n========================================")