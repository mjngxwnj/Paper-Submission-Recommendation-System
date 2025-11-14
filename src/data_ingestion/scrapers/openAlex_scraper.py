from data_ingestion.scrapers.base_scraper import BaseScraper
import pyalex
from pyalex import config,Works
import time
import os
import requests
import crossref.restful
import re
class openAlexScraper(BaseScraper):
    FIELD = "Computer Science"
    FIELD_ID = "C41008148"
    DATA_NEED = ["id","title","publication_year","type","language","doi",
                "concepts","authorships","locations","primary_location","cited_by_count",
                "primary_topic","keywords"]
    MAX_RESULTS = 1000
    DELAY = 0.3
    MAX_RETRIES = 3
    
    def __init__(self):
        self.configure()
        
    def configure(self):
        pyalex.config.email = "thuattruongminh@gmail.com"
        config.max_retries = 3
        config.retry_backoff_factor = 0.1
        config.retry_http_codes = [429, 500, 503]  
    # config for crawl abstract
    def etiquette(self):
        return {
        "application_name": "PaperSubmission",
        "application_version": "1.0",
        "application_url": "https://github.com/mjngxwnj/Paper-Submission-Recommendation-System.git",
        "contact_email": "22110218@student.hcmus.edu.vn"
    }
    def get_abstract(self,doi, retries:int = 3, backoff:float = 1.0):
        abstrat_record = crossref.restful.Works(etiquette= self.etiquette())
        for attempt in range(1,retries + 1):
            try:
                data = abstrat_record.doi(doi)
                if not data:
                    return {"doi":doi,"abstract":None}
                abstract = data.get("abstract",None)
                if abstract:
                    clean_abstract = re.sub("<[^<]+?>", "", abstract)
                else:
                    clean_abstract = None
                return {"doi":doi,"abstract":clean_abstract.strip()}
            except Exception as e:
                print(f"[Attempt {attempt}/{retries}] Lỗi khi lấy {doi}: {e}")
                if attempt < retries:
                    sleep_time = backoff * 2 * attempt
                    print(f"Waitting {sleep_time} before retries")
                    time.sleep(sleep_time)
                else: 
                    return {"doi": doi,"abstract": None}      
    def fetch_data(self,api_key:str = "",checkpoint = "*") -> list[dict]:
        cursor = checkpoint
        print(f"Crawling OpenAlex for field: {self.FIELD}")

        count_result = 0
        result = []
        last_cursor = cursor
        while count_result < self.MAX_RESULTS:
            try:
                works = Works().filter(concepts = {"id":self.FIELD_ID}).select(self.DATA_NEED).get(per_page = 200,cursor = cursor)
                work_list = list(works)
                if not list(works):
                    print("No more records")
                    break
                print(f"Crawl {len(work_list)} record number")
                for record in work_list:
                    doi = record.get("doi",None)
                    if doi:
                        abstract_data = self.get_abstract(doi)
                        record["abstract"] = abstract_data.get("abstract",None)
                    else:
                        record["abstract"] = None
                    result.append(record)
                count_result += len(work_list)
                cursor = works.meta["next_cursor"]
                last_cursor = cursor
                if not cursor:
                    print("No next page to fetch ")
                    break
                time.sleep(self.DELAY)
            except (requests.exceptions.RequestException, Exception) as e:
                print(f"Error occurred: {e}")
                for i in range(1,self.MAX_RETRIES + 1):
                    print(f"Retrying {i}/{self.MAX_RETRIES} after {i*self.DELAY} seconds")
                    time.sleep(i*self.DELAY)
                    try:
                        works = Works().filter(concepts={"id": self.FIELD_ID}).select(self.DATA_NEED).get(per_page=200, cursor=cursor)
                        break
                    except Exception as e:
                        if i == self.MAX_RETRIES:
                            print("Failed to featch data")
                            return result,last_cursor
                        continue        
        print(f"Completed crawling. Total records {count_result}")
        return result,last_cursor


    

