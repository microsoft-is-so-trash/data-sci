# Dạy và học AI tại các trường đại học – Bài giữa kỳ

Phạm Gia Khánh – B25DCTN064

Mở `index.html` bằng trình duyệt để xem 16 biểu đồ tương tác. Trang không cần mạng hay server. Báo cáo storytelling 1 trang nằm ở `PhamGiaKhanh_B25DCTN064_giuaKy.pdf`: đặc trưng dữ liệu, 3 phát hiện toàn cầu, Việt Nam so với thế giới, giới hạn và nguồn dữ liệu.

## Nội dung thư mục

| File | Nội dung |
| --- | --- |
| `index.html` | Trang kết quả: KPI, mục Dữ liệu & xử lý, 16 biểu đồ Plotly tương tác (⑬–⑯ là phần Việt Nam), mục Insight |
| `collect_openalex.py` | Collection: tải dữ liệu thô từ OpenAlex API bằng `requests` (cursor, 200 bài/trang), đếm `group_by`, hồ sơ trường, biến thể truy vấn và mẫu precision |
| `PhamGiaKhanh_B25DCTN064_giuaKy.ipynb` | Code chính: Collection → Profiling → Cleansing → Structuring → Transformation → Validation → Visualization → Insight |
| `PhamGiaKhanh_B25DCTN064_giuaKy.pdf` | Báo cáo storytelling 1 trang (tạo từ `report.html`) |
| `build_dashboard.py` | Ghép các biểu đồ trong `data/processed/figs/` thành `index.html` |
| `build_report.py` | Tạo `report.html` và in ra PDF 1 trang bằng Chrome headless |
| `data/raw/` | Bản chụp dữ liệu thô tải ngày 23/10/2026 (không sửa) |
| `data/processed/` | Dữ liệu đã làm sạch, bảng dạng dài cho từng biểu đồ (`chartNN_*.csv`), `data_volume.csv` (đặc trưng lượng dữ liệu), data dictionary, bảng chấm điểm chất lượng đã xác minh |
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
python collect_openalex.py   # tuỳ chọn: tải lại dữ liệu vào data/raw_moi/ (không ghi đè data/raw/)
jupyter nbconvert --to notebook --execute --inplace PhamGiaKhanh_B25DCTN064_giuaKy.ipynb
python build_dashboard.py
python build_report.py   # nếu Chrome không có trên PATH: CHROME=/đường/dẫn/chrome python build_report.py
```

Notebook chỉ đọc `data/raw/`, không gọi API, nên lần chạy nào cũng cho cùng kết quả. Muốn tải dữ liệu mới thì chạy `collect_openalex.py`. Script đọc key từ biến môi trường `OPENALEX_API_KEY` nếu có và không viết key vào code. Bản chụp trong `data/raw/` được tải trên Kaggle ngày 23/10/2026 bằng cùng cách gọi API.

## Ghi chú phương pháp

- Năm 2026 chưa đủ năm, nên không đưa vào YoY/CAGR và được vẽ nét đứt.
- Chuỗi theo tháng bỏ 14,7% bài chỉ ghi năm (ngày 01-01).
- Số đếm theo quốc gia là *lượt tham gia*: một bài có tác giả ở hai nước được tính cho cả hai.
- Sunburst ⑪ dùng từ khoá thay cho cây domain → topic. Lý do: mọi bài có cùng `primary_topic`, nên cây đó chỉ có một nhánh.
- Phần Việt Nam (⑬–⑯): bài Việt Nam là bài có ít nhất một tác giả ở Việt Nam. Phần này so với thế giới và Thái Lan, Malaysia, Indonesia, Trung Quốc, Hoa Kỳ bằng số đã chuẩn hoá (‰ số bài thế giới, % số bài của nước, FWCI kèm khoảng tin cậy bootstrap). Khác biệt chủ đề được kiểm định bằng z hai tỷ lệ.
- Bộ lọc "học về AI" (AI literacy, năng lực, chương trình, kỹ năng AI) dựa trên quy tắc từ khoá và tiêu đề, chưa được chấm tay. Notebook chỉ báo tỷ lệ bài được gắn nhãn có nhắc trực tiếp các cụm này, coi như một bước kiểm tra nhất quán.
