# 「학생이 혼자 따라할 수 있는가」 를 기계로 훑는다.
#
# verify_guide.py 는 «구조» 를 본다 — 태그가 맞는가, 링크가 살아 있는가.
# 이 도구는 «따라할 수 있는가» 를 본다. 지금까지 사람이 눈으로 잡던 것들이다.
#
#   1 전제물   시작하려면 무엇을 받아야 하는지 적혀 있는가
#   2 앞참조   아직 안 한 실습의 «결과물» 을 쓰라고 하지 않는가
#   3 막힘     실습마다 «안 될 때 볼 곳» 이 있는가
#   4 마감     실습마다 제출물과 스스로 확인이 있는가
#   5 맨손     명령만 던지고 «나오는 화면» 을 안 보여 준 곳이 없는가
#
#   python tools/guide/audit.py            교안 전부
#   python tools/guide/audit.py m13 m18    고른 것만

import re
import sys
from pathlib import Path

GUIDES = Path(__file__).resolve().parent.parent.parent / "guides"

# 학생이 «받아야» 하는 것을 가리키는 말
SUPPLIED = ("EX01", "EX02", "작업지시서", "제공물", "제공되는", "제공된", "받는 프로젝트")
# 전제물을 밝혀 두었다고 볼 만한 말
DECLARED = ("시작 전에 받아야", "받아서 시작", "미리 받아", "준비물", "받아 두어야")
# «실제로 쳐야 하는 것» 인지 가리는 말 — .cmdline 은 단순 목록에도 쓰이므로
# 이 말이 든 덩이만 명령으로 센다
CMD = ("mysql>", "mysql -", "$ ", "&gt; ", "python ", "java ", "javac ", "curl ",
       "docker ", "git ", "gradlew", "SELECT ", "INSERT ", "CREATE ", "UPDATE ",
       "DELETE ", "DROP ", "EXPLAIN", "ALTER ", "npm ", "ssh ", "ping ")
# 막혔을 때를 다루는 말
STUCK = ("안 되면", "안 나오면", "이렇게 나오면", "볼 곳", "막히면", "안 뜨면",
         "나오는 것", "오류", "ERROR", "실패하면", "틀리면", "안 먹")


def labs(s):
    """실습 덩이를 (번호, 본문) 으로 끊어 낸다 — div 짝을 세어 정확히 자른다."""
    out = []
    for m in re.finditer(r'<div class="lab">', s):
        a, d = m.start(), 0
        for t in re.finditer(r"<div\b[^>]*>|</div>", s[a:]):
            d += 1 if t.group().startswith("<div") else -1
            if d == 0:
                body = s[a:a + t.end()]
                no = re.search(r'<b class="t">실습\s*([\d-]+)</b>', body)
                out.append((no.group(1) if no else "?", body))
                break
    return out


def audit(mod):
    page = GUIDES / f"{mod}.html"
    s = page.read_text(encoding="utf-8")
    plain = re.sub(r"<[^>]+>", " ", s)
    found = []

    # ── 1. 전제물 ────────────────────────────────────────
    used = sorted({w for w in SUPPLIED if w in s})
    if used and not any(d in plain for d in DECLARED):
        found.append(("전제물", "치명",
                      f"받아야 시작되는 것을 쓰는데({', '.join(used)}) "
                      f"«무엇을 받아야 하는지» 를 밝힌 곳이 없습니다"))

    lb = labs(s)
    nums = [n for n, _ in lb]

    for no, body in lb:
        bp = re.sub(r"<[^>]+>", " ", body)
        tag = f"실습 {no}"

        # ── 2. 앞참조 — 아직 안 한 실습의 결과물을 쓰라고 하는가
        try:
            here = nums.index(no)
        except ValueError:
            here = -1
        for ref in re.findall(r"실습\s*(\d+)\s*(?:의|에서)\s*([^,.·\n]{0,18})", bp):
            n, what = ref
            if n in nums and nums.index(n) > here >= 0:
                if any(k in what for k in ("만든", "쓴", "적은", "잰", "세어", "받은", "나온")):
                    found.append(("앞참조", "주의",
                                  f"{tag} 가 «실습 {n} 에서 {what.strip()}» 을 씁니다 — "
                                  f"아직 안 한 실습입니다"))

        # ── 3. 막힘 ──────────────────────────────────────
        # 명령이나 코드를 «시키는» 실습만 본다. 문서만 쓰는 실습은 해당 없다.
        shows = sum(1 for blk in re.findall(
            r'<p class="cmdline">(.*?)</p>|<pre>(.*?)</pre>', body, re.S)
            if any(k in (blk[0] or blk[1]) for k in CMD))
        if shows and not any(k in bp for k in STUCK):
            found.append(("막힘", "주의",
                          f"{tag} 는 명령을 시키는데 «안 될 때 볼 곳» 이 없습니다"))

        # ── 4. 마감 ──────────────────────────────────────
        if "제출물" not in bp:
            found.append(("마감", "주의", f"{tag} 에 제출물이 없습니다"))
        if "스스로 확인" not in bp and "끝으로" not in bp:
            found.append(("마감", "주의", f"{tag} 에 «스스로 확인» 이 없습니다"))

        # ── 5. 맨손 — 명령을 시키고 결과를 안 보여 준 실습
        cmds = shows
        if cmds == 1 and len(bp) > 1500:
            found.append(("맨손", "주의",
                          f"{tag} 에 화면이 한 덩이뿐입니다 — "
                          f"«쳐 보라» 만 있고 «이렇게 나온다» 가 모자랄 수 있습니다"))

    return lb, found


def main(argv):
    mods = [a for a in argv if re.fullmatch(r"m\d+", a)]
    if not mods:
        mods = sorted((p.stem for p in GUIDES.glob("m*.html")),
                      key=lambda x: int(x[1:]))
    worst = 0
    for mod in mods:
        if not (GUIDES / f"{mod}.html").exists():
            continue
        lb, found = audit(mod)
        if not lb:
            continue
        bad = sum(1 for k, lv, _ in found if lv == "치명")
        worst = max(worst, 2 if bad else (1 if found else 0))
        mark = "✗" if bad else ("·" if found else "✓")
        print(f"{mark} {mod}  실습 {len(lb):2}  지적 {len(found)}")
        for kind, lv, msg in found:
            print(f"    {'✗' if lv == '치명' else '·'} [{kind}] {msg}")
    return worst


sys.exit(main(sys.argv[1:]))
