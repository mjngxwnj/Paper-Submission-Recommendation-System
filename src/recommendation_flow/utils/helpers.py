from typing import List

def parse_api_keys(raw_key: str) -> List[str]:
  if not raw_key:
    return []
  
  return [k.strip() for k in raw_key.split("-") if k.strip()] 