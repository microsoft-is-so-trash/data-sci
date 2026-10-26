"""Ghép 16 biểu đồ Plotly (data/processed/figs/*.json) thành một trang index.html tĩnh.

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
    ("viet-nam", "Việt Nam", "Dạy và học AI tại Việt Nam so với thế giới và 5 nước tham chiếu."),
]
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯"
STUDENT = "Phạm Gia Khánh – B25DCTN064"


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


def vn_findings(i):
    """Phần Việt Nam so với thế giới: mở đầu, kết luận và hạn chế – dùng chung cho index.html và báo cáo PDF."""
    v = i["vn"]
    cp, nm, th, p = v["compare"], v["names"], v["themes"], v["per1000"]
    y, g = v["by_year"], v["cagr_2023_2025"]
    pct = lambda x, d=0: f"{vn(x, d)}%"
    partners = ", ".join(f"{name} ({k})" for name, k in
                         ((("Úc" if c == "AU" else "Anh" if c == "GB" else nm.get(c, c)), k) for c, k in v["partners"][:2]))
    sig = sorted(((t, r) for t, r in th.items() if r["co_y_nghia"]), key=lambda x: x[1]["the_gioi_%"] - x[1]["viet_nam_%"])
    sig_txt = "; ".join(f"'{t}' {pct(r['viet_nam_%'])} so với {pct(r['the_gioi_%'])}" for t, r in sig)
    about = th["Học về AI (năng lực, chương trình)"]
    lift = v["lift_top"][0]
    top = v["top_inst"]
    slower = [nm[c] for c in ("TH", "MY", "ID", "CN", "US") if g[c] < g["VN"]]
    pace = ("cao hơn thế giới" + (f" và cả {len(slower)} nước tham chiếu" if len(slower) == 5 else f" và {', '.join(slower)}" if slower else "")
            if g["VN"] > g["WORLD"] else "không cao hơn thế giới")
    ci = lambda c: (cp[c]["fwci_ci_low"], cp[c]["fwci_ci_high"])
    above = [nm[c] for c in ("TH", "MY", "ID", "CN", "US") if ci(c)[1] < ci("VN")[0]]
    below = [nm[c] for c in ("TH", "MY", "ID", "CN", "US") if ci(c)[0] > ci("VN")[1]]
    sep = " ".join(x for x in (f"Khoảng của Việt Nam nằm hẳn dưới {', '.join(below)}." if below else "",
                               f"Khoảng của Việt Nam nằm hẳn trên {', '.join(above)}." if above else "") if x)
    return {
        "intro": (f"Trong {vn(i['n_clean'])} bài, {v['n']} bài có ít nhất một tác giả ở Việt Nam, tức {vn(v['per1000_all'], 1)} bài trên mỗi 1.000 bài. "
                  f"Phần này so Việt Nam với thế giới và 5 nước tham chiếu (Thái Lan, Malaysia, Indonesia, Trung Quốc, Hoa Kỳ) bằng các số đã chuẩn hoá: "
                  f"‰ số bài thế giới, % số bài của mỗi nước và FWCI. Bộ lọc con 'học về AI' tách các bài coi AI là nội dung cần dạy và học "
                  f"(AI literacy, năng lực AI, chương trình và kỹ năng AI, tư duy tính toán) khỏi các bài dùng AI làm công cụ dạy học. Một bài được gắn nhãn "
                  f"khi có từ khoá OpenAlex hoặc tiêu đề khớp các cụm này; kết quả là {vn(v['about_ai_n'])} bài ({pct(v['about_ai_world'], 1)} toàn bộ)."),
        "k": [
            ("Quy mô: nhỏ nhưng tăng nhanh hơn thế giới",
             f"Số bài của Việt Nam tăng từ {y['2023']} (2023) lên {y['2024']} (2024) và {y['2025']} (2025); riêng 10 tháng 2026 đã có {y['2026']} bài. "
             f"Tốc độ tăng kép 2023–2025 là {g['VN']}%/năm, {pace} (thế giới {g['WORLD']}%). Tỷ trọng tăng từ "
             f"{vn(p['VN']['2023'], 1)}‰ lên {vn(p['VN']['2026'], 1)}‰ số bài thế giới, hạng từ {v['rank']['2023']} lên {v['rank']['2026']}. "
             f"Dù vậy quy mô vẫn gần Thái Lan ({vn(p['TH']['2026'], 1)}‰), còn Indonesia ({vn(p['ID']['2026'], 1)}‰) gấp {vn(p['ID']['2026'] / p['VN']['2026'], 1)} lần. "
             f"Mức tăng phần trăm cao một phần là do xuất phát từ nền rất thấp ({y['2023']} bài năm 2023)."),
            ("Hợp tác quốc tế: ngang thế giới, thấp so với khu vực",
             f"{pct(cp['VN']['hop_tac_quoc_te_%'])} số bài Việt Nam ({v['n_intl']} bài) có tác giả ở nước khác, gần mức thế giới "
             f"({pct(cp['WORLD']['hop_tac_quoc_te_%'])}). Tỷ lệ này ở Thái Lan ({pct(cp['TH']['hop_tac_quoc_te_%'])}) và Malaysia "
             f"({pct(cp['MY']['hop_tac_quoc_te_%'])}) cao gấp {vn(cp['TH']['hop_tac_quoc_te_%'] / cp['VN']['hop_tac_quoc_te_%'], 1)} và "
             f"{vn(cp['MY']['hop_tac_quoc_te_%'] / cp['VN']['hop_tac_quoc_te_%'], 1)} lần. Đối tác thường gặp nhất là {partners}."),
            ("Tác động trích dẫn: chưa khác thế giới",
             f"FWCI trung bình của bài Việt Nam là {vn(cp['VN']['fwci_tb'], 2)} (khoảng tin cậy bootstrap 95%: {vn(cp['VN']['fwci_ci_low'], 2)}–"
             f"{vn(cp['VN']['fwci_ci_high'], 2)}). Khoảng này chồng lên khoảng của thế giới ({vn(cp['WORLD']['fwci_ci_low'], 2)}–"
             f"{vn(cp['WORLD']['fwci_ci_high'], 2)}), nên chưa có bằng chứng bài Việt Nam được trích dẫn nhiều hay ít hơn mặt bằng chung. "
             f"{sep}"),
            ("Chủ đề: thiên về dùng AI tạo sinh trong dạy tiếng Anh",
             f"So với thế giới, bài Việt Nam có tỷ lệ cao hơn rõ rệt ở {sig_txt} (kiểm định z hai tỷ lệ giữa Việt Nam và phần còn lại, p < 0,05). "
             f"Từ khoá đặc trưng nhất là '{lift[0]}' ({pct(lift[2], 1)} bài Việt Nam, so với {pct(lift[3], 1)} thế giới), tiếp theo là "
             f"{', '.join(repr(k[0]) for k in v['lift_top'][1:4])}. "
             f"Ngược lại, nhóm 'học về AI' chiếm {pct(about['viet_nam_%'], 1)} so với {pct(about['the_gioi_%'], 1)} thế giới, nhưng khác biệt "
             f"chưa có ý nghĩa thống kê (p = {vn(about['p_value'], 2)}). Như vậy nghiên cứu ở Việt Nam tập trung vào việc dùng AI để dạy và học hơn là dạy về AI."),
            ("Trường đại học: hai đơn vị dẫn đầu, phần còn lại phân tán",
             f"{v['n_inst']} trường/viện Việt Nam có ít nhất một bài. Dẫn đầu là {top[0][0]} ({top[0][1]} bài), {top[1][0]} ({top[1][1]}) và "
             f"{top[2][0]} ({top[2][1]}); ba đơn vị này cùng góp mặt trong {pct(v['top3_share'])} số bài, phần còn lại rải ở {v['n_inst'] - 3} đơn vị, "
             f"phần lớn chỉ có vài bài."),
        ],
        "limits": (f"Mẫu Việt Nam nhỏ ({v['n']} bài), nên mọi tỷ lệ có sai số lớn. Precision của truy vấn chỉ đo được trên toàn bộ dữ liệu: "
                   f"mẫu 100 bài ngẫu nhiên chỉ có {v['prec_k']} bài Việt Nam ({v['prec_ok']}/{v['prec_k']} đúng), quá ít để ước lượng riêng. "
                   f"Bộ lọc 'học về AI' dựa trên quy tắc từ khoá và chưa được chấm tay; {pct(v['about_ai_explicit'])} số bài được gắn nhãn có nhắc trực tiếp các cụm này "
                   f"trong tiêu đề hoặc tóm tắt (so với {pct(v['about_ai_explicit_rest'])} ở nhóm còn lại), đây là kiểm tra nhất quán chứ chưa phải precision. "
                   f"Độ phủ tiếng Việt thấp: {v['lang'].get('thiếu nhãn', 0)} bài chưa có nhãn ngôn ngữ, chỉ {v['lang'].get('vi', 0)} bài gắn nhãn tiếng Việt "
                   f"(một số bị gán nhầm) và {v['lang'].get('ang', 0)} bài bị gán nhầm là tiếng Anh cổ. Bài đăng ở tạp chí trong nước có thể không được OpenAlex "
                   f"lập chỉ mục hoặc không được xếp vào chủ đề này, nên số của Việt Nam nhiều khả năng bị đếm thiếu. Trường được đếm theo ID của OpenAlex, "
                   f"chưa gộp trường thành viên vào đại học mẹ."),
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
.tbl{width:100%;border-collapse:collapse;font-size:14.5px;background:var(--card)}
.tbl td,.tbl th{border-bottom:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
.tbl th{background:#eef3f8}.tbl td.v{text-align:right;white-space:nowrap}.tbl td.g{color:var(--muted);font-weight:600}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;align-items:start}
.steps{margin:0;padding-left:20px}.steps li{margin-bottom:6px}
@media (max-width:640px){.kpi b{font-size:24px}section h2{font-size:21px}}
"""


def data_section(i):
    """Mục 'Dữ liệu & xử lý': quy mô dữ liệu qua từng bước (data_volume.csv) và các bước làm sạch, biến đổi."""
    rows, last = [], None
    for r in i["volume"]:
        v = r["giá trị"]
        v = vn(v, 0 if float(v).is_integer() else 2 if abs(v) < 1 else 1) if isinstance(v, (int, float)) else v
        rows.append(f'<tr><td class="g">{html.escape(r["nhóm"] if r["nhóm"] != last else "")}</td>'
                    f'<td>{html.escape(r["chỉ số"])}</td><td class="v">{html.escape(str(v))}</td></tr>')
        last = r["nhóm"]
    steps = [
        ("Thu thập", "OpenAlex API (API mở) gọi bằng requests trong collect_openalex.py, phân trang cursor 200 bài/trang; số theo năm và quốc gia đếm bằng group_by trên toàn bộ kết quả."),
        ("Chuẩn hoá kiểu", "Năm → int16, ngày → datetime, loại tài liệu → category, trích dẫn → int32, truy cập mở → bool; DOI chữ thường; mã quốc gia ISO-2 → ISO-3 (pycountry); tóm tắt ghép lại từ inverted index."),
        ("Trùng lặp", f"Loại 154 dòng trùng ID do phân trang cursor và 5 bài trùng DOI (giữ bản nhiều trích dẫn hơn); lệch so với số API {vn(100 * (i['api_count'] - i['n_clean']) / i['api_count'], 1)}%."),
        ("Dữ liệu thiếu", "Thiếu nhãn ngôn ngữ dồn vào bài mới (MAR) nên không dùng để lọc; thiếu tóm tắt và quốc gia được giữ lại, loại theo từng phân tích (pairwise deletion) và ghi vào phần giới hạn; ngày ghi 01-01 coi là chỉ có năm, bỏ khỏi chuỗi theo tháng."),
        ("Đặc trưng mới", "log_cit = log(1 + trích dẫn), citations_per_year, n_countries, n_institutions, is_international, period (trước/sau 2023), continent, cùng YoY, CAGR, trung bình trượt 3 tháng và nhãn 'học về AI'."),
    ]
    steps_html = "".join(f"<li><b>{html.escape(t)}:</b> {html.escape(x)}</li>" for t, x in steps)
    return (f'<section id="du-lieu"><div class="wrap"><h2>Dữ liệu &amp; xử lý</h2>'
            f'<p class="lead">Dữ liệu đi từ API đến bảng phân tích thế nào, và còn thiếu gì.</p>'
            f'<div class="cols"><table class="tbl"><tr><th>Nhóm</th><th>Chỉ số</th><th style="text-align:right">Giá trị</th></tr>{"".join(rows)}</table>'
            f'<div class="find"><h3>Các bước xử lý</h3><ul class="steps">{steps_html}</ul></div></div></div></section>')


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
        if sid == "viet-nam":
            vf = vn_findings(i)
            cards.append(f'<div class="insight"><div class="find"><h3>Phạm vi và bộ lọc</h3><p>{html.escape(vf["intro"])}</p></div>'
                         + "".join(f'<div class="find"><h3>{html.escape(t)}</h3><p>{html.escape(x)}</p></div>' for t, x in vf["k"])
                         + f'<div class="find note"><h3>Hạn chế của phần Việt Nam</h3><p>{html.escape(vf["limits"])}</p></div></div>')
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
    nav = ('<a href="#du-lieu">Dữ liệu</a>' + "".join(f'<a href="#{sid}">{name}</a>' for sid, name, _ in SECTIONS)
           + '<a href="#insight">Insight</a>')
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
{data_section(i)}
{"".join(sections)}
{insight}
<footer><div class="wrap">{STUDENT} · Bài giữa kỳ · Dữ liệu: OpenAlex (CC0) · Mọi biểu đồ có thể rê chuột, phóng to, bấm chú thích để ẩn/hiện.</div></footer>
</body></html>"""
    out = ROOT / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"Đã ghi {out} ({out.stat().st_size / 1e6:.1f} MB, {len(manifest)} biểu đồ)")


if __name__ == "__main__":
    build()
