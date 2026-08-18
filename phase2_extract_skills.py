import json
import re
from pathlib import Path


CLASSIFIED_FILE = Path("reports/classified_jobs.json")
JOBS_FILE = Path("data/deduplicated/jobs_deduplicated.json")

OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "jobs_with_skills.json"

REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "skill_extraction.txt"


SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "rust",
    "php",
    "scala",

    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "elasticsearch",

    "aws",
    "azure",
    "gcp",

    "docker",
    "kubernetes",
    "terraform",

    "spark",
    "kafka",
    "airflow",
    "dbt",

    "snowflake",
    "databricks",
    "redshift",

    "react",
    "angular",
    "vue",
    "node.js",

    "fastapi",
    "django",
    "flask",
    "spring",
    "spring boot",

    "rest api",
    "graphql",
    "microservices",

    "git",
    "github",
    "gitlab",

    "jenkins",
    "github actions",

    "linux",
    "bash",

    "machine learning",
    "deep learning",
    "pytorch",
    "tensorflow",

    "pandas",
    "numpy",

    "tableau",
    "power bi",
]


def build_patterns():
    patterns = {}

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        patterns[skill] = re.compile(pattern)

    return patterns


def load_data():
    with CLASSIFIED_FILE.open("r", encoding="utf-8") as file:
        classified_jobs = json.load(file)

    with JOBS_FILE.open("r", encoding="utf-8") as file:
        jobs = json.load(file)

    job_lookup = {
        job["job_id"]: job
        for job in jobs
    }

    return classified_jobs, job_lookup


def extract_skills(text, patterns):
    matched_skills = []

    for skill, pattern in patterns.items():
        if pattern.search(text):
            matched_skills.append(skill)

    return matched_skills


def main():
    classified_jobs, job_lookup = load_data()
    patterns = build_patterns()

    jobs_with_skills = []
    skill_counts = {skill: 0 for skill in SKILLS}

    for classified_job in classified_jobs:
        job = job_lookup.get(classified_job["job_id"])

        if not job:
            continue

        title = job.get("title") or ""
        description = job.get("description") or ""

        text = (title + " " + description).lower()

        skills = extract_skills(text, patterns)

        for skill in skills:
            skill_counts[skill] += 1

        jobs_with_skills.append({
            "job_id": job["job_id"],
            "source": job["source"],
            "company": job["company"],
            "role": classified_job["role"],
            "title": title,
            "location": job["location"],
            "skills": skills,
        })

    ranked_skills = sorted(
        (
            (skill, count)
            for skill, count in skill_counts.items()
            if count > 0
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            jobs_with_skills,
            file,
            indent=2,
            ensure_ascii=False,
        )

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        file.write("========== PHASE 2 SKILL EXTRACTION ==========\n")
        file.write(
            f"Classified postings: {len(classified_jobs)}\n"
        )
        file.write(
            f"Postings with at least one skill: "
            f"{sum(1 for job in jobs_with_skills if job['skills'])}\n"
        )
        file.write(
            f"Postings with zero skills: "
            f"{sum(1 for job in jobs_with_skills if not job['skills'])}\n"
        )

        file.write("\nSkill frequency:\n")

        for skill, count in ranked_skills:
            file.write(f"{skill:20} | {count}\n")

        file.write("\nSkills by posting:\n")

        for job in jobs_with_skills:
            file.write(
                f'{job["company"]:20} | '
                f'{job["role"]:20} | '
                f'{job["title"]} | '
                f'{", ".join(job["skills"])}\n'
            )

    print("========== PHASE 2 SKILL EXTRACTION ==========")
    print(f"Classified postings: {len(classified_jobs)}")

    print(
        "Postings with at least one skill:",
        sum(1 for job in jobs_with_skills if job["skills"])
    )

    print(
        "Postings with zero skills:",
        sum(1 for job in jobs_with_skills if not job["skills"])
    )

    print("\nSkill frequency:")

    for skill, count in ranked_skills:
        print(f"{skill:20} | {count}")

    print("\nSaved to:")
    print(OUTPUT_FILE)
    print(REPORT_FILE)


if __name__ == "__main__":
    main()