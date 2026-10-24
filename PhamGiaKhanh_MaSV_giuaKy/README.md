# Dạy và học AI tại các trường đại học – Bài giữa kỳ

Phạm Gia Khánh – `<MaSV>`

Mở `index.html` bằng trình duyệt để xem 12 biểu đồ tương tác. Trang không cần mạng hay server. Báo cáo insight 1 trang nằm ở `PhamGiaKhanh_MaSV_giuaKy.pdf`.

## Nội dung thư mục

| File | Nội dung |
| --- | --- |
| `index.html` | Trang kết quả: KPI, 12 biểu đồ Plotly, mục Insight |
| `PhamGiaKhanh_MaSV_giuaKy.ipynb` | Code chính: Collection → Profiling → Cleansing → Structuring → Transformation → Validation → Visualization → Insight |
| `PhamGiaKhanh_MaSV_giuaKy.pdf` | Báo cáo insight 1 trang (tạo từ `report.html`) |
| `build_dashboard.py` | Ghép các biểu đồ trong `data/processed/figs/` thành `index.html` |
| `build_report.py` | Tạo `report.html` và in ra PDF bằng Chrome headless |
| `data/raw/` | Bản chụp dữ liệu thô tải ngày 23/10/2026 (không sửa) |
| `data/processed/` | Dữ liệu đã làm sạch, bảng dạng dài cho từng biểu đồ (`chartNN_*.csv`), data dictionary, bảng chấm điểm chất lượng đã xác minh |
| `requirements.txt` | Phiên bản thư viện |

## Dữ liệu

- Nguồn: OpenAlex API (https://api.openalex.org), dữ liệu thứ cấp, giấy phép CC0.
- Ngày tải: 2026-10-23.
- Truy vấn: `primary_topic.id:T14414,title_and_abstract.search:"higher education" OR university,type:article|review|conference-paper,publication_year:2015-2026`. Nghĩa là các bài OpenAlex xếp vào chủ đề *Artificial Intelligence in Education*, có nhắc "higher education" hoặc "university", gồm article, review và bài hội nghị.
- Căn cứ chọn truy vấn: so 5 biến thể trong `data/raw/query_variants.csv`. Precision đo trên 100 bài ngẫu nhiên (seed = 1, `precision_samples.csv`): 96% ± 3,8%, so với 79% của truy vấn theo cụm từ.
- Số bài: API báo 23.712 bài. Tải về 23.699 dòng; sau khi khử 154 dòng trùng ID và 5 cặp trùng DOI còn 23.540 bài (lệch 0,7%). Có thêm dữ liệu 400 trường nhiều bài nhất.
- Chất lượng dữ liệu: `data/processed/quality_scorecard_verified.csv` (7 quy tắc) và `cleaning_plan_verified.csv` (hành động đã áp dụng).
- File thô: `works/page_*.json` (119 trang), `yearly.json` và `country_year.json` (số đếm `group_by` trên toàn bộ dữ liệu), `institutions.json`, `download_log.json`.

## Cách chạy lại

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace PhamGiaKhanh_MaSV_giuaKy.ipynb
python build_dashboard.py
python build_report.py
```

Notebook chỉ đọc `data/raw/`, không gọi API, nên lần chạy nào cũng cho cùng kết quả. Muốn tải dữ liệu mới thì chạy Phần A–C của notebook Kaggle với Kaggle Secret tên `OpenAlex`. Không viết API key vào code.

## Ghi chú phương pháp

- Năm 2026 chưa đủ năm, nên không đưa vào YoY/CAGR và được vẽ nét đứt.
- Chuỗi theo tháng bỏ 14,7% bài chỉ ghi năm (ngày 01-01).
- Số đếm theo quốc gia là *lượt tham gia*: một bài có tác giả ở hai nước được tính cho cả hai.
- Sunburst ⑪ dùng từ khoá thay cho cây domain → topic. Lý do: mọi bài có cùng `primary_topic`, nên cây đó chỉ có một nhánh.
