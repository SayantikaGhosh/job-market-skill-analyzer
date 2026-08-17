import json
from pathlib import Path
from datetime import date
import requests


def fetch_lever_postings(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            f"Failed to fetch Lever postings for '{company}': {error}"
        ) from error

    return response.json()


def save_raw_postings(data, source, company):
    output_dir = Path("data/raw") / source
    output_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    output_file = output_dir / f"{company}_{today}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_file