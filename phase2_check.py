import json
from pathlib import Path


JOBS_FILE = Path("data/deduplicated/jobs_deduplicated.json")
CLASSIFIED_FILE = Path("reports/classified_jobs.json")


def main():
    with JOBS_FILE.open("r", encoding="utf-8") as file:
        jobs = json.load(file)

    with CLASSIFIED_FILE.open("r", encoding="utf-8") as file:
        classified = json.load(file)

    classified_ids = {
        job["job_id"]
        for job in classified
    }

    classified_jobs = [
        job
        for job in jobs
        if job.get("job_id") in classified_ids
    ]

    with_description = [
        job
        for job in classified_jobs
        if (job.get("description") or "").strip()
    ]

    missing_description = [
        job
        for job in classified_jobs
        if not (job.get("description") or "").strip()
    ]

    print("========== PHASE 2 DATA CHECK ==========")
    print(f"Classified postings:     {len(classified_jobs)}")
    print(f"With descriptions:       {len(with_description)}")
    print(f"Missing descriptions:    {len(missing_description)}")

    if missing_description:
        print("\nMissing-description postings:")

        for job in missing_description:
            print(
                f'{job["company"]:20} | '
                f'{job["title"]} | '
                f'{job["job_id"]}'
            )

    print("=========================================")


if __name__ == "__main__":
    main()