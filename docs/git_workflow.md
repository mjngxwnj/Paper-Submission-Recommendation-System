# Git Workflow Tutorial for Team

## 1. Branches 🌿
- **main**: Nhánh chính, ổn định, chỉ merge code đã review & test xong từ các feature branch.
- **feature/architecture-data**: Branch làm việc của Scope 1, bao gồm kiến trúc hệ thống, Docker, cơ sở dữ liệu, object storage, pipeline ingestion, ...
- **feature/data-preprocessing**: Branch làm việc của Scope 2, bao gồm thu thập dữ liệu, data validation, data cleaning, schema, preprocessing, EDA, handle text data, ...
- **feature/feature-engineering**: Branch làm việc của Scope 3, bao gồm feature engineering, tạo embeddings, đánh giá chất lượng features, ...
- **feature/recommendation-engine**: Branch làm việc chính của Scope 4, bao gồm xây dựng và tinh chỉnh mô hình recommendation, huấn luyện, đánh giá model, ...

## 2. Git Command Dictionary 📖
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
