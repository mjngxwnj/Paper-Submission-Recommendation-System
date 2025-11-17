from data_ingestion.scrapers.base_scraper import BaseScraper
import requests
import json
import time
import os
from typing import Union
from concurrent.futures import ThreadPoolExecutor, as_completed

class ScopusScraper(BaseScraper):
    def __init__(self):
        self.query = 'computer science'
        self.count_per_page = 25
        self.max_requests = 20  
        self.timeout = 20
        self.retry_delay = 10
        self.save_interval = 100  
        self.temp_file = "scopus_temp.json"

    def fetch_data(self, api_key: str, checkpoint: Union[int, str] = "0-2026") -> tuple[list[dict], Union[int, str]]:
        self.api_key = api_key
        all_results = []
        batch_num = 0
        
        checkpoint, year_extract = checkpoint.split("-")
        year_extract = int(year_extract)

        print("Bắt đầu crawl Scopus API...\n")

        for _ in range(self.max_requests):
            start = int(checkpoint)
            if start >= 5000:
                year_extract -= 1
                start = 0

            url = "https://api.elsevier.com/content/search/scopus"
            query = f"{self.query} AND PUBYEAR = {year_extract}"
            params = {"query": query, "count": self.count_per_page, "start": start}
            headers = {"X-ELS-APIKey": self.api_key, "Accept": "application/json"}

            # retry khi lỗi request
            for attempt in range(2):
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Lỗi request tại start={start}: {e}, thử lại...")
                    time.sleep(self.retry_delay)
            else:
                print(f"Bỏ qua batch start={start} sau khi retry thất bại")
                checkpoint = start + self.count_per_page
                continue

            if response.status_code == 429:
                print(f"Rate limit exceeded (429) tại start={start}, chờ 10s...")
                time.sleep(10)
                continue
            elif response.status_code != 200:
                print(f"Lỗi {response.status_code}: {response.text}")
                break

            data = response.json()
            records = data.get("search-results", {}).get("entry", [])
            if not records:
                print(f"Hết dữ liệu tại start={start}")
                break
            
            doi_list = [r.get("prism:doi") for r in records if r.get("prism:doi")]
            abstracts_info = self.fetch_abstracts_parallel(doi_list, max_workers=10)

            doi_map = {info["doi"]: info for info in abstracts_info}
            for r in records:
                doi = r.get("prism:doi")
                if doi in doi_map:
                    r["abstract"] = doi_map[doi]["abstract"]
                    r["subjects"] = doi_map[doi]["subjects"]

            all_results.extend(records)
            checkpoint = start + self.count_per_page

            # lưu tạm định kỳ
            if len(all_results) >= self.save_interval * (batch_num + 1):
                with open(self.temp_file, "w", encoding="utf-8") as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
                print(f"Đã lưu tạm {len(all_results)} record vào {self.temp_file}")
                batch_num += 1
                
        # --- cuối loop, lưu tạm tất cả record còn lại ---
        if all_results:
            with open(self.temp_file, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu tạm cuối: {len(all_results)} record")

        # cuối cùng lưu tất cả
        filename_all = "scopus_all.json"
        with open(filename_all, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"Tổng cộng đã crawl: {len(all_results)} record, lưu vào {filename_all}")

        # xóa file tạm nếu muốn
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            print(f"Đã xóa file tạm: {self.temp_file}")

        return all_results, f"{checkpoint}-{year_extract}"

    def fetch_abstracts_parallel(self, doi_list: list[str], max_workers: int = 5) -> list[dict]:
        """
        Lấy abstract và subjects song song từ Article Retrieval API cho nhiều DOI.
        Trả về list dict: [{"doi":..., "abstract":..., "subjects":...}, ...]
        """
        results = []

        def fetch_single(doi):
            abstract, subjects = self.fetch_abstract(doi)
            return {"doi": doi, "abstract": abstract, "subjects": subjects}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_single, doi) for doi in doi_list]
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"Error fetching abstract for DOI: {e}")

        return results
        
    def fetch_abstract(self, doi: str) -> tuple[str, Union[list[str], None]]:
        url = f"https://api.elsevier.com/content/article/doi/{doi}"
        headers = {"X-ELS-APIKey": self.api_key, "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                abstract = data.get("full-text-retrieval-response", {}).get("coredata", {}).get("dc:description", "")
                subjects = data.get('full-text-retrieval-response', {}).get('coredata', {}).get('dcterms:subject')
                return abstract, subjects
            else:
                #print(f"Lỗi lấy abstract cho DOI {doi}: {response.status_code}")
                return "", None
        except requests.exceptions.RequestException as e:
            #print(f"Lỗi request lấy abstract cho DOI {doi}: {e}")
            return "", None
