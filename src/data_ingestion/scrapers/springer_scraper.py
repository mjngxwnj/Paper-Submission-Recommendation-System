import requests
import json
import time
import os
from typing import Union

class SpringerScraper:
    def __init__(self):
        self.query = (
            '(keyword:"computer science" OR '
            'keyword:"artificial intelligence" OR '
            'keyword:"machine learning" OR '
            'keyword:"deep learning" OR '
            'keyword:"data mining" OR '
            'keyword:"computer vision" OR '
            'keyword:"natural language processing") '
            'AND series:"Lecture Notes in Computer Science"'
        )
        self.count_per_page = 25
        self.max_requests = 500
        self.delay = 1
        self.timeout = 10
        self.retry_delay = 5
        self.save_interval = 100
        self.temp_file = "springer_meta_tmp.json"
        

    def fetch_data(self, api_key: str = "", checkpoint: Union[int, str] = 0) -> tuple[list[dict], Union[int, str]]:
        self.api_key = api_key
        all_results = []
        print("Bắt đầu crawl Springer Meta API...\n")
        for i in range(self.max_requests):
            start = int(checkpoint) if isinstance(checkpoint, str) else checkpoint
            start = max(1, start)
            url = (
                f"https://api.springernature.com/meta/v2/json?"
                f"q={self.query}&p={self.count_per_page}&s={start}&api_key={self.api_key}"
            )

            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=self.timeout)
                    break
                except requests.exceptions.ReadTimeout:
                    print(f"Timeout ở start={start}, thử lại sau {self.retry_delay}s... (lần {attempt+1}/3)")
                    time.sleep(self.retry_delay)
            else:
                print(f"Bỏ qua start={start} sau 3 lần timeout.")
                continue

            if response.status_code == 429:
                print("Quá giới hạn tốc độ (429 Too Many Requests). Dừng lại.")
                break
            elif response.status_code != 200:
                print(f"Lỗi {response.status_code}: {response.text}")
                break

            data = response.json()
            records = data.get("records", [])
            if not records:
                print(f"Hết dữ liệu (start={start})")
                continue

            all_results.extend(records)
            if len(all_results) % self.save_interval < self.count_per_page:
                with open(self.temp_file, "w", encoding="utf-8") as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
                print(f"Đã lưu tạm {len(all_results)} record.")

            checkpoint = start + self.count_per_page
            time.sleep(self.delay)

        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            print(f"Đã xóa file tạm: {self.temp_file}")

        print(f"Tổng cộng đã crawl: {len(all_results)} record")
        return all_results, checkpoint
