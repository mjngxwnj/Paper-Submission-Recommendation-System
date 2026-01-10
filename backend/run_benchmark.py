import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / '.env.backend'
print(f"Loading env from: {env_path}")

if env_path.exists():
  load_dotenv(dotenv_path=env_path)
else:
  print("WARNING: .env.backend file not found!")
  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tqdm import tqdm
from api.v1.services.benchmark_service import BenchmarkService
from api.v1.services.db_service import get_db_session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_metrics():
  top_k_metrics = {1: 0, 3: 0, 5: 0, 7: 0, 10: 0}
  
  with get_db_session() as db:
    repo = BenchmarkService(db)
    
    # 1. Take testing data (10%)
    test_papers = repo.get_random_test_set(percentage=0.1)
    total_test = len(test_papers)
    
    if total_test == 0:
      print("No data found for benchmarking.")
      return

    print(f"Starting benchmark on {total_test} papers...")
    
    # 2. Loop through each article
    for paper in tqdm(test_papers, desc="Benchmarking"):
      true_venue_id = paper.venue_id
      
      vector_query = paper.embedding 
      if hasattr(vector_query, "tolist"):
        vector_query = vector_query.tolist()
      
      keyword_query = paper.combined_text
      
      # Call bechmark service
      recommended_venue_ids = repo.benchmark_search_hybrid(
        vector_query=vector_query,
        keyword_query=keyword_query,
        exclude_doi=paper.doi,
        limit=10
      )
      
      # 3. Calculate Hit Rate at different K levels
      for k in top_k_metrics.keys():
        top_k_recs = recommended_venue_ids[:k]
        
        if true_venue_id in top_k_recs:
          top_k_metrics[k] += 1

  # 4. Export report
  print("\n" + "="*40)
  print(f"BENCHMARK REPORT (Sample: {total_test} papers)")
  print("="*40)
  
  for k in sorted(top_k_metrics.keys()):
    hits = top_k_metrics[k]
    accuracy = (hits / total_test) * 100
    print(f"Top-{k:<2} Accuracy: {accuracy:.2f}% ({hits}/{total_test})")
  
  print("="*40)

if __name__ == "__main__":
  calculate_metrics()