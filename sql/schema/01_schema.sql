CREATE TABLE postings (
    id BIGSERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    source TEXT NOT NULL,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT NOT NULL,
    snapshot_date DATE,
    description TEXT,
    url TEXT,

    CONSTRAINT unique_source_job
        UNIQUE (source, job_id)
);

CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE posting_skills (
    posting_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,

    PRIMARY KEY (posting_id, skill_id),

    CONSTRAINT fk_posting
        FOREIGN KEY (posting_id)
        REFERENCES postings(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_skill
        FOREIGN KEY (skill_id)
        REFERENCES skills(id)
        ON DELETE CASCADE
);