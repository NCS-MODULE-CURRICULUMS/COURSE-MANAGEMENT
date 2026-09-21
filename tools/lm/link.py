# 준비 교안의 「근거」 칸을 원문 HTML 로 잇는다.
#
# 교안 aside 에 이렇게 적혀 있다.
#     <b class="sh">근거</b>
#     <p class="v">학습모듈 1-2 · 기본 명령어</p>
# 이 「1-2」 를 lm/<코드>/index.html#p24 로 보낸다.
# 쪽 번호는 NCS-CATALOG 의 printed 에 앞표지 장수를 더해 얻는다.
#
# lm/ 이 없는 PC 에서는 링크가 죽으므로 원문 쪽만 글자로 남긴다.
#
#   python tools/lm/link.py m19 2001020233_23v5
#   python tools/lm/link.py --check m19 2001020233_23v5

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
META = ROOT.parent / "NCS-CATALOG" / "data" / "learning-modules"


def 쪽표(코드):
    """학습내용 번호 → (PDF 쪽, 인쇄 쪽, 끝 인쇄 쪽, 제목)"""
    d = json.loads((META / f"{코드}.json").read_text(encoding="utf-8"))
    앞 = d.get("front", 0)
    차례 = []
    for e in d["elements"]:
        for c in e["contents"]:
            if c.get("printed") is not None:
                차례.append([c["no"], c["printed"], None, c["title"]])
    for i in range(len(차례) - 1):
        차례[i][2] = 차례[i + 1][1] - 1
    if 차례:
        차례[-1][2] = d.get("pages", 0) - 앞
    return {n: (p + 앞, p, 끝, t) for n, p, 끝, t in 차례}, d


def main():
    보기만 = "--check" in sys.argv
    인자 = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(인자) != 2:
        print("python tools/lm/link.py <교안> <능력단위코드>")
        return
    교안, 코드 = 인자
    표, 뜻 = 쪽표(코드)
    쪽 = ROOT / "guides" / f"{교안}.html"
    s = 쪽.read_text(encoding="utf-8")
    있음 = (ROOT / "lm" / 코드 / "index.html").exists()
    센 = [0, 0]

    def 잇기(m):
        전체, 번호, 꼬리 = m.group(0), m.group(1), m.group(2)
        it = 표.get(번호)
        if not it:
            센[1] += 1
            return 전체
        센[0] += 1
        pdf쪽, 인쇄, 끝, 제목 = it
        쪽말 = f"원문 {인쇄}~{끝}쪽"
        if 있음:
            고리 = (f'<a class="lmlink" href="../lm/{코드}/index.html#p{pdf쪽}" '
                    f'target="_blank" title="{html.escape(제목)}">'
                    f"학습모듈 {번호}</a>")
        else:
            고리 = f"학습모듈 {번호}"
        return f'<p class="v">{고리}{꼬리}<span class="lmpg">{쪽말}</span>'

    새 = re.sub(r'<p class="v">학습모듈 (\d+-\d+)((?:[^<]*))', 잇기, s)

    # 링크 꼴 — 한 번만 넣는다
    CSS = ("  a.lmlink{color:#000}\n"
           "  .lmpg{display:block;font-size:10.5px;color:#888;margin-top:2px}\n")
    if "a.lmlink" not in 새:
        새 = 새.replace("</style>", CSS + "</style>", 1)

    print(f"{교안}  이은 것 {센[0]}곳 · 표에 없는 번호 {센[1]}곳 · "
          f"원문 HTML {'있음' if 있음 else '없음'}")
    if not 보기만:
        쪽.write_bytes(새.encode("utf-8"))
        print("  저장했습니다")


main()
