-- Bảng paper
CREATE TABLE core.paper (
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
    created_at TIMESTAMP
);

--INDEX TABLE paper
-- Index trên cột publication_year để lọc bài báo theo năm
CREATE INDEX idx_paper_publication_year ON core.paper(publication_year);
-- Index trên cột venue_id để join với bảng venue nhanh hơn
CREATE INDEX idx_paper_venue_id ON core.paper(venue_id);
-- Index trên cột ingestion_source_id để join với bảng ingestion_source nhanh hơn
CREATE INDEX idx_paper_ingestion_source_id ON core.paper(ingestion_source_id);

-- Bảng venue
CREATE TABLE core.venue (
    id SERIAL PRIMARY KEY,
    name VARCHAR(512) NOT NULL UNIQUE
);

-- Bảng ingestion_source
CREATE TABLE core.ingestion_source (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Bảng author
CREATE TABLE core.author (
    orcid VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

--INDEX TABLE author
-- Index trên tên author để tìm kiếm theo tên nhanh hơn
CREATE INDEX idx_author_name ON core.author(name);

-- Bảng paper_author
CREATE TABLE core.paper_author (
    paper_doi VARCHAR(255) NOT NULL,
    author_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (paper_doi, author_id),
    FOREIGN KEY (paper_doi) REFERENCES core.paper(doi),
    FOREIGN KEY (author_id) REFERENCES core.author(orcid)
);

--INDEX TABLE paper_author
-- Index để tìm tất cả tác giả của 1 paper
CREATE INDEX idx_paper_author_paper_doi ON core.paper_author(paper_doi);
-- Index để tìm tất cả bài báo của 1 author
CREATE INDEX idx_paper_author_author_id ON core.paper_author(author_id);

-- Bảng keyword
CREATE TABLE core.keyword (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
);

--INDEX TABLE keyword
-- Index trên name để tìm kiếm từ khóa nhanh
CREATE INDEX idx_keyword_name ON core.keyword(name);

-- Bảng paper_keyword
CREATE TABLE core.paper_keyword (
    paper_doi VARCHAR(255) NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (paper_doi, keyword_id),
    FOREIGN KEY (paper_doi) REFERENCES core.paper(doi),
    FOREIGN KEY (keyword_id) REFERENCES core.keyword(id)
);

--INDEX TABLE paper_keyword
-- Index để tìm tất cả keyword của 1 paper
CREATE INDEX idx_paper_keyword_paper_doi ON core.paper_keyword(paper_doi);
-- Index để tìm tất cả paper có 1 keyword
CREATE INDEX idx_paper_keyword_keyword_id ON core.paper_keyword(keyword_id);

-- Bổ sung FK cho paper
ALTER TABLE core.paper
    ADD FOREIGN KEY (venue_id) REFERENCES core.venue(id);
ALTER TABLE core.paper
    ADD FOREIGN KEY (ingestion_source_id) REFERENCES core.ingestion_source(id);
