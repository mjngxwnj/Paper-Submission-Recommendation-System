-- Bảng core.paper
CREATE TABLE core.paper (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    abstract_link TEXT,
    execution_datetime TIMESTAMP,
    open_access BOOLEAN,
    publication_day INT,
    publication_month INT,
    publication_year INT,
    venue_id INT,
    ingestion_source_id INT,
    created_at TIMESTAMP
);

-- Index bổ sung
CREATE INDEX idx_paper_publication_year ON core.paper(publication_year);
CREATE INDEX idx_paper_venue_id ON core.paper(venue_id);
CREATE INDEX idx_paper_ingestion_source_id ON core.paper(ingestion_source_id);

-- Bảng venue
CREATE TABLE core.venue (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
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

CREATE INDEX idx_author_name ON core.author(name);

-- Bảng paper_author
CREATE TABLE core.paper_author (
    paper_id VARCHAR(255) NOT NULL,
    author_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (paper_id, author_id),
    FOREIGN KEY (paper_id) REFERENCES core.paper(id),
    FOREIGN KEY (author_id) REFERENCES core.author(orcid)
);

CREATE INDEX idx_paper_author_paper_id ON core.paper_author(paper_id);
CREATE INDEX idx_paper_author_author_id ON core.paper_author(author_id);

-- Bảng keyword
CREATE TABLE core.keyword (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE INDEX idx_keyword_name ON core.keyword(name);

-- Bảng paper_keyword
CREATE TABLE core.paper_keyword (
    paper_id VARCHAR(255) NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (paper_id, keyword_id),
    FOREIGN KEY (paper_id) REFERENCES core.paper(id),
    FOREIGN KEY (keyword_id) REFERENCES core.keyword(id)
);

CREATE INDEX idx_paper_keyword_paper_id ON core.paper_keyword(paper_id);
CREATE INDEX idx_paper_keyword_keyword_id ON core.paper_keyword(keyword_id);

-- Bổ sung FK cho paper
ALTER TABLE core.paper
    ADD FOREIGN KEY (venue_id) REFERENCES core.venue(id);
ALTER TABLE core.paper
    ADD FOREIGN KEY (ingestion_source_id) REFERENCES core.ingestion_source(id);
