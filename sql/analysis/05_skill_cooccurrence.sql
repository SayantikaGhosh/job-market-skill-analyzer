-- Q5: Skill co-occurrence among SQL-requiring postings,
-- with specific focus on Tableau and Power BI.

WITH sql_postings AS (
    SELECT DISTINCT
        ps.posting_id
    FROM posting_skills ps
    JOIN skills s
        ON ps.skill_id = s.id
    WHERE s.name = 'sql'
),

bi_overlap AS (
    SELECT
        sp.posting_id,
        MAX(CASE WHEN s.name = 'tableau' THEN 1 ELSE 0 END) AS has_tableau,
        MAX(CASE WHEN s.name = 'power bi' THEN 1 ELSE 0 END) AS has_power_bi
    FROM sql_postings sp
    LEFT JOIN posting_skills ps
        ON sp.posting_id = ps.posting_id
    LEFT JOIN skills s
        ON ps.skill_id = s.id
    GROUP BY sp.posting_id
)

SELECT
    COUNT(*) AS sql_postings,

    SUM(CASE
        WHEN has_tableau = 1 THEN 1
        ELSE 0
    END) AS sql_and_tableau,

    ROUND(
        SUM(CASE WHEN has_tableau = 1 THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    ) AS sql_tableau_percentage,

    SUM(CASE
        WHEN has_power_bi = 1 THEN 1
        ELSE 0
    END) AS sql_and_power_bi,

    ROUND(
        SUM(CASE WHEN has_power_bi = 1 THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    ) AS sql_power_bi_percentage,

    SUM(CASE
        WHEN has_tableau = 1 AND has_power_bi = 1 THEN 1
        ELSE 0
    END) AS sql_and_both,

    SUM(CASE
        WHEN has_tableau = 0 AND has_power_bi = 0 THEN 1
        ELSE 0
    END) AS sql_and_neither

FROM bi_overlap;