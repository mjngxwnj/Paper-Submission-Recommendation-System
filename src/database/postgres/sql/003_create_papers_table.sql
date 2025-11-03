CREATE TABLE IF NOT EXISTS normalized.papers (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  abstract TEXT,
  authors JSONB,
  published_date DATE,
  doi TEXT UNIQUE,
  source VARCHAR(255)
);
