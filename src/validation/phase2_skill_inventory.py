import json
import re
from pathlib import Path

CLASSIFIED_FILE = Path("../../reports/classified_jobs.json")
JOBS_FILE = Path("../../data/deduplicated/jobs_deduplicated.json")
REPORT_DIR = Path("../../reports")
REPORT_TXT = REPORT_DIR / "skill_inventory.txt"
REPORT_JSON = REPORT_DIR / "skill_inventory.json"


CANDIDATE_SKILLS = [
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


def build_patterns(skills):
    """
    Precompile one regex per skill.

    Leading boundary: \\b works fine since every skill in this list
    starts with a word character (letter).

    Trailing boundary: plain \\b breaks for skills ending in a
    non-word character (e.g. "c++", "c#") because \\b only fires at a
    word <-> non-word transition, and non-word-to-non-word is not a
    transition. We use a negative lookahead instead, which just checks
    "not immediately followed by another letter/digit" and works
    regardless of what character the skill ends with.
    """
    compiled = {}

    for skill in skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        compiled[skill] = re.compile(pattern)

    return compiled


def load_data():
    with CLASSIFIED_FILE.open("r", encoding="utf-8") as file:
        classified = json.load(file)

    with JOBS_FILE.open("r", encoding="utf-8") as file:
        jobs = json.load(file)

    job_lookup = {
        job["job_id"]: job
        for job in jobs
    }

    return classified, job_lookup


def main():
    classified, job_lookup = load_data()
    patterns = build_patterns(CANDIDATE_SKILLS)

    counts = {skill: 0 for skill in CANDIDATE_SKILLS}
    postings_with_no_skills = []

    for classified_job in classified:
        job = job_lookup.get(classified_job["job_id"])

        if not job:
            continue

        title = (job.get("title") or "").lower()
        description = (job.get("description") or "").lower()

        text = title + " " + description

        matched_any = False

        for skill, pattern in patterns.items():
            if pattern.search(text):
                counts[skill] += 1
                matched_any = True

        if not matched_any:
            postings_with_no_skills.append({
                "job_id": classified_job["job_id"],
                "title": job.get("title"),
                "company": job.get("company"),
            })

    ranked = sorted(
        ((skill, count) for skill, count in counts.items() if count > 0),
        key=lambda item: item[1],
        reverse=True,
    )

    # ---- console output ----
    print("========== PHASE 2 SKILL INVENTORY ==========")
    print(f"Classified postings: {len(classified)}")
    print(f"Postings with zero skill matches: {len(postings_with_no_skills)}")

    print("\nSkill frequency:")
    for skill, count in ranked:
        print(f"{skill:20} | {count}")

    print("==============================================")

    # ---- persisted report ----
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with REPORT_TXT.open("w", encoding="utf-8") as file:
        file.write("========== PHASE 2 SKILL INVENTORY ==========\n")
        file.write(f"Classified postings: {len(classified)}\n")
        file.write(
            f"Postings with zero skill matches: "
            f"{len(postings_with_no_skills)}\n"
        )

        file.write("\nSkill frequency:\n")
        for skill, count in ranked:
            file.write(f"{skill:20} | {count}\n")

        if postings_with_no_skills:
            file.write("\nPostings with zero skill matches (dictionary gaps):\n")
            for entry in postings_with_no_skills:
                file.write(
                    f"{entry['company']:20} | {entry['title']} | "
                    f"{entry['job_id']}\n"
                )

    with REPORT_JSON.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "classified_postings": len(classified),
                "zero_match_postings": len(postings_with_no_skills),
                "skill_counts": dict(ranked),
                "zero_match_details": postings_with_no_skills,
            },
            file,
            indent=2,
        )

    print(f"\nReport saved to: {REPORT_TXT}")
    print(f"Report saved to: {REPORT_JSON}")


if __name__ == "__main__":
    main()