import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv



ANALYSIS_DIR = Path("../analysis")
OUTPUT_DIR = Path("../../powerbi/exports")


EXPORTS = {
    "01_sample_scope.sql": "role_distribution.csv",
    "02_overall_skill_demand.sql": "overall_skill_demand.csv",
    "03_role_comparison.sql": "role_skill_comparison.csv",
    "04_small_sample_roles.sql": "small_sample_role_skills.csv",
    "05_skill_cooccurrence.sql": "sql_bi_cooccurrence.csv",
    "06_role_differentiators.sql": "role_differentiators.csv",
    "07_cloud_vs_noncloud.sql": "cloud_vs_noncloud.csv",
    "08_skill_demand_tiers.sql": "skill_demand_tiers.csv",
}


def main():
    env_path = Path("../../.env")
    load_dotenv(env_path)

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in .env")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = None

    try:
        connection = psycopg2.connect(database_url)

        with connection.cursor() as cursor:

            for sql_file, csv_file in EXPORTS.items():

                sql_path = ANALYSIS_DIR / sql_file
                output_path = OUTPUT_DIR / csv_file

                print(f"Running: {sql_file}")

                with sql_path.open("r", encoding="utf-8") as file:
                    query = file.read()

                cursor.execute(query)

                rows = cursor.fetchall()
                columns = [
                    description[0]
                    for description in cursor.description
                ]

                with output_path.open(
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as file:

                    writer = csv.writer(file)

                    writer.writerow(columns)
                    writer.writerows(rows)

                print(
                    f"Exported {len(rows)} rows "
                    f"to {output_path}"
                )

        print("\n========================================")
        print("POWER BI EXPORT COMPLETE")
        print("========================================")

    except psycopg2.Error as error:
        print("Database export failed.")
        print(error)

    finally:
        if connection:
            connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()