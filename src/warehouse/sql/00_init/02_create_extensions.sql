-- 1. Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Update new fields for table core.paper
CREATE TABLE IF NOT EXISTS core.paper (
  doi VARCHAR(255) PRIMARY KEY,
  title TEXT,
  abstract TEXT,
  abstract_link TEXT,
  open_access BOOLEAN,
  publication_day INT,
  publication_month INT,
  publication_year INT,
  venue_id INT,
  ingestion_source_id INT,
);

-- 3. Indexes
-- Create HNSW Index for fast Vector Search
CREATE INDEX IF NOT EXISTS idx_paper_embedding ON core.paper USING hnsw (embedding vector_cosine_ops);

-- Create GIN Index for fast Keyword Search
CREATE INDEX IF NOT EXISTS idx_paper_tsv ON core.paper USING GIN (tsv);

-- 4. Helper RRF Function
CREATE OR REPLACE FUNCTION rrf_score(rank_1 int, rank_2 int, k int DEFAULT 60)
RETURNS numeric LANGUAGE SQL IMMUTABLE PARALLEL SAFE AS $$
  SELECT (
    COALESCE(1.0 / ($3 + NULLIF($1, 0)), 0.0) + 
    COALESCE(1.0 / ($3 + NULLIF($2, 0)), 0.0)
  );
$$;
