import re
from typing import Optional, Dict, List, Union
from google.api_core import exceptions as gexc

# ============================ USER INPUT PROCESSOR ============================
class UserInputProcessor:
  def __init__(self):
    pass
  
  # ----------------------------------------------------------------------------
  def preprocess_text(self, text: str) -> str:
    """
    Normalize and clean text for 'title' and 'abstract' fields.

    Args:
      text (str): Input text string.

    Returns:
      str: Cleaned and normalized text.
           Returns an empty string if input is not a string.
    """
    if not isinstance(text, str):
      return ""
    
    text = text.lower()
    
    # Remove complex math formulas/LaTeX sections
    text = re.sub(r"\$\$.*?\$\$", "", text)
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"\\\(.*?\\\)", "", text)
    text = re.sub(r"\\\[.*?\\\]", "", text)
    text = re.sub(r"\\begin.*?\\end", "", text)

    # Remove other brackets
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"{.*?}", "", text)

    # Other removals
    text = re.sub(r"http[^ ]*", "", text)
    text = re.sub(r"[^0-9a-zA-ZÀ-ỹ\s]", "", text)
    text = re.sub(r'\s+', " ", text)

    return text.strip()
  
  # ----------------------------------------------------------------------------
  def normalize_keywords(self, keyword: Union[str, List[str], None]) -> str:
    """
    Convert keywords input (string, list, or None) into a single normalized string.
    
    Args:
      keyword: Can be:
        - None
        - String (comma-separated or space-separated)
        - List of strings
    
    Returns:
      str: Space-separated lowercase keywords
    
    Examples:
      normalize_keywords(['Deep Learning', 'NLP']) -> 'deep learning nlp'
      normalize_keywords('Deep Learning, NLP') -> 'deep learning nlp'
      normalize_keywords(None) -> ''
    """
    if not keyword:
      return ""
    
    # If it's a list, join with spaces
    if isinstance(keyword, list):
      keyword = " ".join(keyword)
    
    # If it's a string, clean it
    if isinstance(keyword, str):
      # Remove common separators and normalize
      keyword = re.sub(r'[,;|]+', ' ', keyword)
      keyword = re.sub(r'\s+', ' ', keyword)
      return keyword.lower().strip()
    
    return ""
  
  # ----------------------------------------------------------------------------
  def process_user_input(
    self, 
    title: Optional[str] = None, 
    abstract: Optional[str] = None, 
    keyword: Union[str, List[str], None] = None
  ) -> Dict[str, str]:
    """
    Preprocess user input fields.
    
    Args:
      title: Paper title
      abstract: Paper abstract
      keyword: None/ String (comma-separated or space-separated)/ List of strings

    Returns:
      dict with keys: title, abstract, keyword
    """
    processed_title = self.preprocess_text(title)
    processed_abstract = self.preprocess_text(abstract)
    processed_keyword = self.normalize_keywords(keyword)
    
    return {
      "title": processed_title,
      "abstract": processed_abstract,
      "keyword": processed_keyword
    }
    
  # ----------------------------------------------------------------------------  
  def combine_user_query(
    self,
    title: Optional[str] = None, 
    abstract: Optional[str] = None, 
    keyword: Optional[str] = None,
    task_type: str = "VECTOR_SEARCH"
  ) -> str:
    """
    Combines raw user input fields into a single formatted string based on the specified task.

    This method handles data type normalization for keywords and applies specific 
    formatting rules:
    - VECTOR_SEARCH: Adds special separators (e.g., [SEP], prefixes) to preserve semantic structure 
      for embedding models.
    - KEYWORD_SEARCH: Concatenates fields with simple whitespace for lexical search engines 
      (e.g., PostgreSQL tsvector).

    Args:
      title (Optional[str]): The user-provided title query.
      abstract (Optional[str]): The user-provided abstract query.
      keyword (Optional[str]): The user-provided keywords. 
          Can be a comma-separated string, a list of strings, or None.
      task_type (str, optional): The target task type. 
          Must be one of ["VECTOR_SEARCH", "KEYWORD_SEARCH"]. Defaults to "VECTOR_SEARCH".

    Return:
      str: A formatted string ready for the specific downstream processing.
    """
    keyword = keyword if keyword else ""
      
    if task_type == "VECTOR_SEARCH":
      return f"Title: {title} [SEP] Abstract: {abstract} [SEP] Keyword: {keyword}"
    
    elif task_type == "KEYWORD_SEARCH":
      parts = [title, abstract, keyword]
      return " ".join(filter(None, parts))
    
    else: 
      raise ValueError(f"Invalid task type: '{task_type}'. Expected 'VECTOR_SEARCH' or 'KEYWORD_SEARCH'.")

# ============================ STATUS CODE CHECKER =============================
class GoogleAPIChecker:
  @staticmethod
  def extract_staus_code(error: Exception) -> Optional[int]:
    """
    Extract HTTP-like status code from Google API exception.
    Link HTTP status codes: https://docs.cloud.google.com/web-risk/docs/status-codes
    """
    
    if isinstance(error, gexc.ResourceExhausted):
      return 429
    if isinstance(error, gexc.PermissionDenied):
      return 403
    if isinstance(error, gexc.Unauthorized):
      return 401
    if isinstance(error, gexc.InvalidArgument):
      return 400
    if isinstance(error, gexc.NotFound):
      return 404
    if isinstance(error, gexc.InternalServerError):
      return 500
    if isinstance(error, gexc.ServiceUnavailable):
      return 503
    if isinstance(error, gexc.DeadlineExceeded):
      return 504

    return None
  
  @staticmethod
  def should_rotate_key(status_code: int) -> bool:
    """
    Only rotate key if the error relates to key exhaustion or quota exhaustion.
    """
    return status_code in {403, 429}