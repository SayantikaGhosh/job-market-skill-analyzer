import csv
import json
from pathlib import Path


INPUT_FILE = Path("data/processed/jobs_normalized.json")

OUTPUT_DIR = Path("data/deduplicated")
OUTPUT_FILE = OUTPUT_DIR / "jobs_deduplicated.json"

REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "dedup_report.csv"


def load_jobs():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def deduplicate_jobs(jobs):
    unique_jobs = {}
    duplicate_records = []

    for job in jobs:
        job_id = job["job_id"]

        # Do not deduplicate records without a job ID.
        if not job_id:
            unique_jobs[(job["source"], id(job))] = job
            continue

        key = (job["source"], job_id)

        if key not in unique_jobs:
            unique_jobs[key] = job
            continue

        existing_job = unique_jobs[key]

        if job["snapshot_date"] > existing_job["snapshot_date"]:
            kept_job = job
            dropped_job = existing_job
        else:
            kept_job = existing_job
            dropped_job = job

        unique_jobs[key] = kept_job

        duplicate_records.append({
            "job_id": job_id,
            "source": job["source"],
            "kept_snapshot": kept_job["snapshot_date"],
            "dropped_snapshot": dropped_job["snapshot_date"],
            "kept_url": kept_job["url"],
            "dropped_url": dropped_job["url"],
        })

    return list(unique_jobs.values()), duplicate_records


def save_jobs(jobs):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            jobs,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_report(duplicates):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "job_id",
                "source",
                "kept_snapshot",
                "dropped_snapshot",
                "kept_url",
                "dropped_url",
            ],
        )

        writer.writeheader()
        writer.writerows(duplicates)


def main():
    jobs = load_jobs()

    unique_jobs, duplicates = deduplicate_jobs(jobs)

    save_jobs(unique_jobs)
    save_report(duplicates)

    print("Deduplication complete.")
    print(f"Records before: {len(jobs)}")
    print(f"Unique records: {len(unique_jobs)}")
    print(f"Duplicates removed: {len(duplicates)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()