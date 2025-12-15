from typing import Union, List

class DocumentCombiner:
  def __init__(self) -> None:
    pass

  @staticmethod
  def combine_documents(row) -> str:
    """
    Combine documents (title, abstract, and keyword list) into a single text.
    This is used for full dataset processing.

    Args:
      row: pd.Series
           A row containing 'title', 'abstract', and 'keyword'.

    Returns:
      str: Combined text for embedding.
    """
    if isinstance(row['keyword'], list):
      keyword = ", ".join(map(str, row['keyword']))
    else:
      keyword = str(row['keyword']) if row['keyword'] is not None else ""

    combined_text = f"Title: {row['title']} [SEP] Abstract: {row['abstract']} [SEP] Keyword: {keyword}"
    return combined_text
  
  # ----------------------------------------------------------------------------
  @staticmethod
  def combine_user_query(
    title: str, 
    abstract: str, 
    keyword: Union[str, List[str], None],
    task: str = "VECTOR_SEARCH"
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
      title (str): The user-provided title query.
      abstract (str): The user-provided abstract query.
      keyword (Union[str, List[str], None]): The user-provided keywords. 
          Can be a comma-separated string, a list of strings, or None.
      task (str, optional): The target task type. 
          Must be one of ["VECTOR_SEARCH", "KEYWORD_SEARCH"]. Defaults to "VECTOR_SEARCH".

    Returns:
      str: A formatted string ready for the specific downstream processing.
    """
    # Normalize Keyword Input
    if isinstance(keyword, list):
      keyword = ", ".join(map(str, keyword))
    elif keyword is None:
      keyword = ""
    else:
      keyword = str(keyword).strip()
    
    # Handle Task-Specific Formatting
    if task == "VECTOR_SEARCH":
      return f"Title: {title} [SEP] Abstract: {abstract} [SEP] Keyword: {keyword}"
    
    elif task == "KEYWORD_SEARCH":
      parts = [title, abstract, keyword]
      return " ".join(filter(None, parts))
    
    else:
      raise ValueError(f"Invalid task type: '{task}'. Expected 'VECTOR_SEARCH' or 'KEYWORD_SEARCH'.")