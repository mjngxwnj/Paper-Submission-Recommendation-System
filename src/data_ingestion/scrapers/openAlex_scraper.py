from data_ingestion.scrapers.base_scraper import BaseScraper
import pyalex
from pyalex import config,Works
import time
import os
import requests
class openAlexScraper(BaseScraper):
    CHECKPOINT_FILE = "checkpoint.txt"
    FIELD = "Computer Science"
    FIELD_ID = "C41008148"
    DATA_NEED = ["id","title","publication_year","type","language","doi",
                "concepts","authorships","locations","primary_location","cited_by_count",
                "primary_topic","keywords"]
    MAX_RESULTS = 500
    DELAY = 1
    MAX_RETRIES = 3
    
    def __init__(self):
        self.configure()
        
    def configure(self):
        pyalex.config.email = "thuattruongminh@gmail.com"
        config.max_retries = 3
        config.retry_backoff_factor = 0.1
        config.retry_http_codes = [429, 500, 503]
        
    def load_checkpoint(self):
        if os.path.exists(self.CHECKPOINT_FILE):
            with open(self.CHECKPOINT_FILE) as f:
                return f.read().strip() or "*"
        return "*"
    
    def save_checkpoint(self,cursor):
        with open(self.CHECKPOINT_FILE, "w") as f:
            f.write(cursor)
            
    def fetch_data(self) -> list[dict]:
        cursor = self.load_checkpoint()
        print(f"Crawling OpenAlex for field: {self.FIELD}")

        count_result = 0
        result = []
        while count_result < self.MAX_RESULTS:
            try:
                works = Works().filter(concepts = {"id":self.FIELD_ID}).select(self.DATA_NEED).get(per_page = 100,cursor = cursor)
                if not list(works):
                    print("No more records")
                    break
                for record in works:
                    print(f"Crawl record number: {count_result}")
                    result.append(record)
                    count_result += 1
                    if (count_result >= self.MAX_RESULTS):
                        break
                cursor = works.meta["next_cursor"]
                if not cursor:
                    print("No next page to fetch ")
                    break
                self.save_checkpoint(works.meta["next_cursor"])
                time.sleep(self.DELAY)
            except (requests.exceptions.RequestException, Exception) as e:
                print(f"Error occurred: {e}")
                for i in range(1,self.MAX_RETRIES + 1):
                    print(f"Retrying {i}/{self.MAX_RETRIES} after {i*self.DELAY} seconds")
                    time.sleep(i*self.DELAY)
                    try:
                        works = Works().filter(concepts={"id": self.FIELD_ID}).select(self.DATA_NEED).get(per_page=50, cursor=cursor)
                        break
                    except Exception as e:
                        if i == self.MAX_RETRIES:
                            print("Failed to featch data")
                            return
                        continue        
        print(f"Completed crawling. Total records {count_result}")
        return result


    

