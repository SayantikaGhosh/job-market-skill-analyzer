-- Q4: Directional skill demand for smaller role groups.
-- Data Analyst (8), Backend Engineer (8),
-- Data Scientist (4), Analytics Engineer (1).
-- Results are exploratory because of small sample sizes.

WITH skill_counts AS (

    SELECT
        p.role,
        s.name AS skill,
        COUNT(ps.posting_id) AS skill_count

    FROM postings p

    JOIN posting_skills ps
        ON p.id = ps.posting_id

    JOIN skills s
        ON ps.skill_id = s.id

    WHERE p.role IN (
        'Software Engineer',
        'Data Engineer',
        'Data Analyst',
        'Backend Engineer',
        'Data Scientist',
        'Analytics Engineer'
    )

    GROUP BY
        p.role,
        s.name
)

SELECT
    role,
    skill,
    skill_count,

    ROUND(
        (skill_count * 100.0)
        /
        (
            SELECT COUNT(*)
            FROM postings
            WHERE role = skill_counts.role
        ),
        2
    ) AS percentage,

    RANK() OVER (
        PARTITION BY role
        ORDER BY skill_count DESC
    ) AS skill_rank

FROM skill_counts

ORDER BY
    role,
    skill_rank;