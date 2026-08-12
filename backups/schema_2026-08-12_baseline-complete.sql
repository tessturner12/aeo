-- schema.sql

CREATE TABLE IF NOT EXISTS questions (
    id          TEXT PRIMARY KEY,
    text        TEXT NOT NULL,
    topic       TEXT NOT NULL,
    tier        TEXT CHECK (tier IN ('head','mid','long')),
    is_product  BOOLEAN NOT NULL,
    cohort      TEXT CHECK (cohort IN ('test','control')),
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS runs (
    run_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id       TEXT NOT NULL REFERENCES questions(id),
    surface           TEXT NOT NULL,
    model             TEXT NOT NULL,
    run_index         INTEGER NOT NULL,
    ts                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_answer        TEXT NOT NULL,
    cited_urls        TEXT,          -- JSON array
    brand_mentioned   BOOLEAN,
    brand_position    INTEGER,       -- 1 = named first; NULL if absent
    competitors_named TEXT,          -- JSON array
    recommended         BOOLEAN,     -- true only if brand is actively recommended, not merely mentioned
    recommendation_rank INTEGER,     -- 1 = first/primary recommendation; NULL if not recommended
    parse_ok          BOOLEAN DEFAULT 1,
    error             TEXT,
    checkpoint        TEXT CHECK (checkpoint IN ('baseline','canary','after'))
);

-- Log every intervention. This is your experiment audit trail.
CREATE TABLE IF NOT EXISTS interventions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    topic       TEXT NOT NULL,
    cohort      TEXT NOT NULL,
    type        TEXT,   -- new_page | content_enhancement | citation
    description TEXT,
    url         TEXT
);

CREATE INDEX IF NOT EXISTS idx_runs_question ON runs(question_id);
CREATE INDEX IF NOT EXISTS idx_runs_ts       ON runs(ts);
CREATE INDEX IF NOT EXISTS idx_runs_surface  ON runs(surface);
