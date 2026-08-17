from src.collection.companies import (
    LEVER_COMPANIES,
    GREENHOUSE_COMPANIES,
)

from src.collection.lever import (
    fetch_lever_postings,
    save_raw_postings as save_lever_raw,
)

from src.collection.greenhouse import (
    fetch_greenhouse_postings,
    save_raw_postings as save_greenhouse_raw,
)


print("========================================")
print("       PHASE 1 - DATA COLLECTION")
print("========================================")


# -------------------------
# LEVER
# -------------------------

print("\n=== LEVER ===")

for company, board_token in LEVER_COMPANIES.items():

    print(f"\nCollecting: {company}")

    try:
        jobs = fetch_lever_postings(board_token)

        output_file = save_lever_raw(
            jobs,
            source="lever",
            company=company,
        )

        print("Postings:", len(jobs))
        print("Saved to:", output_file)

    except Exception as e:
        print("ERROR:", e)


# -------------------------
# GREENHOUSE
# -------------------------

print("\n=== GREENHOUSE ===")

for company, board_token in GREENHOUSE_COMPANIES.items():

    print(f"\nCollecting: {company}")

    try:
        data = fetch_greenhouse_postings(board_token)

        jobs = data["jobs"]

        output_file = save_greenhouse_raw(
            data,
            source="greenhouse",
            company=company,
        )

        print("Postings:", len(jobs))
        print("Saved to:", output_file)

    except Exception as e:
        print("ERROR:", e)


print("\n========================================")
print("       COLLECTION COMPLETE")
print("========================================")