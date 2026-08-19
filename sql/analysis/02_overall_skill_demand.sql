-- Q2: Overall skill demand across all classified postings.

SELECT
    s.name,
    COUNT(ps.posting_id) AS posting_cnt,
    ROUND(
        (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM postings),
        2
    ) AS percentage
FROM skills s
JOIN posting_skills ps
    ON s.id = ps.skill_id
GROUP BY s.name
ORDER BY posting_cnt DESC;