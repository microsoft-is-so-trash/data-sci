"""Tạo báo cáo insight 1 trang (HTML rồi PDF) từ data/processed/insights.json.

Chạy:  python build_report.py
PDF được in bằng Chrome/Chromium headless nếu máy có; nếu không, mở report.html và In → Lưu PDF.
"""
import html
import shutil
import subprocess
from pathlib import Path

from build_dashboard import INSIGHTS, findings, vn

ROOT = Path(__file__).parent
NAME = "PhamGiaKhanh_MaSV_giuaKy"

CSS = """
@page{size:A4;margin:14mm 15mm}
body{font:10.4pt/1.42 "Be Vietnam Pro","Segoe UI",system-ui,sans-serif;color:#1d2433;margin:0}
h1{font-size:15.5pt;line-height:1.25;margin:0 0 3px}
.sub{color:#5b6475;font-size:9pt;margin-bottom:8px}
.kpis{display:flex;gap:8px;margin:6px 0 9px}
.kpi{flex:1;border:1px solid #dfe3e8;border-radius:6px;padding:5px 8px}
.kpi b{font-size:14pt;display:block;color:#0072B2}.kpi span{font-size:8.5pt;color:#5b6475}
h2{font-size:11pt;margin:9px 0 2px;color:#0072B2}
p{margin:0 0 3px}
.box{background:#fff8ec;border-left:3px solid #E69F00;padding:5px 9px;margin-top:8px}
.box h2{color:#a06800;margin-top:0}
.foot{color:#5b6475;font-size:8.3pt;margin-top:8px;border-top:1px solid #dfe3e8;padding-top:4px}
"""


def build():
    i, f = INSIGHTS, findings(INSIGHTS)
    kpis = [
        (vn(i["api_count"]), "bài nghiên cứu 2015–2026"),
        (f"×{vn(i['mult_2025_2022'])}", "số bài 2025 so với 2022"),
        (f"{vn(i['share_2023_on'], 1)}%", "bài ra đời từ 2023"),
        (vn(i["n_countries"]), "quốc gia tham gia"),
    ]
    blocks = "".join(f"<h2>{html.escape(t)}</h2><p>{html.escape(x)}</p>" for t, x in (f["f1"], f["f2"], f["f3"]))
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{NAME}</title><style>{CSS}</style></head><body>
<h1>{html.escape(f["headline"])}</h1>
<div class="sub">Báo cáo insight – Dạy và học AI tại các trường đại học · Phạm Gia Khánh – &lt;MaSV&gt; · Dữ liệu OpenAlex tải ngày {i["download_date"]}</div>
<div class="kpis">{"".join(f'<div class="kpi"><b>{v}</b><span>{t}</span></div>' for v, t in kpis)}</div>
{blocks}
<h2>Về tác động trích dẫn</h2><p>{html.escape(f["impact"])}</p>
<div class="box"><h2>Giới hạn</h2><p>{html.escape(f["limits"])}</p></div>
<h2>Ý nghĩa</h2><p>{html.escape(f["meaning"])}</p>
<div class="foot">{html.escape(f["method"])} Biểu đồ ①–⑫ ở index.html; code ở {NAME}.ipynb.</div>
</body></html>"""
    out_html = ROOT / "report.html"
    out_html.write_text(page, encoding="utf-8")
    print("Đã ghi", out_html)

    chrome = next((shutil.which(c) for c in ("google-chrome", "chromium", "chromium-browser") if shutil.which(c)), None)
    if not chrome:
        print("Không tìm thấy Chrome/Chromium: mở report.html và In → Lưu PDF.")
        return
    out_pdf = ROOT / f"{NAME}.pdf"
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", out_html.resolve().as_uri()], check=True, capture_output=True)
    print("Đã ghi", out_pdf)


if __name__ == "__main__":
    build()
