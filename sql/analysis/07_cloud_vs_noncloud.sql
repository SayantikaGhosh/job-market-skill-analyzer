-- Q7: Compare skill composition of cloud-platform
-- postings versus non-cloud postings.

WITH cloud_postings AS (
    SELECT DISTINCT
        ps.posting_id
    FROM posting_skills ps
    JOIN skills s
        ON ps.skill_id = s.id
    WHERE s.name IN ('aws', 'azure', 'gcp')
),

posting_groups AS (
    SELECT
        p.id AS posting_id,
        CASE
            WHEN cp.posting_id IS NOT NULL THEN 'Cloud'
            ELSE 'Non-Cloud'
        END AS cloud_group
    FROM postings p
    LEFT JOIN cloud_postings cp
        ON p.id = cp.posting_id
),

skill_counts AS (
    SELECT
        pg.cloud_group,
        s.name AS skill,
        COUNT(DISTINCT pg.posting_id) AS posting_count
    FROM posting_groups pg
    JOIN posting_skills ps
        ON pg.posting_id = ps.posting_id
    JOIN skills s
        ON ps.skill_id = s.id
    GROUP BY
        pg.cloud_group,
        s.name
),

group_totals AS (
    SELECT
        cloud_group,
        COUNT(*) AS total_postings
    FROM posting_groups
    GROUP BY cloud_group
)

SELECT
    sc.cloud_group,
    sc.skill,
    sc.posting_count,

    ROUND(
        sc.posting_count * 100.0 / gt.total_postings,
        2
    ) AS percentage

FROM skill_counts sc
JOIN group_totals gt
    ON sc.cloud_group = gt.cloud_group

ORDER BY
    sc.cloud_group,
    sc.posting_count DESC;