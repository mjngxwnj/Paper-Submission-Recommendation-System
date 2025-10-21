# Git Workflow Tutorial for Team

## 1. Branches 🌿
- **main**: Nhánh chính, ổn định, chứa code đã review & test, dùng để release production.
- **dev**: Nhánh phát triển tổng hợp. Mọi feature branch sẽ merge vào nhánh này để test & tích hợp.
- **feature/architecture-data**: Branch làm việc của Scope 1, bao gồm kiến trúc hệ thống, Docker, cơ sở dữ liệu, object storage, pipeline ingestion, ...
- **feature/data-preprocessing**: Branch làm việc của Scope 2, bao gồm thu thập dữ liệu, data validation, data cleaning, schema, preprocessing, EDA, handle text data, ...
- **feature/feature-engineering**: Branch làm việc của Scope 3, bao gồm feature engineering, tạo embeddings, đánh giá chất lượng features, ...
- **feature/recommendation-engine**: Branch làm việc của Scope 4, bao gồm xây dựng và tinh chỉnh mô hình recommendation, huấn luyện, đánh giá model, ...



## 2. Feature Integration Workflow
![feature_integration_workflow](https://github.com/mjngxwnj/Paper-Submission-Recommendation-System/blob/main/docs/images/feature_integration_workflow.png)  

**Mũi tên xanh**: Push code, tức đẩy code từ nhánh feature của mình vào nhánh phát triển chung là "dev". Thao tác mặc định là dùng PR (Pull Request).  

**Mũi tên đỏ**: Pull code, tức kéo code từ dev (nhánh phát triển chung) về nhánh feature của mình để cập nhật code mới từ team và đồng bộ source với feature hiện tại mà mình đang phát triển. Thao tác mặc định là pull nhánh dev về + merge vào nhánh feature của mình.


### Các steps để đảm bảo hạn chế conflict & lệch tích hợp code trong quá trình phát triển feature:  

**Step 1**: Chuyển sang nhánh dev (nhánh phát triển tổng hợp) để check xem có source code mới từ team không
```bash
git checkout dev
git fetch origin
```
**Step 2**: Cập nhật code mới nhất từ nhánh dev
```bash
git pull origin dev
```
**Step 3**: Checkout trở lại nhánh feature của mình, merge code mới (từ nhánh dev) vào nhánh của mình đẻ đồng bộ source mới từ team và tiếp tục phát triển
```bash
git checkout feature/<your-feature-name>
git merge dev
```
**Step 4**: Tiếp tục phát triển & test nhánh của mình.  

**Step 5**: Sau khi dev & test xong, đẩy lên github, sau đó tạo PR (pull request) để yêu cầu merge vào nhánh dev. Request sẽ được check và phê duyệt trước khi merge vào nhánh dev cho team tiếp tục phát triển.

## 3. Git Command Dictionary 📖
**Clone repo về local**  

```bash
git clone <repo-url>
cd <repo-folder>
```

**Tổ hợp lệnh để cập nhật code mới từ main về nhánh hiện tại trên máy local (nếu có code mới trên main, pull trước rồi tiếp tục phát triển)**
```
git checkout main                     # Nhảy sang nhánh main
git pull origin main                  # Kéo code mới từ nhánh main trên remote về local
git checkout feature/<tên-feature>    # Nhảy sang nhánh feature
git merge main                        # Đồng bộ feature branch với main để tránh conflict
```

**Tạo nhánh và checkout sang nhánh làm việc**
```bash
git checkout -b feature/<tên-feature>
```

**Thêm file code vào git**
```bash
git add .
```

**Commit code với message**
```bash
git commit -m "[ScopeX]: <mô tả ngắn về thay đổi>"
```

**Push branch lên remote**
```bash
git push origin feature/<tên-feature>
```

**Merge to main**  
Sau khi push branch lên remote, vào branch trên GitHub và tạo Pull Request (PR) để merge vào `main`.  
