from data_ingestion.scrapers.base_scraper import BaseScraper

class SourceBScraper(BaseScraper):
    def __init__(self):
        pass

    def fetch_data(self) -> list[dict]:
        return [
            {"title": "Paper B1", "authors": ["David"], "year": 2019, "keywords": ["ML"]},
            {"title": "Paper B2", "authors": ["Eve", "Frank"], "year": 2022, "keywords": ["AI"]},
        ]


