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

  @staticmethod
  def combine_user_query(title: str, abstract: str, keyword) -> str:
    """
    Combine raw user input into the same embedding text format.
    Does NOT clean or modify user keywords.

    Args:
      title (str): User input title.
      abstract (str): User input abstract.
      keyword (str | list | any): User input keyword.

    Returns:
      str: Combined text for embedding inference.
    """
    if isinstance(keyword, list):
      keyword = ", ".join(map(str, keyword))
    elif keyword is None:
      keyword = ""

    combined_text = f"Title: {title} [SEP] Abstract: {abstract} [SEP] Keyword: {keyword}"
    return combined_text