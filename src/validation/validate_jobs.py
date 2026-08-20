import json
from pathlib import Path
from urllib.parse import urlparse


INPUT_FILE = Path("../../data/deduplicated/jobs_deduplicated.json")


def load_jobs():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def is_valid_url(url):
    if not url:
        return False

    parsed = urlparse(url)

    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_jobs(jobs):
    problems = {
        "missing_job_id": [],
        "missing_title": [],
        "missing_description": [],
        "missing_company": [],
        "missing_location": [],
        "invalid_url": [],
    }

    for index, job in enumerate(jobs):
        if not job.get("job_id"):
            problems["missing_job_id"].append(index)

        if not job.get("title"):
            problems["missing_title"].append(index)

        if not job.get("description"):
            problems["missing_description"].append(index)

        if not job.get("company"):
            problems["missing_company"].append(index)

        if not job.get("location"):
            problems["missing_location"].append(index)

        if not is_valid_url(job.get("url")):
            problems["invalid_url"].append(index)

    return problems


def main():
    jobs = load_jobs()
    problems = validate_jobs(jobs)

    print("========== DATA QUALITY REPORT ==========")
    print(f"Total jobs: {len(jobs)}")

    for problem, records in problems.items():
        print(f"{problem:20} | {len(records)}")

    print("=========================================")


if __name__ == "__main__":
    main()