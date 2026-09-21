# 교안 본문의 강조 버릇을 덜어 낸다.
#
#   python plain.py m21            보기만 한다 (몇 군데 고칠지)
#   python plain.py m21 --fix      고친다
#
# 고치는 것은 설명하는 산문뿐이다.
#   · <p> 안의 " " 같은 홑화살괄호 강조를 없애고 글자는 남긴다
#   · <p> 안에 <b> 가 둘 이상이면 첫 번째만 남긴다
#
# 손대지 않는 것
#   · <pre> · <p class="cmdline"> · <code> 안 — 명령과 화면은 그대로
#   · <table> 안 — 표의 강조는 대조를 보이는 것이라 남긴다
#   · note · warn 상자 안 — 상자는 사람이 판단한다
#   · 제목과 aside
#   · 「제출물」 「스스로 확인」 「목적」 줄

import re
import sys
from pathlib import Path

GUIDES = Path(__file__).resolve().parent.parent.parent / "guides"

KEEP = ("<b>제출물</b>", "<b>스스로 확인</b>", "<b>목적</b>")

건드리지_않을_패턴 = (
    r"<pre>.*?</pre>",
    r'<p class="cmdline">.*?</p>',
    r"<table.*?</table>",
    r'<div class="note">.*?</div>',
    r'<div class="warn">.*?</div>',
    r"<code>.*?</code>",
    r"<h[1-6][^>]*>.*?</h[1-6]>",
    r'<aside class="side">.*?</aside>',
)

조사 = ("만", "뿐", "까지", "부터", "조차", "마저", "처럼", "보다", "이나", "나마")


def 보호구간(s):
    구간 = []
    for p in 건드리지_않을_패턴:
        for m in re.finditer(p, s, re.S):
            구간.append((m.start(), m.end()))
    return 구간


def 안전한가(a, b, 구간):
    return not any(시작 <= a and b <= 끝 for 시작, 끝 in 구간)


def 띄어쓰기_손질(s):
    """강조를 걷어내며 벌어진 자리를 붙인다."""
    for 조 in 조사:
        s = s.replace(" " + 조 + " ", 조 + " ")
        s = s.replace(" " + 조 + ".", 조 + ".")
        s = s.replace(" " + 조 + ",", 조 + ",")
    while "  " in s:
        s = s.replace("  ", " ")
    return s


def 다듬기(s):
    구간 = 보호구간(s)
    고침 = {"강조": 0, "굵게": 0}

    # ① 홑화살괄호 강조를 없앤다 — 안쪽 글자는 남긴다
    조각, 끝 = [], 0
    for m in re.finditer("«([^»]{1,60})»", s):
        if not 안전한가(m.start(), m.end(), 구간):
            continue
        조각.append(s[끝:m.start()])
        조각.append(m.group(1))
        끝 = m.end()
        고침["강조"] += 1
    조각.append(s[끝:])
    s = "".join(조각)

    # ② 한 문단에 <b> 가 둘 이상이면 첫 번째만 남긴다
    구간 = 보호구간(s)

    def 문단(m):
        원본 = m.group(0)
        if any(k in 원본 for k in KEEP):
            return 원본
        if not 안전한가(m.start(), m.end(), 구간):
            return 원본
        굵은 = [b for b in re.finditer(r"<b>(.*?)</b>", 원본, re.S)
                if 안전한가(m.start() + b.start(), m.start() + b.end(), 구간)]
        if len(굵은) <= 1:
            return 원본
        새, 끝 = [], 0
        for i, b in enumerate(굵은):
            새.append(원본[끝:b.start()])
            새.append(b.group(0) if i == 0 else b.group(1))
            끝 = b.end()
            if i:
                고침["굵게"] += 1
        새.append(원본[끝:])
        return 띄어쓰기_손질("".join(새))

    s = re.sub(r"<p>.*?</p>", 문단, s, flags=re.S)
    return s, 고침


def main(argv):
    if not argv:
        raise SystemExit("교안을 적어 주십시오 — 보기: python plain.py m21")
    mod = argv[0]
    고칠까 = "--fix" in argv
    p = GUIDES / f"{mod}.html"
    s = p.read_text(encoding="utf-8")
    새, 고침 = 다듬기(s)
    print(f"{p.name}  강조 {고침['강조']}군데 · 겹친 굵은 글씨 {고침['굵게']}군데")
    if 고칠까:
        p.write_text(새, encoding="utf-8")
        print(f"고쳤습니다 — {len(s):,} -> {len(새):,}자")
    else:
        print("보기만 했습니다. 고치려면 --fix 를 붙이십시오")


main(sys.argv[1:])
