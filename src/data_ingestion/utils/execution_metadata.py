from datetime import datetime

def add_execution_metadata(data: list[dict],
                           execution_datetime: datetime,
                           source: str = "") -> list[dict]:
    """
    Inject execution metadata into a list of records.

    Args:
        data (List[Dict]): List of scraped records — REQUIRED
        execution_datetime (datetime): Datetime the job was executed (with hour, minute, second)
        source (str): Source identifier (e.g., 'springer', 'openalex')

    Returns:
        List[Dict]: Records with two additional fields:
            - execution_datetime (str): ISO format, e.g., '2025-11-15T19:50:30+07:00'
            - ingestion_source (str): Source name
    """

    metadata = {
        'execution_datetime': execution_datetime,
        'ingestion_source': source,
    }

    return [{**record, **metadata} for record in data]
