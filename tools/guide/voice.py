# 「교재처럼 읽히는가」 를 기계로 훑는다.
#
# plain.py 는 «서식» 을 본다 — 강조 태그가 겹쳤는가.
# 이 도구는 «문체» 를 본다. 지금까지 사람이 눈으로 잡던 것들이다.
#
#   1 겹낫표   «» 강조를 산문에서 몇 번 썼는가
#   2 줄표     — 로 문장을 이어 붙인 곳
#   3 굵기     한 문단에 굵은 글씨가 둘 이상인 곳
#   4 상자     한 실습에 note/warn 이 둘을 넘는 곳
#   5 어미     문장이 전부 같은 말로 끝나는가
#   6 대조문   「A 가 아니라 B」 를 한 덩이에서 되풀이하는가
#   7 판박이   문단이 전부 같은 길이·같은 짜임인가
#   8 되풀이   같은 문장을 여러 곳에 그대로 옮겨 놓았는가
#
# 표·명령 화면·실측값은 세지 않는다. 세는 것은 «설명하는 산문» 뿐이다.
#
#   python tools/guide/voice.py            교안 전부
#   python tools/guide/voice.py m26 m28    고른 것만

import re
import sys
from pathlib import Path

GUIDES = Path(__file__).resolve().parent.parent.parent / "guides"

# 산문으로 세지 않는 덩이 — 명령 화면, 코드, 표
SKIP = re.compile(r'<p class="cmdline">.*?</p>|<pre>.*?</pre>|<table.*?</table>', re.S)
# 산문 문단 — 아무 class 도 없는 <p> 와 상자 안의 글
PROSE = re.compile(r'<p>(.*?)</p>|<div class="(?:note|warn)">(.*?)</div>', re.S)

BOX = re.compile(r'<div class="(note|warn)">')
LAB = re.compile(r'<div class="lab">')
# 어미 — 문장 끝에 오는 말
ENDING = re.compile(r"([가-힣]{2,4})\.")
CONTRAST = re.compile(r"(?:가|이) 아니라|(?:은|는) 아닙니다")


def strip(s):
    """산문만 남긴다."""
    return SKIP.sub(" ", s)


def blocks(s, pattern):
    """div 짝을 세어 덩이를 정확히 자른다."""
    out = []
    for m in pattern.finditer(s):
        a, d = m.start(), 0
        for t in re.finditer(r"<div\b[^>]*>|</div>", s[a:]):
            d += 1 if t.group().startswith("<div") else -1
            if d == 0:
                out.append(s[a:a + t.end()])
                break
    return out


def prose(s):
    """산문 문단을 태그 없는 글로 뽑는다."""
    out = []
    for m in PROSE.finditer(strip(s)):
        t = m.group(1) or m.group(2) or ""
        out.append((t, re.sub(r"<[^>]+>", "", t)))
    return out


def audit(mod):
    page = GUIDES / f"{mod}.html"
    s = page.read_text(encoding="utf-8")
    found = []
    para = prose(s)
    글 = " ".join(p for _, p in para)

    # ── 1. 겹낫표 ──────────────────────────────────────
    n = 글.count("«")
    if n:
        found.append(("겹낫표", n, "산문에서 «» 로 강조했습니다 — 대부분 지웁니다"))

    # ── 2. 줄표 ────────────────────────────────────────
    # 「목적 — 」「제출물 — 」「스스로 확인 — 」 은 양식이라 세지 않는다
    라벨 = re.compile(r"^(목적|제출물|스스로 확인)\s*—\s*")
    n = sum(라벨.sub("", p).count("—") for _, p in para)
    if n > len(para) * 0.15:
        found.append(("줄표", n,
                      f"산문 {len(para)}문단에 — 가 {n}번 — 마침표로 끊으십시오"))

    # ── 3. 굵기 ────────────────────────────────────────
    n = sum(1 for t, _ in para if t.count("<b>") >= 2)
    if n:
        found.append(("굵기", n, "한 문단에 굵은 글씨가 둘 이상인 문단"))

    # ── 4. 상자 ────────────────────────────────────────
    넘침 = []
    for body in blocks(s, LAB):
        no = re.search(r'<b class="t">실습\s*([\d-]+)</b>', body)
        c = len(BOX.findall(body))
        if c > 2:
            넘침.append(f"{no.group(1) if no else '?'}({c})")
    if 넘침:
        found.append(("상자", len(넘침),
                      "한 실습에 note/warn 이 셋 이상 — " + " ".join(넘침)))

    # ── 5. 어미 ────────────────────────────────────────
    끝 = ENDING.findall(글)
    if len(끝) >= 40:
        같은말 = max(set(끝), key=끝.count)
        비율 = 끝.count(같은말) / len(끝)
        if 비율 > 0.45:
            found.append(("어미", f"{비율:.0%}",
                          f"문장 끝이 «{같은말}» 로 몰려 있습니다 — 길이와 어미를 섞으십시오"))

    # ── 6. 대조문 ──────────────────────────────────────
    넘침 = []
    for body in blocks(s, LAB):
        no = re.search(r'<b class="t">실습\s*([\d-]+)</b>', body)
        c = len(CONTRAST.findall(" ".join(p for _, p in prose(body))))
        if c > 1:
            넘침.append(f"{no.group(1) if no else '?'}({c})")
    if 넘침:
        found.append(("대조문", len(넘침),
                      "한 실습에서 「A 가 아니라 B」 를 되풀이 — " + " ".join(넘침)))

    # ── 7. 판박이 ──────────────────────────────────────
    설명 = [p for _, p in para
            if len(p) > 40 and not p.startswith(("제출물", "스스로 확인", "목적"))]
    문장수 = [len([x for x in re.split(r"(?<=다)\.", p) if x.strip()]) for p in 설명]
    if len(설명) >= 30:
        흔한 = max(set(문장수), key=문장수.count)
        비율 = 문장수.count(흔한) / len(문장수)
        if 비율 > 0.5:
            found.append(("판박이", f"{비율:.0%}",
                          f"설명 문단 {len(설명)}개 가운데 {비율:.0%}가 {흔한}문장짜리 — "
                          f"길이를 섞으십시오"))

    # ── 8. 되풀이 ──────────────────────────────────────
    문장 = []
    for p in 설명:
        문장 += [x.strip() for x in re.split(r"(?<=다)\.", p) if len(x.strip()) > 25]
    겹침 = sorted({x for x in 문장 if 문장.count(x) > 1})
    if 겹침:
        found.append(("되풀이", len(겹침),
                      "같은 문장을 여러 곳에 옮겨 놓았습니다 — 예) "
                      + 겹침[0][:38]))

    return len(para), found


def main(argv):
    mods = [a for a in argv if re.fullmatch(r"m\d+", a)]
    if not mods:
        mods = sorted((p.stem for p in GUIDES.glob("m*.html")),
                      key=lambda x: int(x[1:]))
    worst = 0
    for mod in mods:
        if not (GUIDES / f"{mod}.html").exists():
            continue
        n, found = audit(mod)
        if not found:
            print(f"✓ {mod}  산문 {n}문단  지적 0")
            continue
        worst = 1
        print(f"✗ {mod}  산문 {n}문단  지적 {len(found)}")
        for 갈래, 수, 말 in found:
            print(f"    [{갈래}] {수}  {말}")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
