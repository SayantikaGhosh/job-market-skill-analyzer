import json
from pathlib import Path


RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "jobs_normalized.json"


def load_jobs(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if file_path.parent.name == "greenhouse":
        return data.get("jobs", [])

    return data


def get_snapshot_date(file_path):
    # Example:
    # dnb_2026-08-17.json -> 2026-08-17
    return file_path.stem.split("_")[-1]

def get_company_name(file_path):
    return file_path.stem.rsplit("_", 1)[0]


def normalize_greenhouse(job, snapshot_date, company_name):
    location = job.get("location") or {}

    return {
        "job_id": str(job.get("id") or ""),
        "source": "greenhouse",
        "snapshot_date": snapshot_date,
        "company": job.get("company_name") or company_name,
        "title": job.get("title") or "",
        "location": location.get("name") or "",
        "country": "",
        "description": job.get("content") or "",
        "url": job.get("absolute_url") or "",
        "posted_at": job.get("first_published") or "",
    }


def normalize_lever(job, snapshot_date, company_name):
    categories = job.get("categories") or {}
    return {
        "job_id": str(job.get("id") or ""),
        "source": "lever",
        "snapshot_date": snapshot_date,
        "company": company_name,
        "title": job.get("text") or "",
        "location": categories.get("location") or "",
        "country": job.get("country") or "",
        "description": job.get("descriptionPlain") or "",
        "url": job.get("hostedUrl") or "",
        "posted_at": "",
    }


def normalize_job(job, source, snapshot_date, company_name):
    if source == "greenhouse":
        return normalize_greenhouse(job, snapshot_date, company_name)

    if source == "lever":
        return normalize_lever(job, snapshot_date, company_name)

    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    normalized_jobs = []

    for file_path in RAW_DIR.rglob("*.json"):
        source = file_path.parent.name

        if source not in {"greenhouse", "lever"}:
            continue

        snapshot_date = get_snapshot_date(file_path)
        company_name = get_company_name(file_path)
        jobs = load_jobs(file_path)

        for job in jobs:
            normalized_job = normalize_job(
                job,
                source,
                snapshot_date,
                company_name,
            )

            if normalized_job:
                normalized_jobs.append(normalized_job)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            normalized_jobs,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("Normalization complete.")
    print(f"Jobs normalized: {len(normalized_jobs)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()