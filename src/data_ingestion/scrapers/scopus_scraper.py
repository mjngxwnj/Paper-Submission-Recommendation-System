import requests
import json
import time
import os
from typing import Union

class ScopusScraper:
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

            all_results.extend(records)
            checkpoint = start + self.count_per_page
            time.sleep(0.1)

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

