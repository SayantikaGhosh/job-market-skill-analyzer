import json
from datetime import date
from pathlib import Path

import requests


def fetch_greenhouse_postings(board_token):
    url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board_token}/jobs?content=true"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


def save_raw_postings(data, source, company):
    output_dir = Path("data/raw") / source
    output_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    output_file = output_dir / f"{company}_{today}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_file