# NCS 학습모듈 PDF 를 HTML 로 옮긴다 — 강사 PC 안에서만 쓴다.
#
# 만들어 두면 준비 교안 옆에 원문을 띄워 놓고 볼 수 있다.
# PDF 뷰어와 달리 글자를 찾을 수 있고, 인쇄 쪽이 아니라 학습내용 단위로 잘린다.
#
# ■ 이 결과물은 저장소에 올리지 않는다
#   학습모듈 유의사항 1 —
#     「NCS학습모듈은 교육훈련기관에서 출처를 명시하고 교육적 목적으로 활용할 수
#      있습니다. 다만 … 출처가 표기된 도표·사진·삽화·도면 등이 포함되어 있으므로,
#      이러한 저작물의 … 배포 및 공중 송신 … 에는 원작자의 동의를 받아야 합니다.」
#   강의실 안에서 보는 것은 「교육적 목적으로 활용」 이고, 올리는 순간 「공중 송신」
#   이 된다. 그래서 lm/ 을 .gitignore 에 둔다.
#
#   python tools/lm/pdf2html.py 2001020233_23v5
#   python tools/lm/pdf2html.py --all          응용SW 27개
#   python tools/lm/pdf2html.py --check        PDF 가 어디 있는지만 본다

import html
import json
import re
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parent.parent.parent      # COURSE-MANAGEMENT
BASE = ROOT.parent                                        # TMP_NCS_20260916
OUT = ROOT / "lm"
META = BASE / "NCS-CATALOG" / "data" / "learning-modules"

# 쪽 위아래 — 쪽번호를 걷어 낸다.
# 머리말(학습 1/학습 2 상자)은 학습내용 첫 쪽에만 있어 자리로 자르면 안 된다.
# 상자를 찾아서 그 구간만 버린다.
TOP, BOTTOM = 78.0, 782.0
머리끝 = 160.0
# 글꼴 크기로 가른다
SMALL = 9.3          # 출처 · 그림 캡션
BODY = 11.4          # 본문
ZOOM = 2.0           # 그림을 뽑을 때 확대율


def 색인():
    """assets/modules-pdf.js 가 적어 둔 PDF 자리를 읽는다."""
    s = (ROOT / "assets" / "modules-pdf.js").read_text(encoding="utf-8")
    s = s[s.index("{"):s.rindex("}") + 1]
    return json.loads(s)


def 겹침(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def 뭉치기(사각들, 틈=14.0):
    """가까이 놓인 그림 조각을 한 덩이로 묶는다."""
    남 = list(사각들)
    덩이 = []
    while 남:
        x0, y0, x1, y1 = 남.pop()
        바뀜 = True
        while 바뀜:
            바뀜 = False
            for i in range(len(남) - 1, -1, -1):
                a = 남[i]
                if (a[0] - 틈 < x1 and a[2] + 틈 > x0
                        and a[1] - 틈 < y1 and a[3] + 틈 > y0):
                    x0, y0 = min(x0, a[0]), min(y0, a[1])
                    x1, y1 = max(x1, a[2]), max(y1, a[3])
                    남.pop(i)
                    바뀜 = True
        덩이.append((x0, y0, x1, y1))
    return 덩이


def 그림자리(쪽, 표사각, 글줄):
    """넣은 그림과 그려 넣은 도형에서 그림 덩이를 찾는다.

    본문 줄을 품은 덩이는 그림이 아니다 — 쪽 전체를 삼키는 것을 막는다.
    """
    안쪽 = [l for l in 글줄 if TOP < l[1] < BOTTOM]
    바닥 = max([m[3] for m in 표사각 if m[0] == 0] or [TOP])

    def 글을품나(c):
        for x0, y0, x1, y1 in 안쪽:
            if c[0] - 2 < (x0 + x1) / 2 < c[2] + 2 and c[1] - 2 < (y0 + y1) / 2 < c[3] + 2:
                return True
        return False

    덩이 = []
    # 넣은 그림은 그대로 그림이다
    넣은 = [tuple(i["bbox"]) for i in 쪽.get_image_info()]
    # 그려 넣은 도형은 뭉쳐 보고 글이 없는 것만 고른다
    조각 = []
    for d in 쪽.get_drawings():
        r = d["rect"]
        if r.width < 8 or r.height < 8 or r.width > 480:
            continue
        조각.append((r.x0, r.y0, r.x1, r.y1))
    for c in 넣은 + 뭉치기(조각, 8.0):
        if c[3] < 바닥 or c[1] > BOTTOM:
            continue
        if (c[2] - c[0]) < 70 or (c[3] - c[1]) < 45:
            continue
        if any(겹침(c, t) for t in 표사각):
            continue
        if c not in 넣은 and 글을품나(c):
            continue
        if any(겹침(c, e) for e in 덩이):
            continue
        덩이.append(c)
    return 덩이


def 문단만들기(줄들, 오른끝):
    """줄을 문단으로 잇는다.

    PDF 는 문단 안에서만 줄을 강제로 접는다. 그래서 앞줄이 오른쪽 끝까지
    차 있을 때만 잇는다. 일찍 끝난 줄은 글쓴이가 끊은 자리다.
    """
    나온 = []
    쌓임 = None
    for 크기, 글꼴, x0, x1, y0, 글 in 줄들:
        갈래 = "h" if 크기 >= BODY else ("s" if 크기 <= SMALL else "p")
        이을까 = (쌓임 and 쌓임["갈래"] == "p" == 갈래
                  and abs(쌓임["x0"] - x0) < 3.0
                  and 0 <= y0 - 쌓임["y1"] < 26
                  and 쌓임["x1"] > 오른끝 - 14)
        if 이을까:
            쌓임["글"] += 글
            쌓임["y1"], 쌓임["x1"] = y0, x1
            continue
        if 쌓임:
            나온.append(쌓임)
        쌓임 = {"갈래": 갈래, "크기": 크기, "글꼴": 글꼴, "x0": x0, "x1": x1,
                "y0": y0, "y1": y0, "글": 글}
    if 쌓임:
        나온.append(쌓임)
    return 나온


def 표HTML(표):
    줄 = ['<table class="lmt">']
    for i, 행 in enumerate(표.extract()):
        칸 = "th" if i == 0 else "td"
        줄.append("  <tr>" + "".join(
            f"<{칸}>{html.escape((c or '').strip())}</{칸}>" for c in 행) + "</tr>")
    줄.append("</table>")
    return "\n".join(줄)


def 전폭괘선(쪽):
    """쪽을 가로지르는 가는 선의 y 값. 표의 위아래 테두리다."""
    y = set()
    for d in 쪽.get_drawings():
        r = d["rect"]
        if r.y1 - r.y0 < 3 and r.x1 - r.x0 > 300 and r.y0 > 머리끝:
            y.add(round(r.y0, 1))
    return sorted(y)


def 한쪽(쪽, 번호, 그림칸):
    괘선 = 전폭괘선(쪽)
    표들, 표그림, 머리 = [], [], []
    for t in 쪽.find_tables().tables:
        if t.bbox[1] < 머리끝:                 # 학습 1 / 학습 2 머리말 상자
            머리.append((0, 0, 999, t.bbox[3] + 2))
            continue
        아래 = [y for y in 괘선 if y > t.bbox[3] + 2]
        # 머리 밴드만 잡히고 본체가 병합 셀이면 그 구간을 통째로 그림으로 뜬다
        if 아래 and 아래[0] - t.bbox[3] > 20:
            표그림.append((t.bbox[0], t.bbox[1], t.bbox[2], 아래[0] + 2))
        else:
            표들.append(t)
    표사각 = [t.bbox for t in 표들] + 표그림 + 머리
    모든줄 = [l["bbox"] for b in 쪽.get_text("dict")["blocks"] if b["type"] == 0
              for l in b["lines"] if "".join(s["text"] for s in l["spans"]).strip()]
    그림 = 그림자리(쪽, 표사각, 모든줄)
    그림 = [c for c in 그림 if not any(겹침(c, r) for r in 표그림)]

    조각 = []
    for b in 쪽.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            bb = l["bbox"]
            if bb[3] < TOP or bb[1] > BOTTOM:
                continue
            if any(겹침(bb, r) for r in 표사각 + 그림):
                continue
            글 = "".join(s["text"] for s in l["spans"])
            if not 글.strip():
                continue
            s0 = l["spans"][0]
            밑선 = s0.get("origin", (0, bb[3]))[1]
            조각.append((round(s0["size"], 1), s0["font"], bb[0], bb[2], bb[1], 글, 밑선))
    조각.sort(key=lambda r: (round(r[6] / 4), r[2]))

    # 같은 줄에 흩어진 조각을 하나로 —「1-1.」과「운영체제 식별」이 한 줄이다
    줄들 = []
    for 것 in 조각:
        if 줄들 and abs(줄들[-1][6] - 것[6]) < 4.0:
            앞 = 줄들[-1]
            사이 = " " if 것[2] - 앞[3] > 4 else ""
            줄들[-1] = (max(앞[0], 것[0]), 앞[1], 앞[2], 것[3], 앞[4],
                        앞[5].rstrip() + 사이 + 것[5], 앞[6])
        else:
            줄들.append(것)
    줄들.sort(key=lambda r: r[6])
    줄들 = [(a, b2, c, d, e, f) for a, b2, c, d, e, f, _ in 줄들]
    오른끝 = max((l[3] for l in 줄들), default=0)

    items = [(m["y0"], "글", m) for m in 문단만들기(줄들, 오른끝)]
    items += [(t.bbox[1], "표", t) for t in 표들]
    for k, c in enumerate(그림 + 표그림, 1):
        items.append((c[1], "그림", (c, k)))
    items.sort(key=lambda r: r[0])

    나온 = [f'<div class="lmp" id="p{번호}"><span class="lmn">{번호}</span>']
    for _, 갈래, 것 in items:
        if 갈래 == "표":
            나온.append(표HTML(것))
        elif 갈래 == "그림":
            사각, k = 것
            이름 = f"p{번호:03d}_{k}.png"
            pix = 쪽.get_pixmap(clip=fitz.Rect(*사각),
                                matrix=fitz.Matrix(ZOOM, ZOOM))
            pix.save(그림칸 / 이름)
            나온.append(f'<p class="lmf"><img src="img/{이름}" alt="{번호}쪽 그림 {k}"></p>')
        else:
            글 = 것["글"].strip(" 	")
            글 = 글.lstrip("숔◇▣□■▪●○").strip(" 	")
            글 = 글.strip("/").strip(" 	")
            if not 글 or 글 in ("/", "·", "\\"):
                continue
            글 = html.escape(글)
            if 것["갈래"] == "h":
                단 = "lmh1" if 것["크기"] >= 18 else "lmh2"
                나온.append(f'<p class="{단}">{글}</p>')
            elif 것["갈래"] == "s":
                나온.append(f'<p class="lms">{글}</p>')
            else:
                나온.append(f"<p>{글}</p>")
    나온.append("</div>")
    return "\n".join(나온)


CSS = """<style>
  body{margin:0;font:15px/1.9 "맑은 고딕","Malgun Gothic",sans-serif;color:#111;background:#fff}
  .wrap{max-width:900px;margin:0 auto;padding:0 20px 80px}
  h1{font-size:20px;margin:26px 0 4px}
  .sub{color:#555;font-size:12.5px;margin:0 0 6px}
  .note{border:1px solid #000;padding:10px 12px;font-size:12.5px;margin:14px 0 24px;background:#fafafa}
  nav.toc{border-top:2px solid #000;border-bottom:1px solid #000;padding:12px 0;margin:0 0 26px}
  nav.toc b{display:block;font-size:13px;margin:8px 0 3px}
  nav.toc a{display:inline-block;color:#000;font-size:12.5px;margin:0 14px 3px 0}
  .lmp{border-top:1px solid #e4e4e4;padding:22px 0 4px;position:relative}
  .lmn{position:absolute;right:-46px;top:22px;color:#aaa;font-size:11px}
  .lmp p{margin:0 0 11px}
  .lmh1{font-size:19px;font-weight:700;margin:26px 0 10px}
  .lmh2{font-size:15px;font-weight:700;margin:20px 0 8px}
  .lms{font-size:12px;color:#666}
  .lmf{text-align:center}
  .lmf img{max-width:100%;border:1px solid #ddd}
  table.lmt{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}
  table.lmt th,table.lmt td{border:1px solid #999;padding:5px 7px;vertical-align:top}
  table.lmt th{background:#f2f2f2;text-align:left}
  @media print{.lmn{display:none}}
</style>"""


def 목차(뜻):
    if not 뜻:
        return ""
    앞 = 뜻.get("front", 0)
    줄 = ['<nav class="toc">']
    for e in 뜻["elements"]:
        줄.append(f"  <b>요소 {e['no']} {html.escape(e['name'])}</b>")
        for c in e["contents"]:
            p = c.get("printed")
            if p is None:
                continue
            줄.append(f'  <a href="#p{p + 앞}">{c["no"]} {html.escape(c["title"])}'
                      f" <span style=\"color:#888\">{p}쪽</span></a>")
    줄.append("</nav>")
    return "\n".join(줄)


def 만들기(코드, 색):
    it = 색.get(코드)
    if not it:
        print(f"  ✗ {코드}  색인에 없습니다")
        return False
    pdf = BASE.joinpath(*it["p"])
    if not pdf.exists():
        print(f"  ✗ {코드}  PDF 가 없습니다 — {pdf}")
        return False
    뜻 = {}
    j = META / f"{코드}.json"
    if j.exists():
        뜻 = json.loads(j.read_text(encoding="utf-8"))

    칸 = OUT / 코드
    (칸 / "img").mkdir(parents=True, exist_ok=True)
    for old in (칸 / "img").glob("*.png"):
        old.unlink()

    d = fitz.open(pdf)
    앞 = 뜻.get("front", 0)
    쪽들 = [한쪽(d[i], i + 1, 칸 / "img") for i in range(앞, d.page_count)]
    이름 = 뜻.get("name", 코드)
    본 = [
        '<meta charset="utf-8">',
        f"<title>{html.escape(이름)} — NCS 학습모듈 원문</title>",
        CSS, '<div class="wrap">',
        f"<h1>{html.escape(이름)}</h1>",
        f'<p class="sub">NCS 학습모듈 <code>{코드}</code> · 원문 {d.page_count}쪽 '
        f"· 앞표지 {앞}장을 뺀 {d.page_count - 앞}쪽</p>",
        '<div class="note">한국직업능력연구원 저작물(공공누리 제2유형 · 출처표시 · 상업적 이용 금지)을 '
        "교육 목적으로 옮긴 것입니다. 도표·사진·삽화·도면 가운데 출처가 표기된 것은 "
        "국가가 저작재산권을 갖지 않으므로, <b>이 문서를 강의실 밖으로 내보내거나 "
        "인터넷에 올리지 마십시오.</b></div>",
        목차(뜻), "\n".join(쪽들), "</div>",
    ]
    (칸 / "index.html").write_text("\n".join(본), encoding="utf-8")
    그림수 = len(list((칸 / "img").glob("*.png")))
    print(f"  ✓ {코드}  {이름}  {d.page_count - 앞}쪽 · 그림 {그림수}장 → lm/{코드}/index.html")
    return True


def main():
    색 = 색인()
    인자 = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--check" in sys.argv:
        for k, v in sorted(색.items()):
            p = BASE.joinpath(*v["p"])
            print(f"  {'있음' if p.exists() else '없음'}  {k}  {v['n']}")
        return
    if "--all" in sys.argv:
        인자 = sorted(색)
    if not 인자:
        print(__doc__ or "python tools/lm/pdf2html.py <능력단위코드>")
        return
    OUT.mkdir(exist_ok=True)
    (OUT / ".gitignore").write_text("*\n", encoding="utf-8")
    됨 = sum(만들기(c, 색) for c in 인자)
    print(f"\n{됨}/{len(인자)} 건")


main()
