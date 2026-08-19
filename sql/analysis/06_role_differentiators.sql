-- Q6: Identify skills that are disproportionately associated
-- with a role compared with all other classified postings.

WITH role_skill_counts AS (
    SELECT
        p.role,
        s.name AS skill,
        COUNT(*) AS role_postings
    FROM postings p
    JOIN posting_skills ps
        ON p.id = ps.posting_id
    JOIN skills s
        ON ps.skill_id = s.id
    GROUP BY
        p.role,
        s.name
),

role_totals AS (
    SELECT
        role,
        COUNT(*) AS total_postings
    FROM postings
    GROUP BY role
),

skill_totals AS (
    SELECT
        s.name AS skill,
        COUNT(DISTINCT ps.posting_id) AS total_skill_postings
    FROM skills s
    JOIN posting_skills ps
        ON s.id = ps.skill_id
    GROUP BY s.name
)

SELECT
    rsc.role,
    rsc.skill,
    rsc.role_postings,

    ROUND(
        rsc.role_postings * 100.0 / rt.total_postings,
        2
    ) AS role_percentage,

    st.total_skill_postings,

    ROUND(
        rsc.role_postings * 100.0 / st.total_skill_postings,
        2
    ) AS role_share_of_skill

FROM role_skill_counts rsc
JOIN role_totals rt
    ON rsc.role = rt.role
JOIN skill_totals st
    ON rsc.skill = st.skill

ORDER BY
    role_share_of_skill DESC,
    role,
    skill;