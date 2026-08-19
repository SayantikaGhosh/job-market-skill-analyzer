-- Q8: Classify skills into demand tiers.

WITH skill_demand AS (
    SELECT
        s.name AS skill,
        COUNT(ps.posting_id) AS posting_count,
        COUNT(ps.posting_id) * 100.0
            / (SELECT COUNT(*) FROM postings) AS percentage
    FROM skills s
    JOIN posting_skills ps
        ON s.id = ps.skill_id
    GROUP BY s.name
)

SELECT
    skill,
    posting_count,
    ROUND(percentage, 2) AS percentage,

    CASE
        WHEN percentage > 50 THEN 'Near-universal'
        WHEN percentage >= 20 THEN 'Common-but-optional'
        ELSE 'Niche'
    END AS demand_tier

FROM skill_demand

ORDER BY
    percentage DESC;