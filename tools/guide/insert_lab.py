# 단계 본문 끝에 실습을 끼워 넣는다.
#
# 여는/닫는 <div> 를 세어 «자기 짝» 을 찾는다.
# 느슨한 패턴으로 찾으면 바깥 블록의 닫는 태그를 먹는다 (m04 st4 에서 겪었다).
#
#   python insert_lab.py [mNN] st13 st14 ...
#
# 실습 파일 이름은 m04 면 labs_st13.html, 그 밖이면 m05_labs_st13.html.

import re
import sys
from pathlib import Path

# 이 스크립트는 tools/guide/ 에 있다.
# 저장소를 어디에 두었든 저장소 안의 guides/ 를 찾는다.
GUIDES = Path(__file__).resolve().parent.parent.parent / "guides"


def step_span(text, sid):
    a = text.index(f'<div class="step" id="{sid}">')
    d = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', text[a:]):
        d += 1 if m.group().startswith("<div") else -1
        if d == 0:
            return a, a + m.start()
    raise SystemExit(f"{sid}: 닫는 자리를 찾지 못했습니다")


def main(argv):
    mod = "m04"
    if argv and re.fullmatch(r"m\d+", argv[0]):
        mod = argv.pop(0)
    page = GUIDES / f"{mod}.html"
    if not argv:
        raise SystemExit("넣을 단계를 적어 주십시오 (예: st1 st2)")

    s = page.read_text(encoding="utf-8")
    before = len(s)

    for sid in argv:
        a, close = step_span(s, sid)
        if 'class="lab"' in s[a:close]:
            print(f"{sid}: 이미 실습 있음 — 건너뜀")
            continue
        src = Path(f"labs_{sid}.html" if mod == "m04"
                   else f"{mod}_labs_{sid}.html")
        if not src.exists():
            print(f"{sid}: {src.name} 이 없습니다")
            continue
        lab = src.read_text(encoding="utf-8").rstrip()
        bd = s.rindex("</div>", a, close)      # .bd 가 닫히는 자리
        s = s[:bd] + lab + "\n      " + s[bd:]
        print(f"{sid}: 실습 넣음 (+{len(lab):,}자)")

    page.write_bytes(s.encode("utf-8"))
    print(f"{page.name} {before:,} -> {len(s):,}자")


main(sys.argv[1:])
