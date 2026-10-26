"""Tạo báo cáo storytelling 1 trang (HTML rồi PDF) từ data/processed/insights.json.

Chạy:  python build_report.py
PDF được in bằng Chrome/Chromium headless (tìm trên PATH hoặc theo biến môi trường CHROME); nếu không có, mở report.html và In → Lưu PDF.
Báo cáo chỉ ghi nguồn ở hai chỗ: dòng "Biểu đồ" dưới mỗi phát hiện (nơi biểu đồ tương tác được thể hiện) và mục nguồn dữ liệu ở cuối trang.
"""
import html
import os
import re
import shutil
import subprocess
from pathlib import Path

from build_dashboard import INSIGHTS, SECTIONS, STUDENT, vn

ROOT = Path(__file__).parent
NAME = "PhamGiaKhanh_B25DCTN064_giuaKy"
SECTION_NAME = {sid: name for sid, name, _ in SECTIONS}

CSS = """
@page{size:A4;margin:11mm 13mm}
body{font:9.3pt/1.38 "Be Vietnam Pro","Segoe UI","Noto Sans","DejaVu Sans",system-ui,sans-serif;color:#1d2433;margin:0}
h1{font-size:14.5pt;line-height:1.22;margin:0 0 3px}
.sub{color:#5b6475;font-size:8.4pt;margin-bottom:6px}
.kpis{display:flex;gap:7px;margin:4px 0 6px}
.kpi{flex:1;border:1px solid #dfe3e8;border-radius:6px;padding:4px 8px}
.kpi b{font-size:13pt;display:block;color:#0072B2}.kpi span{font-size:7.9pt;color:#5b6475}
.data{background:#f3f6f9;border-radius:6px;padding:4px 9px;font-size:8.3pt;margin-bottom:2px}
h2{font-size:10.4pt;margin:7px 0 1px;color:#0072B2}
p{margin:0}ul{margin:1px 0 0;padding-left:16px}li{margin:0 0 1px}
.where{color:#6b7383;font-size:7.8pt;margin-top:1px}
.vn h2{color:#b34700}
.box{background:#fff8ec;border-left:3px solid #E69F00;padding:4px 9px;margin-top:7px}
.box h2{color:#a06800;margin-top:0}
.foot{color:#5b6475;font-size:7.6pt;margin-top:6px;border-top:1px solid #dfe3e8;padding-top:3px}
"""


def where(nums, *sections):
    """Dòng chỉ nơi biểu đồ được thể hiện: số biểu đồ và mục tương ứng trong index.html."""
    names = ", ".join(f"“{SECTION_NAME[s]}”" for s in sections)
    return f'<div class="where">Biểu đồ {nums} – index.html, mục {names}</div>'


def story(i):
    v, vf = i["vn"], i["vn"]["compare"]
    vol = {r["chỉ số"]: r["giá trị"] for r in i["volume"]}
    p, g, y, th = v["per1000"], v["cagr_2023_2025"], v["by_year"], v["themes"]
    about = th["Học về AI (năng lực, chương trình)"]
    pct = lambda x, d=0: f"{vn(x, d)}%"
    return {
        "headline": (f"Sau ChatGPT, nghiên cứu về AI trong giáo dục đại học tăng gấp {vn(i['mult_2025_2022'])} lần; "
                     f"Việt Nam tăng nhanh hơn thế giới nhưng quy mô còn nhỏ và ít hợp tác quốc tế"),
        "kpis": [
            (vn(i["api_count"]), "bài nghiên cứu 2015–2026"),
            (f"×{vn(i['mult_2025_2022'])}", "số bài 2025 so với 2022"),
            (vn(i["n_countries"]), "quốc gia có tác giả"),
            (vn(v["n"]), f"bài có tác giả Việt Nam (hạng {v['rank']['2026']} năm 2026)"),
        ],
        "data": (f"<b>Dữ liệu.</b> {vol['Số trang đã tải bằng cursor (200 bài/trang)']} trang JSON ({vn(vol['Dung lượng dữ liệu thô trong data/raw (MB)'], 1)} MB) "
                 f"tải qua OpenAlex API bằng requests → loại {vol['Dòng trùng ID đã loại']} dòng trùng ID và {vol['Bài trùng DOI đã loại']} bài trùng DOI → "
                 f"{vn(i['n_clean'])} bài; {vn(vol['Số trường/viện khác nhau (ID OpenAlex)'])} trường/viện, {vn(vol['Số tác giả khác nhau'])} tác giả, "
                 f"{vn(vol['Số từ khoá khác nhau'])} từ khoá. Thiếu quốc gia {pct(vol['Không có quốc gia (%)'], 1)}, tóm tắt {pct(vol['Thiếu tóm tắt (%)'], 1)}, "
                 f"nhãn ngôn ngữ {pct(vol['Thiếu nhãn ngôn ngữ (%)'], 1)}. Đặc trưng mới: log trích dẫn, trích dẫn/năm, số quốc gia, hợp tác quốc tế, giai đoạn, châu lục."),
        "world": [
            ("1. Xu hướng: gần như toàn bộ nghiên cứu ra đời sau ChatGPT",
             f"{pct(i['share_2023_on'], 1)} số bài xuất bản từ 2023. Số bài tăng từ {vn(i['count_2022'])} (2022) lên {vn(i['count_2025'])} (2025), "
             f"tốc độ tăng kép từ {i['cagr_2018_2022']}%/năm (2018–2022) lên {i['cagr_2022_2025']}%/năm (2022–2025); mới 10 tháng, 2026 đã có "
             f"{vn(i['count_2026'])} bài, vượt cả năm 2025.", where("①", "xu-huong")),
            ("2. Biến động: tăng vọt rồi chậm dần, chưa bão hoà",
             f"Tốc độ tăng đạt đỉnh +{vn(i['yoy']['2023'])}% năm 2023 rồi giảm còn +{vn(i['yoy']['2024'])}% và +{vn(i['yoy']['2025'])}%. "
             f"Trung bình trượt 3 tháng đi từ {i['rolling_2022_12']} lên {i['rolling_last']} bài/tháng ({i['last_month']}) mà không có đợt giảm kéo dài.",
             where("③ ④", "bien-dong")),
            ("3. Chủ đề và địa lý: từ công cụ sang đạo đức, châu Á dẫn dắt",
             f"'{i['top_last'][0]}' có trong {pct(i['top_last_share'])} bài 2025–2026; 'ChatGPT' giảm từ {pct(i['chatgpt_2324'])} (2023–2024) xuống "
             f"{pct(i['chatgpt_last'])}, 'academic integrity' lên {pct(i['integrity_last'])}. Châu Á tăng từ {pct(i['asia_2019'])} lên "
             f"{pct(i['asia_2026'])} lượt tham gia, châu Âu giảm từ {pct(i['europe_2019'])} xuống {pct(i['europe_2026'])}.",
             where("② ⑪ ⑫", "xu-huong", "chu-de")),
        ],
        "vn": [
            (f"<b>Quy mô:</b> từ {y['2023']} bài (2023) lên {y['2025']} bài (2025), tăng {g['VN']}%/năm so với {g['WORLD']}% của thế giới; tỷ trọng từ "
             f"{vn(p['VN']['2023'], 1)}‰ lên {vn(p['VN']['2026'], 1)}‰, hạng từ {v['rank']['2023']} lên {v['rank']['2026']}. Vẫn gần Thái Lan "
             f"({vn(p['TH']['2026'], 1)}‰), còn Indonesia gấp {vn(p['ID']['2026'] / p['VN']['2026'], 1)} lần.", "⑬"),
            (f"<b>Hợp tác và tác động:</b> {pct(vf['VN']['hop_tac_quoc_te_%'])} số bài có hợp tác quốc tế, ngang thế giới ({pct(vf['WORLD']['hop_tac_quoc_te_%'])}) "
             f"nhưng thấp hơn Thái Lan ({pct(vf['TH']['hop_tac_quoc_te_%'])}) và Malaysia ({pct(vf['MY']['hop_tac_quoc_te_%'])}). FWCI {vn(vf['VN']['fwci_tb'], 2)} "
             f"(khoảng tin cậy 95%: {vn(vf['VN']['fwci_ci_low'], 2)}–{vn(vf['VN']['fwci_ci_high'], 2)}) chưa khác thế giới ({vn(vf['WORLD']['fwci_tb'], 2)}).", "⑭"),
            (f"<b>Chủ đề:</b> nghiêng về AI tạo sinh ({pct(th['AI tạo sinh & LLM']['viet_nam_%'])} so với {pct(th['AI tạo sinh & LLM']['the_gioi_%'])}), "
             f"thái độ và chấp nhận ({pct(th['Chấp nhận & thái độ']['viet_nam_%'])} so với {pct(th['Chấp nhận & thái độ']['the_gioi_%'])}) và dạy tiếng Anh "
             f"('{v['lift_top'][0][0]}' {pct(v['lift_top'][0][2], 1)} so với {pct(v['lift_top'][0][3], 1)}). Bài coi AI là nội dung cần dạy chiếm "
             f"{pct(about['viet_nam_%'], 1)} so với {pct(about['the_gioi_%'], 1)}, khác biệt chưa có ý nghĩa thống kê.", "⑮"),
            (f"<b>Trường:</b> {v['n_inst']} trường/viện có bài; {v['top_inst'][0][0]} ({v['top_inst'][0][1]}) và {v['top_inst'][1][0]} "
             f"({v['top_inst'][1][1]}) dẫn đầu, ba đơn vị đầu góp mặt trong {pct(v['top3_share'])} số bài.", "⑯"),
        ],
        "limits": (f"Chỉ gồm bài OpenAlex xếp vào chủ đề 'AI in Education' (precision {i['precision']}% ± {vn(i['precision_margin'], 1)}% trên "
                   f"{i['precision_k']} bài ngẫu nhiên). {pct(i['missing_country'], 1)} bài không có quốc gia nên số theo nước nghiêng về nước nói tiếng Anh; "
                   f"2026 chưa đủ năm và bài mới chưa kịp được trích dẫn. Phần Việt Nam chỉ có {v['n']} bài; nhãn ngôn ngữ của OpenAlex sai ở một số bài "
                   f"và tạp chí trong nước có thể chưa được lập chỉ mục, nên số của Việt Nam nhiều khả năng bị đếm thiếu."),
        "meaning": ("Câu hỏi nghiên cứu đã chuyển từ 'có nên dùng AI' sang 'dùng thế nào cho đúng': liêm chính học thuật, năng lực AI, tư duy phản biện. "
                    "Ở Việt Nam, nghiên cứu vẫn chủ yếu khảo sát cách dùng công cụ AI tạo sinh. Hai hướng nên bổ sung là nghiên cứu về chương trình "
                    "và năng lực AI, và hợp tác quốc tế nhiều hơn."),
        "source": (f"<b>Nguồn dữ liệu:</b> OpenAlex API (api.openalex.org, giấy phép CC0), truy vấn chủ đề T14414 có 'higher education' hoặc 'university', "
                   f"article/review/conference-paper, 2015–2026, tải ngày {i['download_date']}; Priem, Piwowar &amp; Orr (2022), arXiv:2205.01833. "
                   f"Bản tương tác của 16 biểu đồ ①–⑯: index.html. Code: collect_openalex.py (thu thập), {NAME}.ipynb (xử lý, phân tích, biểu đồ)."),
    }


def build():
    s = story(INSIGHTS)
    esc = lambda t: html.escape(t, quote=False)
    kpis = "".join(f'<div class="kpi"><b>{v}</b><span>{esc(t)}</span></div>' for v, t in s["kpis"])
    world = "".join(f"<h2>{esc(t)}</h2><p>{esc(x)}</p>{w}" for t, x, w in s["world"])
    vn_items = "".join(f"<li>{x}</li>" for x, _ in s["vn"])
    vn_where = where(" ".join(n for _, n in s["vn"]), "viet-nam")
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{NAME}</title><style>{CSS}</style></head><body>
<h1>{esc(s["headline"])}</h1>
<div class="sub">Báo cáo storytelling – Dạy và học AI tại các trường đại học · {STUDENT} · Dữ liệu OpenAlex tải ngày {INSIGHTS["download_date"]}</div>
<div class="kpis">{kpis}</div>
<div class="data">{s["data"]}</div>
{world}
<div class="vn"><h2>4. Việt Nam so với thế giới: tăng nhanh, nhưng nhỏ và thiên về dùng công cụ</h2><ul>{vn_items}</ul>{vn_where}</div>
<div class="box"><h2>Giới hạn</h2><p>{esc(s["limits"])}</p></div>
<h2>Ý nghĩa</h2><p>{esc(s["meaning"])}</p>
<div class="foot">{s["source"]}</div>
</body></html>"""
    out_html = ROOT / "report.html"
    out_html.write_text(page, encoding="utf-8")
    print("Đã ghi", out_html)

    chrome = next((c for c in [os.environ.get("CHROME")] + [shutil.which(c) for c in ("google-chrome", "chromium", "chromium-browser")] if c), None)
    if not chrome:
        print("Không tìm thấy Chrome/Chromium: mở report.html và In → Lưu PDF.")
        return
    out_pdf = ROOT / f"{NAME}.pdf"
    args = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}", out_html.resolve().as_uri()]
    if hasattr(os, "geteuid") and os.geteuid() == 0:  # Chrome không chạy sandbox dưới quyền root (ví dụ trong container)
        args.insert(1, "--no-sandbox")
    subprocess.run(args, check=True, capture_output=True)
    pages = shutil.which("pdfinfo") and re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(out_pdf)], capture_output=True, text=True).stdout)
    print("Đã ghi", out_pdf, f"({pages.group(1)} trang)" if pages else "")


if __name__ == "__main__":
    build()
