CREATE OR REPLACE VIEW core.paper_rcm_features AS
SELECT
    p.doi AS doi,
    p.title AS title,
    p.abstract AS abstract,
    k.name AS keyword_name,
    v.name AS target_venue
FROM core.paper p
JOIN core.venue v ON v.id = p.venue_id
JOIN core.paper_keyword pk ON pk.paper_doi = p.doi
JOIN core.keyword k ON k.id = pk.keyword_id;
