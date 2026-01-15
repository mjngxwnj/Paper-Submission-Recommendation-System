import logging
import pandas as pd
from tqdm import tqdm
from api.v1.services.db_service import get_db_session
from api.v1.services.benchmark_service import BenchmarkService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_hybrid_search_benchmark(limit_candidates: int = 10):
  """
  Run benchmarking evaluate Hit Rate @ K (Strict Match)
  for Hybrid Search (Semantic + Keyword + RRF)
  """
  
  df = pd.read_csv("benchmark_test_ids.csv")
  test_ids = df["doi"].tolist()

  # 1. Initialize metric counters
  k_metrics = [1, 3, 5, 10]
  hits = {k: 0 for k in k_metrics}

  with get_db_session() as db:
    repo = BenchmarkService(db)

    # 2. Load fixed test set (deterministic)
    test_papers = repo.get_test_set_by_doi(test_ids)
    total_samples = len(test_papers)

    if total_samples == 0:
      print("No test papers found.")
      return {}

    print(f"Starting Hybrid Search Benchmark on {total_samples} papers...")

    # 3. Loop through each test paper
    for paper in tqdm(test_papers, desc="Benchmarking"):

      true_doi = paper.doi
      true_venue_id = paper.venue_id

      # Safety check
      if true_venue_id is None or paper.embedding is None:
        total_samples -= 1
        continue

      # Prepare query inputs
      vector_query = paper.embedding
      if hasattr(vector_query, "tolist"):
        vector_query = vector_query.tolist()

      keyword_query = paper.combined_text or paper.title

      try:
        recommended_venue_ids = repo.benchmark_search_hybrid(
          vector_query=vector_query,
          keyword_query=keyword_query,
          exclude_doi=true_doi,
          limit=limit_candidates
        )
      except Exception:
        total_samples -= 1
        continue

      # 4. Hit@K evaluation (Strict Match)
      for k in k_metrics:
        top_k_venues = recommended_venue_ids[:k]
        if true_venue_id in top_k_venues:
          hits[k] += 1

  # 5. Export report (FORMAT GIỐNG CBF)
  print("\n" + "=" * 50)
  print("HYBRID SEARCH PERFORMANCE REPORT")
  print(f"Tested Samples: {total_samples}")
  print("=" * 50)

  results = {}
  for k in k_metrics:
    acc = (hits[k] / total_samples) * 100 if total_samples > 0 else 0
    results[f"Hit@{k}"] = acc
    print(f"Hit Rate @ {k:<2}: {acc:.2f}%  ({hits[k]}/{total_samples})")

  print("=" * 50)

if __name__ == "__main__":
  run_hybrid_search_benchmark()
  