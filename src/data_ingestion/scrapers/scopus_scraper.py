from data_ingestion.scrapers.base_scraper import BaseScraper
import requests
import json
import time
import os
from typing import Union
from concurrent.futures import ThreadPoolExecutor, as_completed

class ScopusScraper(BaseScraper):
    def __init__(self):
        self.keywords = [
            # AI & ML
            "artificial intelligence", "machine learning", "deep learning",
            "reinforcement learning", "neural network", "computer vision",
            "natural language processing", "pattern recognition", "expert system",
            "fuzzy logic", "generative AI", "transfer learning", "few-shot learning",
            "convolutional neural network", "recurrent neural network",
            "transformer model", "graph neural network", "meta learning",

            # Data & Knowledge
            "data mining computer science", "big data analytics", "data science", "data analytics",
            "information retrieval computer science", "knowledge discovery", "knowledge graph",
            "recommendation system", "predictive analytics", "text mining computer science",
            "ontology", "semantic web", "linked data", "data preprocessing", "feature engineering",

            # Software & Programming
            "software engineering", "programming language", "compiler", "interpreter",
            "DevOps", "agile software development", "cloud computing", "distributed system",
            "parallel computing", "operating system", "microservices",
            "software testing", "version control", "continuous integration", "containerization",

            # Networking & Security
            "cybersecurity", "network security", "cryptography computer science", "blockchain computer science",
            "IoT", "wireless network", "internet of things",
            "network protocols", "network topology", "firewall", "intrusion detection",
            "secure communication", "privacy-preserving computation",

            # Algorithms & Theory
            "algorithm computer science", "graph theory", "optimization", "computational complexity",
            "dynamic programming", "NP-complete", "approximation algorithm",
            "formal verification", "automata theory", "string matching algorithm", "search algorithm",
            "sorting algorithm", "randomized algorithm", "distributed algorithm", "online algorithm",

            # Hardware & Robotics
            "computer architecture", "FPGA", "VLSI", "embedded system",
            "robotics", "autonomous robot", "sensor network", "edge computing",
            "parallel processor", "GPU computing", "hardware acceleration", "real-time system",

            # HCI
            "human-computer interaction", "HCI", "user interface", "UX",
            "virtual reality", "augmented reality", "mixed reality",
            "usability study", "interaction design", "cognitive ergonomics",

            # Databases
            "relational database computer science", "NoSQL database", "SQL database",
            "data warehouse computer science", "ETL computer science", "query optimization computer science",
            "graph database", "temporal database", "database indexing", "transaction management",

            # Other emerging CS areas
            "quantum computing", "edge AI", "federated learning", "explainable AI",
            "computer graphics", "visual computing", "computational geometry", "parallel rendering",
            "bioinformatics CS", "computational neuroscience", "cryptanalysis CS"
        ]
        self.count_per_page = 25
        self.max_requests = 20
        self.timeout = 20
        self.retry_delay = 10
        self.save_interval = 100
        self.temp_file = "scopus_temp.json"

    def fetch_data(self, api_key: str, checkpoint: str = "0-2026-0") -> tuple[list[dict], str]:
        """
        checkpoint format: start-year-keyword_idx
        Crawl tuần tự theo checkpoint, mỗi lần 1 batch.
        """
        self.api_key = api_key
        all_results = []
        batch_num = 0
        start, year, kw_idx = map(int, checkpoint.split("-"))
        print("Bắt đầu crawl Scopus API...\n")

        for _ in range(self.max_requests):
            if year < 1980:
                print("Đã crawl hết tất cả năm và keyword")
                return all_results, checkpoint

            keyword = self.keywords[kw_idx]
            url = "https://api.elsevier.com/content/search/scopus"
            query = f'TITLE-ABS-KEY("{keyword}") AND PUBYEAR = {year}'
            params = {"query": query, "count": self.count_per_page, "start": start}
            headers = {"X-ELS-APIKey": self.api_key, "Accept": "application/json"}

            for attempt in range(2):
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Lỗi request start={start}, keyword='{keyword}', year={year}: {e}, thử lại...")
                    time.sleep(self.retry_delay)
            else:
                print(f"Bỏ qua batch start={start} sau khi retry thất bại")
                return all_results, checkpoint

            if response.status_code == 429:
                print(f"Rate limit exceeded tại start={start}, keyword='{keyword}', year={year}, chờ 10s...")
                time.sleep(10)
                return all_results, checkpoint
            elif response.status_code != 200:
                print(f"Lỗi {response.status_code}: {response.text}")
                return all_results, checkpoint

            data = response.json()
            records = data.get("search-results", {}).get("entry", [])
            if not records:
                print(f"Hết dữ liệu tại start={start}, keyword='{keyword}', year={year}")

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

            # cập nhật checkpoint cho lần crawl tiếp theo
            start += self.count_per_page
            if start >= 5000:
                start = 0
                kw_idx += 1
                if kw_idx >= len(self.keywords):
                    kw_idx = 0
                    year -= 1
                    
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            print(f"Đã xóa file tạm: {self.temp_file}")

        print(f"Tổng cộng đã crawl: {len(all_results)} record")

        new_checkpoint = f"{start}-{year}-{kw_idx}"
        return all_results, new_checkpoint

    def fetch_abstracts_parallel(self, doi_list: list[str], max_workers: int = 5) -> list[dict]:
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
                return "", None
        except requests.exceptions.RequestException:
            return "", None
