"""Bước Collection: tải dữ liệu thô từ OpenAlex API bằng requests (phân trang cursor, 200 bài/trang).

Notebook PhamGiaKhanh_B25DCTN064_giuaKy.ipynb chỉ đọc kết quả của bước này. Bản chụp trong data/raw/ được tải ngày
23/10/2026 trên Kaggle bằng các lời gọi API tương tự; script này để chạy lại bước thu thập trên máy bất kỳ.

Chạy:  python collect_openalex.py                          # tải toàn bộ vào data/raw_moi/ (khoảng 140 lần gọi API)
       python collect_openalex.py --max-pages 2 --out thu   # chạy thử 2 trang
Key (nếu có) đọc từ biến môi trường OPENALEX_API_KEY, không viết vào code. Mặc định không ghi vào data/raw/ để giữ nguyên
bản chụp đang dùng cho báo cáo. cursor_state.json được ghi sau mỗi trang, nên chạy lại sẽ tải tiếp từ chỗ bị ngắt.
"""
import argparse
import csv
import datetime as dt
import json
import os
import time
from pathlib import Path

import requests

API = "https://api.openalex.org"
FILTER = ('primary_topic.id:T14414,title_and_abstract.search:"higher education" OR university,'
          "type:article|review|conference-paper,publication_year:2015-2026")
SELECT = ("id,doi,title,publication_year,publication_date,type,language,cited_by_count,fwci,authorships,"
          "primary_topic,keywords,abstract_inverted_index,open_access,referenced_works_count")
# Các biến thể truy vấn đã so để chọn FILTER (query_variants.csv); F là truy vấn được chọn, chưa giới hạn năm.
SEARCH = "title_and_abstract.search:artificial intelligence higher education"
TYPES = "type:article|conference-paper|review"
VARIANTS = {
    "A – từ khoá rời": SEARCH,
    "B' – A + loại tài liệu": f"{SEARCH},{TYPES}",
    "C – article + tiếng Anh": f"language:en,{SEARCH},type:article",
    "G – cụm từ chính xác": f'title_and_abstract.search:"artificial intelligence" "higher education",{TYPES}',
    "F – topic + (HE OR university)": f'primary_topic.id:T14414,title_and_abstract.search:"higher education" OR university,{TYPES}',
}
N_INSTITUTIONS, PRECISION_K, SEED = 400, 100, 1


class OpenAlex:
    def __init__(self, session=None, pause=0.15):
        self.s = session or requests.Session()
        self.key = os.environ.get("OPENALEX_API_KEY")
        self.pause = pause
        self.calls = 0

    def get(self, path, **params):
        if self.key:
            params["api_key"] = self.key
        for attempt in range(5):
            r = self.s.get(f"{API}/{path}", params=params, timeout=60)
            self.calls += 1
            if r.status_code in (429, 500, 502, 503, 504):  # quá tải hoặc lỗi tạm thời: đợi rồi thử lại
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            time.sleep(self.pause)
            return r.json()
        r.raise_for_status()

    def count(self, flt):
        return self.get("works", filter=flt, **{"per-page": 1, "select": "id"})["meta"]["count"]

    def group_by(self, flt, key):
        return self.get("works", filter=flt, group_by=key)["group_by"]


def download_works(oa, out, max_pages=None):
    """Tải mọi bài khớp FILTER, mỗi trang một file works/page_NNNN.json. Trả về số trang."""
    (out / "works").mkdir(parents=True, exist_ok=True)
    state_file = out / "cursor_state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {"cursor": "*", "page": 0}
    while state["cursor"] and (max_pages is None or state["page"] < max_pages):
        data = oa.get("works", filter=FILTER, select=SELECT, cursor=state["cursor"], **{"per-page": 200})
        if not data["results"]:
            state["cursor"] = None
            break
        (out / f"works/page_{state['page']:04d}.json").write_text(json.dumps(data["results"], ensure_ascii=False), encoding="utf-8")
        state = {"cursor": data["meta"].get("next_cursor"), "page": state["page"] + 1}
        state_file.write_text(json.dumps(state))
        print(f"trang {state['page']}: {len(data['results'])} bài")
    return state["page"]


def download_counts(oa, out):
    """Số bài theo năm và theo (năm, quốc gia), đếm bằng group_by trên toàn bộ kết quả của FILTER."""
    yearly = oa.group_by(FILTER, "publication_year")
    (out / "yearly.json").write_text(json.dumps(yearly, ensure_ascii=False), encoding="utf-8")
    rows = []
    for y in sorted(int(g["key"]) for g in yearly):
        flt = FILTER.replace("publication_year:2015-2026", f"publication_year:{y}")
        for g in oa.group_by(flt, "authorships.countries"):
            code = g["key"].split("/")[-1].upper()
            if code and code != "UNKNOWN":
                rows.append({"year": y, "country": code, "name": g["key_display_name"], "count": g["count"]})
    (out / "country_year.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return yearly


def download_institutions(oa, out):
    """Hồ sơ N_INSTITUTIONS trường có nhiều bài nhất (group_by trả tối đa 200 nhóm mỗi lần nên phân trang cursor)."""
    ids, cursor = [], "*"
    while cursor and len(ids) < N_INSTITUTIONS:
        data = oa.get("works", filter=FILTER, group_by="authorships.institutions.id", cursor=cursor, **{"per-page": 200})
        ids += [g["key"].split("/")[-1] for g in data["group_by"] if g["key"] and "unknown" not in g["key"].lower()]
        cursor = data["meta"].get("next_cursor")
    insts = []
    for k in range(0, min(len(ids), N_INSTITUTIONS), 50):
        batch = "|".join(ids[k:min(k + 50, N_INSTITUTIONS)])
        insts += oa.get("institutions", filter=f"openalex:{batch}", select="id,display_name,country_code,type,geo,works_count,cited_by_count",
                        **{"per-page": 50})["results"]
    (out / "institutions.json").write_text(json.dumps(insts, ensure_ascii=False), encoding="utf-8")
    return len(insts)


def query_variants_and_samples(oa, out):
    """Đếm số bài của từng biến thể truy vấn và rút mẫu ngẫu nhiên để chấm precision bằng tay (cột 'đúng' để trống)."""
    counts = {name: oa.count(flt) for name, flt in VARIANTS.items()}
    base = counts["A – từ khoá rời"]
    with open(out / "query_variants.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["biến thể", "count", "filter", "% so với A"])
        for name, flt in VARIANTS.items():
            w.writerow([name, counts[name], flt, round(100 * counts[name] / base, 1)])
    with open(out / "precision_samples.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "publication_year", "type", "đúng", "bien_the"])
        for tag in ("G", "F"):
            flt = next(v for k, v in VARIANTS.items() if k.startswith(tag))
            for r in oa.get("works", filter=flt, sample=PRECISION_K, seed=SEED, select="id,title,publication_year,type",
                            **{"per-page": PRECISION_K})["results"]:
                w.writerow([r["id"], r["title"], r["publication_year"], r["type"], "", tag])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="data/raw_moi", help="thư mục ghi dữ liệu thô (mặc định data/raw_moi)")
    ap.add_argument("--max-pages", type=int, default=None, help="chỉ tải tối đa N trang bài báo (để chạy thử)")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    oa = OpenAlex()
    count_api = oa.count(FILTER)
    print(f"OpenAlex báo {count_api:,} bài khớp truy vấn")
    pages = download_works(oa, out, args.max_pages)
    download_counts(oa, out)
    n_inst = download_institutions(oa, out)
    query_variants_and_samples(oa, out)
    rows = [w for p in sorted((out / "works").glob("page_*.json")) for w in json.loads(p.read_text(encoding="utf-8"))]
    log = {"ngay_tai": dt.date.today().isoformat(), "filter": FILTER, "count_api": count_api, "so_dong_tai_ve": len(rows),
           "trung_id_da_loai": len(rows) - len({w["id"] for w in rows}), "so_bai": len({w["id"] for w in rows}),
           "so_trang": pages, "so_truong": n_inst, "so_lan_goi_api": oa.calls}
    (out / "download_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
