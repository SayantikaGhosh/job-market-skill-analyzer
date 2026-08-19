-- Q1: What is the distribution of classified postings
-- across the six roles?
-- Also establishes the sample-size context for later analysis.

SELECT
    role,
    COUNT(*) AS posting_count,
    ROUND(
        (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM postings),
        2
    ) AS percentage
FROM postings
GROUP BY role
ORDER BY posting_count DESC;