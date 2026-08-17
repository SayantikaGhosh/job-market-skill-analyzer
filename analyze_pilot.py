import json
import re
from pathlib import Path


RAW_DIR = Path("data/raw")


ROLE_KEYWORDS = {
    "Data Analyst": [
        "data analyst",
        "business analyst",
        "analytics analyst",
        "reporting analyst",
    ],
    "Data Engineer": [
        "data engineer",
        "data engineering",
        "data pipeline",
        "etl",
        "data warehouse",
        "spark",
        "airflow",
        "kafka",
    ],
    "Analytics Engineer": [
        "analytics engineer",
        "analytics engineering",
        "dbt",
        "data modeling",
        "semantic layer",
    ],
    "Data Scientist": [
        "data scientist",
        "data science",
        "machine learning",
        "predictive modeling",
        "statistical modeling",
    ],
    "Backend Engineer": [
        "backend engineer",
        "backend developer",
        "back-end engineer",
        "back-end developer",
    ],
    "Software Engineer": [
        "software engineer",
        "software developer",
        "application engineer",
        "full stack",
        "fullstack",
    ],
}


def matches(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


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


def classify_role(title, description):
    title_lower = title.lower()
    description_lower = description.lower()

    # 1. Reject obvious non-target roles first.
    if any(term in title_lower for term in EXCLUDED_TITLE_TERMS):
        return None

    # 2. Strong title-based classification.
    if "analytics engineer" in title_lower:
        return "Analytics Engineer"

    if "data engineer" in title_lower or "data engineering" in title_lower:
        return "Data Engineer"

    if "data scientist" in title_lower or "data science" in title_lower:
        return "Data Scientist"

    if (
        "backend engineer" in title_lower
        or "backend developer" in title_lower
        or "back-end engineer" in title_lower
    ):
        return "Backend Engineer"

    if (
        "software engineer" in title_lower
        or "software developer" in title_lower
        or "fullstack engineer" in title_lower
        or "full stack engineer" in title_lower
    ):
        return "Software Engineer"

    if (
        "data analyst" in title_lower
        or "business analyst" in title_lower
    ):
        return "Data Analyst"

    # 3. Ambiguous titles → inspect description.
    scores = {
        "Data Engineer": 0,
        "Data Analyst": 0,
        "Analytics Engineer": 0,
        "Data Scientist": 0,
        "Backend Engineer": 0,
        "Software Engineer": 0,
    }

    data_engineer_terms = [
        "data pipeline",
        "etl",
        "data warehouse",
        "spark",
        "airflow",
        "kafka",
    ]

    data_analyst_terms = [
        "sql",
        "power bi",
        "tableau",
        "dashboard",
        "reporting",
        "data analysis",
    ]

    analytics_engineer_terms = [
        "dbt",
        "data modeling",
        "semantic layer",
    ]

    data_scientist_terms = [
        "machine learning",
        "predictive modeling",
        "statistical modeling",
        "model development",
    ]

    backend_terms = [
        "backend",
        "api development",
        "rest api",
        "microservices",
    ]

    software_terms = [
        "software development",
        "application development",
        "full stack",
    ]

    term_groups = {
        "Data Engineer": data_engineer_terms,
        "Data Analyst": data_analyst_terms,
        "Analytics Engineer": analytics_engineer_terms,
        "Data Scientist": data_scientist_terms,
        "Backend Engineer": backend_terms,
        "Software Engineer": software_terms,
    }

    for role, terms in term_groups.items():
        for term in terms:
            if term in description_lower:
                scores[role] += 1

    best_role = max(scores, key=scores.get)

    if scores[best_role] >= 3:
        return best_role

    return None

def load_jobs(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "lever" in str(file_path).lower():
        return data

    return data["jobs"]

total = 0
india = 0
classified_roles = []


for file_path in RAW_DIR.rglob("*.json"):
    if "2026-08-17" not in file_path.name:
        continue
    jobs = load_jobs(file_path)

    for job in jobs:
        total += 1

        title = job.get("text") or job.get("title") or ""

        if "lever" in str(file_path).lower():
            location = job.get("categories", {}).get("location", "")
            country = job.get("country", "")
            description = job.get("descriptionPlain", "")

        else:
            location = job.get("location", {}).get("name", "")
            country = location
            description = job.get("content", "")

        country_text = country or ""
        location_text = location or ""
        description = description or ""
        
        if "india" not in country_text.lower() and "india" not in location_text.lower():
            continue

        india += 1

        role = classify_role(title, description)

        if role:
            classified_roles.append({
                "role": role,
                "title": title,
                "location": location,
                "source": file_path.parent.name,
            })


print("Total raw postings:", total)
print("India postings:", india)
print("Classified target postings:", len(classified_roles))

print("\nRole breakdown:")

role_counts = {}

for job in classified_roles:
    role = job["role"]
    role_counts[role] = role_counts.get(role, 0) + 1

for role, count in sorted(role_counts.items()):
    print(f"{role:20} | {count}")


print("\nClassified postings:")

for job in classified_roles:
    print(
        f'{job["role"]:20} | '
        f'{job["title"]} | '
        f'{job["location"]} | '
        f'{job["source"]}'
    )