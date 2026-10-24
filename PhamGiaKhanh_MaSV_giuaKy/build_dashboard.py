"""Ghép 12 biểu đồ Plotly (data/processed/figs/*.json) thành một trang index.html tĩnh.

Chạy sau notebook:  python build_dashboard.py
Mọi con số trong trang lấy từ data/processed/insights.json do notebook tạo ra.
"""
import html
import json
from pathlib import Path

import plotly.io as pio

ROOT = Path(__file__).parent
FIG_DIR = ROOT / "data/processed/figs"
INSIGHTS = json.loads((ROOT / "data/processed/insights.json").read_text(encoding="utf-8"))

SECTIONS = [
    ("xu-huong", "Xu hướng", "Bao nhiêu nghiên cứu, tăng nhanh đến đâu, ai đóng góp."),
    ("bien-dong", "Biến động", "Tăng trưởng đều hay giật cục theo tháng và theo năm."),
    ("tac-dong", "Tác động", "Các bài được trích dẫn ra sao trước và sau ChatGPT."),
    ("quan-he", "Quan hệ", "Quy mô của trường, đặc điểm bài báo và trích dẫn liên quan thế nào."),
    ("dia-ly", "Địa lý & hợp tác", "Nước nào dẫn đầu và hợp tác với ai."),
    ("chu-de", "Chủ đề", "Nghiên cứu nói về điều gì và chủ đề dịch chuyển ra sao."),
]
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫"


def vn(x, d=0):
    """Định dạng số kiểu Việt Nam: 23.712 và 3,8."""
    return f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def findings(i):
    """Ba phát hiện chính, phương pháp và giới hạn – dùng chung cho index.html và báo cáo PDF."""
    b = i["boot"]
    return {
        "headline": (f"Sau ChatGPT, nghiên cứu về AI trong giáo dục đại học bùng nổ gấp {vn(i['mult_2025_2022'])} lần, "
                     f"do châu Á dẫn dắt, và chuyển trọng tâm từ công cụ sang đạo đức và năng lực"),
        "f1": ("Xu hướng: gần như toàn bộ nghiên cứu ra đời sau ChatGPT",
               f"{vn(i['share_2023_on'], 1)}% trong {vn(i['api_count'])} bài xuất bản từ 2023 trở đi. Số bài tăng từ "
               f"{vn(i['count_2022'])} (2022) lên {vn(i['count_2025'])} (2025), tốc độ tăng kép mỗi năm từ "
               f"{i['cagr_2018_2022']}% (2018–2022) lên {i['cagr_2022_2025']}% (2022–2025). Mới đến 23/10, năm 2026 đã có "
               f"{vn(i['count_2026'])} bài, vượt cả năm 2025 (biểu đồ ①)."),
        "f2": ("Biến động: tăng vọt rồi chậm dần, chưa bão hoà",
               f"Tốc độ tăng đạt đỉnh +{vn(i['yoy']['2023'])}% năm 2023, rồi giảm còn +{vn(i['yoy']['2024'])}% và "
               f"+{vn(i['yoy']['2025'])}%; độ lệch chuẩn YoY {i['yoy_std']} điểm phần trăm cho thấy tăng trưởng rất không đều. "
               f"Tính theo tháng, trung bình trượt 3 tháng đi từ {i['rolling_2022_12']} bài (12/2022) lên {i['rolling_last']} "
               f"bài ({i['last_month']}) mà không có tháng nào đảo chiều kéo dài (biểu đồ ③ ④)."),
        "f3": ("Chủ đề và địa lý: từ công cụ sang đạo đức, châu Á vươn lên",
               f"Từ khoá phổ biến nhất chuyển từ '{i['top_first'][0]}' và '{i['top_first'][1]}' (2015–2020) sang "
               f"'{i['top_last'][0]}' ({vn(i['top_last_share'])}% bài 2025–2026); 'ChatGPT' giảm từ {vn(i['chatgpt_2324'])}% "
               f"(2023–2024) xuống {vn(i['chatgpt_last'])}%, còn 'academic integrity' lên {vn(i['integrity_last'])}% (biểu đồ ⑪ ⑫). "
               f"Châu Á tăng từ {vn(i['asia_2019'])}% lên {vn(i['asia_2026'])}% lượt tham gia, châu Âu giảm từ "
               f"{vn(i['europe_2019'])}% xuống {vn(i['europe_2026'])}%; Việt Nam từ {i['vn_2022']} bài (2022) lên "
               f"{i['vn_2025']} bài (2025), đứng thứ {i['vn_rank_2025']} (biểu đồ ② ⑨)."),
        "impact": (f"Bài từ 2023 được trích dẫn trung bình {vn(b['citations_per_year']['sau'], 1)} lần/năm so với "
                   f"{vn(b['citations_per_year']['truoc'], 1)} của bài trước 2023, nhưng khoảng cách này chủ yếu là độ trễ trích dẫn: "
                   f"khi so bằng FWCI (đã chuẩn hoá theo năm), trung bình là {vn(b['fwci']['sau'], 2)} so với "
                   f"{vn(b['fwci']['truoc'], 2)}, khoảng tin cậy bootstrap 95% của chênh lệch "
                   f"[{vn(b['fwci']['ci_low'], 2)}; {vn(b['fwci']['ci_high'], 2)}] chứa 0, tức không có bằng chứng bài mới kém tác động hơn (biểu đồ ⑤)."),
        "limits": (f"Dữ liệu chỉ là phần OpenAlex phân loại vào chủ đề 'AI in Education' (precision {i['precision']}% ± "
                   f"{vn(i['precision_margin'], 1)}% trên {i['precision_k']} bài ngẫu nhiên). {vn(i['missing_country'], 1)}% bài không có "
                   f"quốc gia và tỷ lệ này cao hơn ở bài cũ và bài không phải tiếng Anh, nên bản đồ thiên nhẹ về nước nói tiếng Anh; "
                   f"{vn(i['missing_lang'], 1)}% bài mới chưa được gán ngôn ngữ. Năm 2026 chưa đủ năm và bài mới chưa kịp được trích dẫn."),
        "meaning": ("Nghiên cứu về AI ở đại học không còn là câu hỏi 'có nên dùng công cụ không' mà đã chuyển sang 'dùng thế nào cho "
                    "đúng': liêm chính học thuật, năng lực AI, tư duy phản biện. Với các trường, đó là tín hiệu cần chính sách "
                    "và chương trình dạy năng lực AI, không chỉ cấp quyền dùng công cụ."),
        "method": (f"Nguồn: OpenAlex API, tải ngày {i['download_date']} bằng requests với cursor. Truy vấn: chủ đề T14414 "
                   f"(AI in Education), có 'higher education' hoặc 'university', article/review/conference-paper, 2015–2026. "
                   f"Đếm theo năm và quốc gia dùng group_by trên toàn bộ {vn(i['api_count'])} bài; phân tích chi tiết trên "
                   f"{vn(i['n_clean'])} bài đã khử trùng (lệch 0,7% so với API)."),
    }


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d2433;--muted:#5b6475;--line:#e3e5e8;--accent:#0072B2;--accent2:#E69F00}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 "Be Vietnam Pro","Segoe UI",system-ui,sans-serif}
header{background:var(--ink);color:#fff;padding:40px 16px 32px}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
header h1{font-size:clamp(24px,4vw,36px);line-height:1.2;margin:0 0 8px}
header p{margin:0;color:#c9cfda;max-width:760px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-top:24px}
.kpi{background:rgba(255,255,255,.08);border-radius:10px;padding:14px 16px}
.kpi b{display:block;font-size:30px;line-height:1.1}.kpi span{color:#c9cfda;font-size:14px}
nav{position:sticky;top:0;z-index:10;background:#fff;border-bottom:1px solid var(--line)}
nav .wrap{display:flex;gap:4px;overflow-x:auto;white-space:nowrap;padding:8px 16px}
nav a{color:var(--ink);text-decoration:none;padding:8px 12px;border-radius:8px;font-size:15px}
nav a:hover{background:#eef3f8;color:var(--accent)}
section{padding:36px 0 8px}
section h2{font-size:24px;margin:0 0 4px}section>.wrap>p.lead{color:var(--muted);margin:0 0 18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 12px 14px;margin-bottom:22px}
.card .num{color:var(--accent);font-weight:700;margin:4px 6px 0;font-size:14px}
.how{margin:6px 8px 0;color:var(--muted);font-size:14.5px}.how b{color:var(--ink)}
.insight{display:grid;gap:14px}
.find{background:var(--card);border-left:4px solid var(--accent);border-radius:8px;padding:14px 18px}
.find h3{margin:0 0 6px;font-size:18px}.find p{margin:0}
.note{background:#fff8ec;border-left-color:var(--accent2)}
footer{color:var(--muted);font-size:14px;padding:28px 0 40px}
@media (max-width:640px){.kpi b{font-size:24px}section h2{font-size:21px}}
"""


def figure_html(meta, include_js):
    fig = pio.read_json(FIG_DIR / meta["file"])
    fig.update_layout(title=None, autosize=True)
    div = fig.to_html(full_html=False, include_plotlyjs=include_js, default_width="100%",
                      config={"displaylogo": False, "responsive": True})
    return (f'<div class="card"><div class="num">Biểu đồ {CIRCLED[meta["num"] - 1]}</div>'
            f'<h3 style="margin:2px 6px 0;font-size:18px">{html.escape(meta["title"])}</h3>{div}'
            f'<p class="how"><b>Cách đọc:</b> {html.escape(meta["how"])}</p></div>')


def build():
    manifest = json.loads((FIG_DIR / "manifest.json").read_text(encoding="utf-8"))
    i, f = INSIGHTS, findings(INSIGHTS)
    first = True
    sections = []
    for sid, name, lead in SECTIONS:
        cards = []
        for meta in sorted((m for m in manifest if m["section"] == sid), key=lambda m: m["num"]):
            cards.append(figure_html(meta, include_js=first))
            first = False
        sections.append(f'<section id="{sid}"><div class="wrap"><h2>{name}</h2><p class="lead">{lead}</p>{"".join(cards)}</div></section>')

    finds = "".join(f'<div class="find"><h3>{html.escape(t)}</h3><p>{html.escape(x)}</p></div>' for t, x in (f["f1"], f["f2"], f["f3"]))
    insight = (f'<section id="insight"><div class="wrap"><h2>Insight</h2><p class="lead">{html.escape(f["headline"])}.</p>'
               f'<div class="insight">{finds}'
               f'<div class="find note"><h3>Về tác động</h3><p>{html.escape(f["impact"])}</p></div>'
               f'<div class="find note"><h3>Giới hạn</h3><p>{html.escape(f["limits"])}</p></div>'
               f'<div class="find"><h3>Ý nghĩa</h3><p>{html.escape(f["meaning"])}</p></div>'
               f'<div class="find note"><h3>Phương pháp và nguồn dữ liệu</h3><p>{html.escape(f["method"])}</p></div></div></div></section>')

    kpis = [
        (vn(i["api_count"]), "bài nghiên cứu, 2015–2026"),
        (f"×{vn(i['mult_2025_2022'])}", "số bài năm 2025 so với 2022 (trước ChatGPT)"),
        (vn(i["n_countries"]), "quốc gia có tác giả tham gia"),
    ]
    # Bản đồ ⑨ cần đường biên giới; Plotly mặc định tải từ cdn.plot.ly lúc mở trang, nên nhúng sẵn để chạy offline.
    topo = (ROOT / "assets/world_110m.json").read_text(encoding="utf-8")
    geo_assets = f"<script>window.PlotlyGeoAssets={{topojson:{{world_110m:{topo}}}}};</script>"
    nav = "".join(f'<a href="#{sid}">{name}</a>' for sid, name, _ in SECTIONS) + '<a href="#insight">Insight</a>'
    page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dạy và học AI tại các trường đại học</title><style>{CSS}</style>{geo_assets}</head>
<body>
<header><div class="wrap">
<h1>Dạy và học AI tại các trường đại học</h1>
<p>{html.escape(f["headline"])}. Dữ liệu OpenAlex tải ngày {i["download_date"]}.</p>
<div class="kpis">{"".join(f'<div class="kpi"><b>{v}</b><span>{t}</span></div>' for v, t in kpis)}</div>
</div></header>
<nav><div class="wrap">{nav}</div></nav>
{"".join(sections)}
{insight}
<footer><div class="wrap">Phạm Gia Khánh – &lt;MaSV&gt; · Bài giữa kỳ · Dữ liệu: OpenAlex (CC0) · Mọi biểu đồ có thể rê chuột, phóng to, bấm chú thích để ẩn/hiện.</div></footer>
</body></html>"""
    out = ROOT / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"Đã ghi {out} ({out.stat().st_size / 1e6:.1f} MB, {len(manifest)} biểu đồ)")


if __name__ == "__main__":
    build()
