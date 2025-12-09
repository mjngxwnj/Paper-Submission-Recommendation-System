import re
import ast
import pandas as pd

class DataPreprocessor:
  """
  A utility class for preprocessing text and keyword fields in a DataFrame.

  This class provides methods to:
  - Clean and normalize text (title, abstract).
  - Convert string representations of lists.
  - Clean and filter keyword lists.
  - Apply all transformations to a DataFrame in one step.
  """
  def __init__(self) -> None:
    pass

  @staticmethod
  def preprocess_text(text: str) -> str:
    """
    Normalize and clean text for 'title' and 'abstract' fields.

    Args:
      text (str): Input text string.

    Returns:
      str: Cleaned and normalized text.
           Returns an empty string if input is not a string.
    """
    if not isinstance(text, str):
      return

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

  @staticmethod
  def convert_str_to_list(x) -> list[str]:
    """
    Convert a value into a standardized list of strings.

    Args:
      x (Any): Input value (string, list, NaN, or other type).

    Returns:
      list[str]: A list of cleaned string elements.
    """
    if pd.isna(x):
      return []

    if isinstance(x, list):
      return [str(i).strip() for i in x]

    if isinstance(x, str):
      try:
        parsed = ast.literal_eval(x)
        if isinstance(parsed, list):
          return [str(i).strip() for i in parsed]
      except:
        pass

      if "," in x:
        return [i.strip() for i in x.split(",") if i.strip()]

      return [x.strip()]
    return [str(x).strip()]

  @staticmethod
  def clean_keyword(keywords: list[str]) -> list[str]:
    """
    Clean and filter a list of keywords.

    Args:
      keywords (list[str]): List of keyword strings.

    Returns:
      list[str]: Cleaned list of keywords in lowercase, without duplicates or redundant acronyms.
    """
    # Remove content in bracket
    cleaned = [re.sub(r"\([^)]*\)", "", kw).strip() for kw in keywords if kw.strip()]

    # Separate full form (>=2 words)
    full_forms = [kw for kw in cleaned if len(kw.split()) > 1]

    # Create set acronym from full form (Ex: "Random Forest" -> "RF")
    derived_acronyms = set()
    for ff in full_forms:
      acronym = ''.join([w[0] for w in ff.split() if w[0].isalpha()])
      derived_acronyms.add(acronym.upper())

    def is_abbreviation(word: str) -> bool:
      if len(word) > 5:
        return False

      letters = [ch for ch in word if ch.isalpha()]
      if not letters:
        return False

      upper_ratio = sum(1 for ch in letters if ch.isupper()) / len(letters)
      return upper_ratio >= 0.6

    result = []
    for kw in cleaned:
      # If word is an abbreviation and having in corresponding full form -> remove
      if is_abbreviation(kw) and kw.upper() in derived_acronyms:
        continue
      result.append(kw.lower())

    return result

  def transform(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply preprocessing pipeline to a DataFrame.

    Args:
      df (pd.DataFrame): Input DataFrame with columns 'title', 'abstract', and 'keyword'.

    Returns:
      pd.DataFrame: A new DataFrame with cleaned and normalized values.
    """
    df = df.copy()

    if "title" in df.columns:
      df['title'] = df['title'].apply(self.preprocess_text)

    if "abstract" in df.columns:
      df['abstract'] = df['abstract'].apply(self.preprocess_text)

    if "keyword" in df.columns:
      df["keyword"] = df["keyword"].apply(self.convert_str_to_list)
      df["keyword"] = df["keyword"].apply(self.clean_keyword)

    return df