from data_ingestion.scrapers.base_scraper import BaseScraper

class SourceAScraper(BaseScraper):
    def __init__(self):
        pass

    def fetch_data(self) -> list[dict]:
        return [
            {"title": "Paper A1", "authors": ["Alice", "Bob"], "year": 2020},
            {"title": "Paper A2", "authors": ["Charlie"], "year": 2021},
        ]

