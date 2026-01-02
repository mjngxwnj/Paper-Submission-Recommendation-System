--INDEX TABLE paper
-- Index trên cột publication_year để lọc bài báo theo năm
CREATE INDEX idx_paper_publication_year ON core.paper(publication_year);
-- Index trên cột venue_id để join với bảng venue nhanh hơn
CREATE INDEX idx_paper_venue_id ON core.paper(venue_id);
-- Index trên cột ingestion_source_id để join với bảng ingestion_source nhanh hơn
CREATE INDEX idx_paper_ingestion_source_id ON core.paper(ingestion_source_id);



--INDEX TABLE author
-- Index trên tên author để tìm kiếm theo tên nhanh hơn
CREATE INDEX idx_author_name ON core.author(name);



--INDEX TABLE paper_author
-- Index để tìm tất cả tác giả của 1 paper
CREATE INDEX idx_paper_author_paper_doi ON core.paper_author(paper_doi);
-- Index để tìm tất cả bài báo của 1 author
CREATE INDEX idx_paper_author_author_id ON core.paper_author(author_id);



--INDEX TABLE keyword
-- Index trên name để tìm kiếm từ khóa nhanh
CREATE INDEX idx_keyword_name ON core.keyword(name);



--INDEX TABLE paper_keyword
-- Index để tìm tất cả keyword của 1 paper
CREATE INDEX idx_paper_keyword_paper_doi ON core.paper_keyword(paper_doi);
-- Index để tìm tất cả paper có 1 keyword
CREATE INDEX idx_paper_keyword_keyword_id ON core.paper_keyword(keyword_id);



-- Create HNSW Index for fast Vector Search
CREATE INDEX IF NOT EXISTS idx_paper_embedding ON core.paper USING hnsw (embedding vector_cosine_ops);

-- Create GIN Index for fast Keyword Search
CREATE INDEX IF NOT EXISTS idx_paper_tsv ON core.paper USING GIN (tsv);

-- Helper RRF Function
CREATE OR REPLACE FUNCTION rrf_score(rank_1 int, rank_2 int, k int DEFAULT 60)
RETURNS numeric LANGUAGE SQL IMMUTABLE PARALLEL SAFE AS $$
  SELECT (
    COALESCE(1.0 / ($3 + NULLIF($1, 0)), 0.0) + 
    COALESCE(1.0 / ($3 + NULLIF($2, 0)), 0.0)
  );
$$;

