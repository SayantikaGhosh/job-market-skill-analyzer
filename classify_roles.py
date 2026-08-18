import json
from pathlib import Path


INPUT_FILE = Path("data/deduplicated/jobs_deduplicated.json")
REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "role_classification.txt"
CLASSIFIED_FILE = REPORT_DIR / "classified_jobs.json"

ROLES = [
    "Data Analyst",
    "Data Engineer",
    "Analytics Engineer",
    "Data Scientist",
    "Backend Engineer",
    "Software Engineer",
]


EXCLUDED_TITLE_TERMS = [
    "manager",
    "director",
    "vp",
    "vice president",
    "recruiter",
    "intern",
    "trainee",
    "qa",
    "quality assurance",
    "security",
    "devops",
    "sre",
    "support",
    "sales",
    "marketing",
]


def load_jobs():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def classify_role(title, description):
    title_lower = title.lower()
    description_lower = description.lower()

    # Reject obvious non-target roles.
    if any(term in title_lower for term in EXCLUDED_TITLE_TERMS):
        return None

    # Known QA / automation edge case.
    if (
        "sde" in title_lower
        and (
            "automation" in title_lower
            or "quality" in title_lower
        )
    ):
        return None

    # Strong title-based classification.
    if "analytics engineer" in title_lower:
        return "Analytics Engineer"

    if (
        "data engineer" in title_lower
        or "data engineering" in title_lower
    ):
        return "Data Engineer"

    if (
        "data scientist" in title_lower
        or "data science" in title_lower
    ):
        return "Data Scientist"

    if (
        "backend engineer" in title_lower
        or "backend developer" in title_lower
        or "back-end engineer" in title_lower
        or "back-end developer" in title_lower
    ):
        return "Backend Engineer"

    if (
        "software engineer" in title_lower
        or "software developer" in title_lower
        or "application engineer" in title_lower
        or "fullstack engineer" in title_lower
        or "full stack engineer" in title_lower
    ):
        return "Software Engineer"

    # Do NOT classify every Business Analyst as Data Analyst.
    if "data analyst" in title_lower:
        return "Data Analyst"

    # Ambiguous titles: inspect description.
    scores = {
        "Data Engineer": 0,
        "Data Analyst": 0,
        "Analytics Engineer": 0,
        "Data Scientist": 0,
        "Backend Engineer": 0,
        "Software Engineer": 0,
    }

    term_groups = {
        "Data Engineer": [
            "data pipeline",
            "etl",
            "data warehouse",
            "spark",
            "airflow",
            "kafka",
        ],
        "Data Analyst": [
            "sql",
            "power bi",
            "tableau",
            "dashboard",
            "reporting",
            "data analysis",
        ],
        "Analytics Engineer": [
            "dbt",
            "data modeling",
            "semantic layer",
        ],
        "Data Scientist": [
            "machine learning",
            "predictive modeling",
            "statistical modeling",
            "model development",
        ],
        "Backend Engineer": [
            "backend",
            "api development",
            "rest api",
            "microservices",
        ],
        "Software Engineer": [
            "software development",
            "application development",
            "full stack",
        ],
    }

    for role, terms in term_groups.items():
        for term in terms:
            if term in description_lower:
                scores[role] += 1

    best_role = max(scores, key=scores.get)

    if scores[best_role] >= 3:
        return best_role

    return None


def is_india_job(job):
    country = (job.get("country") or "").lower()
    location = (job.get("location") or "").lower()

    return "india" in country or "india" in location


def main():
    jobs = load_jobs()

    total_jobs = len(jobs)
    india_jobs = []
    classified_jobs = []

    for job in jobs:
        if not is_india_job(job):
            continue

        india_jobs.append(job)

        role = classify_role(
            job.get("title") or "",
            job.get("description") or "",
        )

        if role:
            classified_jobs.append({
                "role": role,
                "job_id": job["job_id"],
                "source": job["source"],
                "company": job["company"],
                "title": job["title"],
                "location": job["location"],
            })

    role_counts = {}

    for job in classified_jobs:
        role = job["role"]
        role_counts[role] = role_counts.get(role, 0) + 1

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with CLASSIFIED_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            classified_jobs,
            file,
            indent=2,
            ensure_ascii=False,
        )

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        file.write("========== ROLE CLASSIFICATION ==========\n")
        file.write(f"Total unique jobs: {total_jobs}\n")
        file.write(f"India jobs: {len(india_jobs)}\n")
        file.write(f"Classified target jobs: {len(classified_jobs)}\n")
        file.write(
            f"Unclassified India jobs: "
            f"{len(india_jobs) - len(classified_jobs)}\n"
        )

        file.write("\nRole breakdown:\n")

        for role in ROLES:
            file.write(
                f"{role:20} | "
                f"{role_counts.get(role, 0)}\n"
            )

        file.write("\nClassified postings:\n")

        for job in classified_jobs:
            file.write(
                f"{job['role']:20} | "
                f"{job['company']} | "
                f"{job['title']} | "
                f"{job['location']} | "
                f"{job['source']}\n"
            )

    print("========== ROLE CLASSIFICATION ==========")
    print(f"Total unique jobs: {total_jobs}")
    print(f"India jobs: {len(india_jobs)}")
    print(f"Classified target jobs: {len(classified_jobs)}")

    print("\nRole breakdown:")

    for role in ROLES:
        print(
            f"{role:20} | "
            f"{role_counts.get(role, 0)}"
        )

    print("\nReport saved to:")
    print(REPORT_FILE)


if __name__ == "__main__":
    main()