# 교안 검수 — 한 단계를 손보고 나서 돌린다.
#
# 손으로 눈검사하면 빠뜨린다. 지금까지 실제로 났던 사고를 그대로 검사로 만든다.
#   · m04 st4 에서 닫는 태그가 먹혀 뒤쪽 단계가 통째로 중첩됐다
#   · 그림 번호가 겹쳤다
#   · 없는 파일을 링크했다
#   · 산출물 사이의 값이 어긋났다 (대여 기능, SR-반납, 기존 API)
#
# 교안마다 표기 관례가 다르다. m04 는 그림에 번호를 붙이고 채점 항목을
# ①②③ 로 나누지만, m05 는 설명형 캡션에 채점 항목이 01~15 평번호다.
# 관례를 모르고 한 잣대로 재면 헛돈다.
#
#   python verify_guide.py [mNN]

import re
import sys
from pathlib import Path

# 이 스크립트는 tools/guide/ 에 있다.
# 저장소를 어디에 두었든 저장소 안의 guides/ 를 찾는다.
GUIDES = Path(__file__).resolve().parent.parent.parent / "guides"

MOD = next((a for a in sys.argv[1:] if re.fullmatch(r"m\d+", a)), "m04")
PAGE = GUIDES / f"{MOD}.html"

# 교안별 채점 항목 표기
SCORE = {
    "m04": [f"{m} {i:02d}" for m, lo, hi in
            (("\u2460", 1, 5), ("\u2461", 6, 10), ("\u2462", 11, 20))
            for i in range(lo, hi + 1)],
    "m05": [f"{i:02d}" for i in range(1, 16)],
    "m06": [f"{i:02d}" for i in range(1, 21)],
    "m07": [f"{i:02d}" for i in range(1, 20)],
    "m10": [str(i) for i in range(1, 12)],
    "m11": [f"{g}-{i}" for g in (1, 2) for i in range(1, 11)],
    "m12": [str(i) for i in range(1, 21)],
    "m08": [f"{i:02d}" for i in range(1, 12)],
    "m09": [f"{i:02d}" for i in range(1, 16)],
    # m18 은 평가도구가 없는 모듈이라 «채점 항목» 대신 NCS 수행준거를 센다
    "m18": [f"{g}-{i}" for g, n in ((1, 3), (2, 3), (3, 4), (4, 3))
            for i in range(1, n + 1)],
}

# 산출물 고리는 교안마다 시나리오가 달라 따로 적는다
CHAIN = {
    "m04": [
        ("현행 기능", "도서 등록 / 수정 / 삭제 / 조회 (전체, 키워드)"),
        ("문제점 1", "인증 기능 부재"),
        ("문제점 2", "도서 대여 기능 없음"),
        ("SR 반납", "SR-05"),
        ("기존 액터", "구분이 없어 누구나"),
        ("DB 서버 판", "5.7"),
    ],
}

s = PAGE.read_text(encoding="utf-8")
bad, warn = [], []

# ── 1. div 가 짝이 맞는가 ─────────────────────────────────
steps = re.findall(r'<div class="step" id="(st\d+)">', s)
for sid in steps:
    a = s.index(f'<div class="step" id="{sid}">')
    d, end = 0, None
    for m in re.finditer(r'<div\b[^>]*>|</div>', s[a:]):
        d += 1 if m.group().startswith("<div") else -1
        if d == 0:
            end = a + m.end()
            break
    if end is None:
        bad.append(f"{sid}: 닫히지 않습니다")
        continue
    body = s[a:end]
    nested = len(re.findall(r'<div class="step" id="st\d+">', body)) - 1
    if nested:
        bad.append(f"{sid}: 다른 단계 {nested}개를 품고 있습니다 (닫는 태그 누락)")
    n_aside = len(re.findall(r"<aside", body))
    if n_aside != 1:
        bad.append(f"{sid}: aside 가 {n_aside}개입니다 (1개여야 합니다)")

# ── 2. 그림 — 번호를 쓰는 교안만 겹침을 본다 ─────────────
defined = re.findall(r"<figcaption>\[그림 ([\d\-]+)\]", s)
n_img = len(re.findall(r"<img ", s))
if defined:
    dup = sorted({n for n in defined if defined.count(n) > 1})
    if dup:
        bad.append(f"그림 번호 중복: {', '.join(dup)}")
    rest = re.sub(r"<figcaption>.*?</figcaption>", "", s, flags=re.S)
    for n in sorted(set(re.findall(r"\[그림 ([\d\-]+)\]", rest))):
        if n not in defined:
            bad.append(f"본문이 없는 그림을 가리킵니다: [그림 {n}]")
    fig_desc = f"그림 {n_img} (번호 {len(defined)})"
else:
    fig_desc = f"그림 {n_img} (번호 없는 관례)"

# 그림마다 alt 가 있는가 — 없으면 읽어 주는 도구에서 빈칸이 된다
no_alt = len(re.findall(r"<img (?![^>]*\balt=)[^>]*>", s))
if no_alt:
    warn.append(f"alt 가 없는 그림 {no_alt}개")

# ── 3. 링크한 파일이 있는가 ──────────────────────────────
for href in sorted(set(re.findall(
        r'(?:src|href)="((?!https?:|#|javascript:|mailto:)[^"]+)"', s))):
    t = href.split("#")[0].split("?")[0]
    if t and not (PAGE.parent / t).exists():
        bad.append(f"대상 없음: {href}")

# ── 4. 산출물 사이의 값이 이어지는가 ─────────────────────
for what, token in CHAIN.get(MOD, []):
    if token not in s:
        bad.append(f"고리 끊김 — {what}: 「{token}」 이 교안에 없습니다")

if MOD == "m04":
    for m in re.finditer(r"[^<>]{0,40}현행[^<>]{0,60}", s):
        t = m.group()
        if "대여" in t and "없" not in t and "추가" not in t:
            warn.append(f"현행+대여 표현 확인: …{t.strip()[:56]}…")

# ── 5. 단계마다 실습이 있는가 ────────────────────────────
todo = []
for i, sid in enumerate(steps):
    a = s.index(f'<div class="step" id="{sid}">')
    b = (s.index(f'<div class="step" id="{steps[i + 1]}">')
         if i + 1 < len(steps) else len(s))
    if 'class="lab"' not in s[a:b]:
        todo.append(sid)
if todo:
    warn.append(f"아직 실습이 없는 단계 {len(todo)}개: {' '.join(todo)}")

# ── 6. 채점 항목이 모두 언급되는가 ───────────────────────
#    「06 ~ 10」 처럼 범위로 적은 것도 덮은 것으로 본다.
covered = set()
for mark, lo, hi in re.findall(r"([\u2460\u2461\u2462]?)\s*(\d{2})\s*~\s*(\d{2})", s):
    covered |= {f"{mark} {i:02d}".strip() for i in range(int(lo), int(hi) + 1)}
for mark, n in re.findall(r"([\u2460\u2461\u2462]?)\s*(\d{2})", s):
    covered.add(f"{mark} {n}".strip())
# 한 자리로 적는 교안(m10) — 「채점 …」 뒤에 오는 번호만 센다.
# 아무 데서나 한 자리를 세면 「10점」 의 1 까지 걸린다.
for run in re.findall(r"채점(?:\s*항목)?\s*([\d\s·~∙,]+)", s):
    for n in re.findall(r"\d+", run):
        covered.add(str(int(n)))
    rng = re.findall(r"(\d+)\s*~\s*(\d+)", run)
    for lo, hi in rng:
        covered |= {str(i) for i in range(int(lo), int(hi) + 1)}
# 「1-1 ~ 1-10」 처럼 «묶음-번호» 로 적는 교안(m11)
for g, lo, hi in re.findall(r"(\d)-(\d+)\s*~\s*\d-(\d+)", s):
    covered |= {f"{g}-{i}" for i in range(int(lo), int(hi) + 1)}
for g, n in re.findall(r"(\d)-(\d+)", s):
    covered.add(f"{g}-{n}")
missing = [w for w in SCORE.get(MOD, []) if w not in covered]
if missing:
    warn.append(f"채점 항목 언급 없음: {', '.join(missing)}")

# ── 결과 ─────────────────────────────────────────────────
n_lab = s.count('<div class="lab">')
print(f"{PAGE.name}  {len(s):,}자 · 단계 {len(steps)} · {fig_desc} · 실습 {n_lab}")
print()
if warn:
    print(f"확인 {len(warn)}건")
    for w in warn:
        print("  ·", w)
    print()
if bad:
    print(f"오류 {len(bad)}건")
    for b in bad:
        print("  ✗", b)
    sys.exit(1)
print("검수 통과 — 구조 · 그림 · 링크 · 산출물 고리 이상 없음")
