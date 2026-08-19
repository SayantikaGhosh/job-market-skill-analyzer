import json

FILE = "data/processed/jobs_normalized.json"
TARGET_ID = "726a1832-21c3-464b-8903-7d3b3a14aa06"

with open(FILE, "r", encoding="utf-8") as file:
    jobs = json.load(file)

for job in jobs:
    if job.get("job_id") == TARGET_ID:
        print("Title:", job["title"])
        print("Description length:", len(job["description"]))
        print("\nNormalized description:")
        print(job["description"])
        break
else:
    print("Job not found.")