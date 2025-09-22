# Git Workflow Tutorial for Team

## 1. Branches
- **main**: Nhánh chính, ổn định, chỉ merge code đã review & test xong từ các feature branch.
- **feature/architecture-data**: Branch làm việc của Scope 1, bao gồm kiến trúc hệ thống, Docker, cơ sở dữ liệu, object storage, pipeline ingestion, ...
- **feature/data-preprocessing**: Branch làm việc của Scope 2, bao gồm thu thập dữ liệu, data validation, data cleaning, schema, preprocessing, EDA, handle text data, ...
- **feature/feature-engineering**: Branch làm việc của Scope 3, bao gồm feature engineering, tạo embeddings, đánh giá chất lượng features, ...
- **feature/recommendation-engine**: Branch làm việc chính của Scope 4, bao gồm xây dựng và tinh chỉnh mô hình recommendation, huấn luyện, đánh giá model, ...

## 2. Workflow
**Clone repo về local**  

```bash
git clone <repo-url>
cd <repo-folder>
```

**Tạo nhánh và checkout sang nhánh làm việc**
```bash
git checkout -b feature/<tên-feature>
```
**Code & Commit**
1. Thêm file code:
```bash
git add .
```
2. Commit với message:
```bash
git commit -m "[ScopeX]: <mô tả ngắn về thay đổi>"
```
3. Push branch lên remote:
```bash
git push origin feature/<tên-feature>
```
4. Merge to main: Sau khi push branch lên remote, vào branch trên GitHub và tạo Pull Request (PR) để merge vào `main`.  
