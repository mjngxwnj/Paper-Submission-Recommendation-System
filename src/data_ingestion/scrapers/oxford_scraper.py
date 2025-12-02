from data_ingestion.scrapers.base_scraper import BaseScraper
import requests
import xml.etree.ElementTree as ET
import json
import time
import os
class oxfordScraper(BaseScraper):
    MAX_RETRIES = 3     # Số lần thử lại khi lỗi mạng
    DELAY = 20           # Giãn cách giữa các lần gọi (giây)
    TIMEOUT = 120  
    BASE_URL = "https://ora.ox.ac.uk/oai2" # endpoint OAI-PMH của ORA
    METADATA_PREFIX = "oai_dc" # Định dạng metadata được quy định của trang
    KEYWORDS_CS = [
    "computer science", "computing", "information technology", "informatics", "software engineering",
    "artificial intelligence", "machine learning", "deep learning", "neural network", "nlp", "computer vision",
    "data science", "data mining", "big data", "data analytics", "data visualization",
    "cloud computing", "distributed systems", "network security", "internet of things", "cybersecurity",
    "algorithm", "optimization", "graph theory", "cryptography", "quantum computing",
    "programming", "software development", "compiler", "debugging",
    "web development", "mobile application", "frontend", "backend", "human computer interaction",
    "robotics", "virtual reality", "computer graphics", "image processing",
]

    def __init__(self):
        pass
    def fetch_record(self,resumption_token = None):
        if resumption_token:
            params = {"verb": "ListRecords", "resumptionToken": resumption_token}
        else:
            params = {"verb": "ListRecords", "metadataPrefix": self.METADATA_PREFIX}
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = requests.get(self.BASE_URL, params=params, timeout=self.TIMEOUT)
                response.raise_for_status() # Ném lỗi HTTP nếu status khác 200
                return response.text # Kết quả trả về
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e: # Ném lỗi nếu bị Timeout hoặc lỗi kết nối
                print(f"Attempt {attempt}/{self.MAX_RETRIES} failed: {e}")
                if attempt < self.MAX_RETRIES:
                    print(f"Waiting {self.TIMEOUT}s before retry...")
                    time.sleep(self.TIMEOUT)
                else:
                    raise Exception("Failed to fetch after multiple retries")
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise
    def parse_xml(self,xml_data):
        '''
        "oai" là viết tắt cho namespace của OAI-PMH (các thẻ như <record>, <ListRecords>, <resumptionToken> nằm trong đó).
        "dc" là viết tắt cho namespace của Dublin Core (các thẻ metadata như <dc:title>, <dc:creator>…).
        '''
        ns = {
            "oai": "http://www.openarchives.org/OAI/2.0/", 
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        root = ET.fromstring(xml_data)
        records = []
        for record in root.findall(".//oai:record",ns):
            data = {}
            for field in ["title","creator","subject","description","publisher","contributor","date","type","format",
                          "identifier","source","language","relation","coverage","rights"]:
                elements = record.findall(f".//dc:{field}",ns)
                data[field] = [e.text for e in elements if e.text] or None
            records.append(data)
        token_elements = root.find(".//oai:resumptionToken", ns) # Lấy resumtionToken nếu có
        token = token_elements.text.strip() if token_elements is not None and token_elements.text else None
        return records,token
    def is_computer_science(self,record):
        text = " ".join(
            [t for lst in record.values() if lst for t in lst]
        ).lower()
        return any(k in text for k in self.KEYWORDS_CS)
    def fetch_data(self,api_key:str = "",checkpoint = "") -> list[dict]:
        token = checkpoint
        if token == "DONE":
            print("All dataset has been crawled")
            return
        page = 1
        total_records = []
        count_total = 0
        max_page = 1
        last_token = token
        print("Starting ORA crawler")
        if token:
            print(f"Resuming from saved token: {token[:40]}...")
        else:
            print("Starting from the beginning...")
        while page <= max_page:
            print(f"\nFetching page {page} ...")
            xml_data = self.fetch_record(token)
            records, token = self.parse_xml(xml_data)
            print(f"Received {len(records)} records")

            # Lọc Computer Science
            filtered = []
            for r in records:
                if self.is_computer_science(r):
                    filtered.append(r)
            total_records.extend(filtered)
            count_total += len(filtered)
            print(f"Saved {len(filtered)} new (Total: {count_total})")

            # Lưu checkpoint
            last_token = token

            # Dừng nếu hết token
            if not token:
                print("No more pages. Crawl completed.")
                token = "DONE"
                break
            if page < max_page:    
                print(f"Waiting {self.DELAY}s before next request...\n")
                time.sleep(self.DELAY)
            page += 1

        print(f"Total {len(total_records)} records ")
        return total_records,last_token


