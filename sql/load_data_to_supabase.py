import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


INPUT_FILE = Path("../data/processed/jobs_with_skills.json")


def load_jobs():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in .env")

    jobs = load_jobs()

    connection = None

    try:
        connection = psycopg2.connect(database_url)

        with connection:
            with connection.cursor() as cursor:

                # --------------------------------------------------
                # 1. Insert postings
                # --------------------------------------------------

                posting_ids = {}

                for job in jobs:

                    cursor.execute(
                        """
                        INSERT INTO postings (
                            job_id,
                            source,
                            company,
                            title,
                            role,
                            location
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (source, job_id)
                        DO UPDATE SET
                            company = EXCLUDED.company,
                            title = EXCLUDED.title,
                            role = EXCLUDED.role,
                            location = EXCLUDED.location
                        RETURNING id;
                        """,
                        (
                            job["job_id"],
                            job["source"],
                            job["company"],
                            job["title"],
                            job["role"],
                            job["location"],
                        ),
                    )

                    posting_id = cursor.fetchone()[0]

                    posting_ids[
                        (job["source"], job["job_id"])
                    ] = posting_id

                # --------------------------------------------------
                # 2. Insert unique skills
                # --------------------------------------------------

                skill_ids = {}

                for job in jobs:

                    for skill in job.get("skills", []):

                        skill = skill.lower().strip()

                        if not skill:
                            continue

                        cursor.execute(
                            """
                            INSERT INTO skills (name)
                            VALUES (%s)
                            ON CONFLICT (name)
                            DO UPDATE SET name = EXCLUDED.name
                            RETURNING id;
                            """,
                            (skill,),
                        )

                        skill_id = cursor.fetchone()[0]

                        skill_ids[skill] = skill_id

                # --------------------------------------------------
                # 3. Insert posting ↔ skill relationships
                # --------------------------------------------------

                relationship_count = 0

                for job in jobs:

                    posting_id = posting_ids[
                        (job["source"], job["job_id"])
                    ]

                    for skill in job.get("skills", []):

                        skill = skill.lower().strip()

                        if not skill:
                            continue

                        skill_id = skill_ids[skill]

                        cursor.execute(
                            """
                            INSERT INTO posting_skills (
                                posting_id,
                                skill_id
                            )
                            VALUES (%s, %s)
                            ON CONFLICT (posting_id, skill_id)
                            DO NOTHING;
                            """,
                            (
                                posting_id,
                                skill_id,
                            ),
                        )

                        relationship_count += cursor.rowcount

        print("========================================")
        print("DATA LOAD COMPLETE")
        print("========================================")
        print(f"Classified postings processed: {len(jobs)}")
        print(f"Unique skills loaded:          {len(skill_ids)}")
        print(f"Skill relationships:           {relationship_count}")
        print("========================================")

    except psycopg2.Error as error:

        if connection:
            connection.rollback()

        print("Database load failed.")
        print(error)

    finally:

        if connection:
            connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()