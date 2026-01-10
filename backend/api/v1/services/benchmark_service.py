from typing import List
from api.v1.models import Paper
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

class BenchmarkService:
  def __init__(self, db: Session):
    self.db = db
    
  def get_random_test_set(self, percentage: float = 0.1) -> List[Paper]:
    # 1. Filter valid papers
    valid_papers = select(func.count()).select_from(Paper).where(
      Paper.venue_id.isnot(None),
      Paper.embedding.isnot(None)
    )
    
    total = self.db.execute(valid_papers).scalar()
    limit = int(total * percentage)
    
    print(f"Total papers: {total}. Fetching test set of {limit} papers...")
    
    # 2. Take random for testing
    query = (
      select(Paper)
      .where(Paper.venue_id.isnot(None), Paper.embedding.isnot(None))
      .order_by(func.random())
      .limit(limit)
    )
    return self.db.execute(query).scalars().all()
  
  def benchmark_search_hybrid(
    self, 
    vector_query: List[float], 
    keyword_query: str, 
    exclude_doi: str, # to exclude itself
    filter_top_k: int = 100, 
    rrf_k: int = 60, 
    limit: int = 10
) -> List[int]:
    """
    Search version for benchmark
    - Input: Existing vector
    - Output: List of venue_id for matching
    - Logic: Exclude the article being queried (exclude_doi)
    """
    
    # 1. Semantic CTE
    semantic_cte = (
      select(
        Paper.doi, Paper.venue_id, 
        func.row_number().over(
          order_by=Paper.embedding.cosine_distance(vector_query)
        ).label("rank_vec")
      )
      .where(Paper.doi != exclude_doi) # AVOID DATA LEAKAGE
      .order_by(Paper.embedding.cosine_distance(vector_query))
      .limit(filter_top_k)
      .cte("semantic_search")
    )

    # 2. Keyword CTE
    ts_query = func.websearch_to_tsquery('english', keyword_query)
    rank_col = func.ts_rank(Paper.tsv, ts_query)
    
    keyword_cte = (
      select(
        Paper.doi, Paper.venue_id,
        func.row_number().over(
          order_by=desc(func.ts_rank(Paper.tsv, ts_query))
        ).label("rank_ts")
      )
      .where(
        Paper.tsv.op('@@')(ts_query),
        Paper.doi != exclude_doi # AVOID DATA LEAKAGE
      )
      .order_by(desc(rank_col))
      .limit(filter_top_k)
      .cte("keyword_search")
    )

    # 3. RRF Logic
    s = semantic_cte
    k = keyword_cte
    
    score_vec = func.coalesce(1.0 / (rrf_k + s.c.rank_vec), 0.0)
    score_ts = func.coalesce(1.0 / (rrf_k + k.c.rank_ts), 0.0)
    rrf_score = (score_vec + score_ts).label("rrf_score")

    rrf_subquery = (
      select(
        func.coalesce(s.c.venue_id, k.c.venue_id).label("venue_id"),
        rrf_score
      )
      .select_from(s)
      .join(k, s.c.doi == k.c.doi, full=True)
      .subquery("rrf_ranking")
    )

    # 4. Final Query
    final_query = (
      select(rrf_subquery.c.venue_id)
      .select_from(rrf_subquery)
      .order_by(desc(rrf_subquery.c.rrf_score))
      .limit(limit)
    )

    # Return list of venue_id
    return self.db.execute(final_query).scalars().all()