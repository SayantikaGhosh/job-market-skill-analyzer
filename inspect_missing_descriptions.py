import json
from pathlib import Path


RAW_DIR = Path("data/raw/lever")

TARGET_IDS = {
    "60e8a6bd-f5e7-4dd6-beef-830c1c7be821",  # Wing Assistant
    "b489fddb-b9cf-4e7b-a812-8d859739a7d9",  # Drivetrain
}


for file_path in RAW_DIR.glob("*.json"):

    with file_path.open("r", encoding="utf-8") as file:
        jobs = json.load(file)

    for job in jobs:

        if job.get("id") not in TARGET_IDS:
            continue

        print("\n" + "=" * 70)
        print(f"FILE: {file_path}")
        print(f"TITLE: {job.get('text')}")
        print(f"ID: {job.get('id')}")
        print("=" * 70)

        for field in [
            "descriptionPlain",
            "lists",
            "additionalPlain",
            "openingPlain",
            "descriptionBodyPlain",
        ]:
            value = job.get(field)

            print(f"\n--- {field} ---")

            if value:
                print(value)
            else:
                print("[EMPTY / MISSING]")