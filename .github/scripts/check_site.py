# -*- coding: utf-8 -*-
"""
사이트 구조 검사.

파일이 존재하는지만 보면 "엉뚱한 곳으로 가는 링크"를 못 잡는다.
실제로 exam/ 의 평가 자료가 다른 과정(c1)의 페이지를 가리키고 있었는데
파일이 있으니 404 가 안 나서 링크 검사를 통과했다.

그래서 여기서는 소유 관계까지 본다. 어떤 페이지가 어느 과정에 속하는지를
assets/*.js 의 데이터에서 끌어내고, 과정을 넘나드는 링크를 오류로 잡는다.

  python .github/scripts/check_site.py              정적 검사 (CI 가 이것을 돌린다)
  python .github/scripts/check_site.py --live <URL> 배포본까지 확인 (캐시 우회)
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "assets"

# 우리 조직 밖으로 나가도 되는 곳. 그 밖의 외부 링크는 경고한다.
EXT_OK = ("https://github.com/NCS-MODULE-CURRICULUMS",
          "https://www.ncs.go.kr", "https://ncs.go.kr",
          "https://www.ksqa.or.kr", "https://www.work24.go.kr",
          "https://www.law.go.kr", "https://www.data.go.kr",
          "https://ncs-module-curriculums.github.io")
# 원본 사이트 — 자료를 이 저장소로 가져왔으므로 더는 가리키면 안 된다.
EXT_BAN = ("my-web-common-lecture.github.io",)

errors, warns = [], []


def err(m): errors.append(m)
def warn(m): warns.append(m)


def jsvar(path, var):
    """assets/*.js 의 window.<var> = <JSON>; 을 읽는다."""
    p = A / path
    if not p.exists():
        return None
    m = re.search(rf"window\.{var}\s*=\s*(\[.*?\]|\{{.*?\}});\s*$",
                  p.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # 손으로 쓰는 파일은 키에 따옴표가 없는 JS 객체 리터럴이다. JSON 으로 맞춰 준다.
    fixed = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:',
                   lambda x: x.group(1) + '"' + x.group(2) + '":', raw)
    fixed = re.sub(r",(\s*[}\]])", lambda x: x.group(1), fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        err(f"assets/{path} 의 {var} 를 읽을 수 없습니다 — {e}")
        return None


def norm(p: Path):
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


# ── 1. 데이터에서 과정별 소유 페이지를 끌어낸다 ────────────────────────
courses = jsvar("courses.js", "CM_COURSES") or []
if not courses:
    err("assets/courses.js 에서 과정 목록을 읽지 못했습니다")

owner = {}          # 페이지 경로 → 과정 id
mods_of = {}        # 과정 id → 모듈 목록

for c in courses:
    cid = c["id"]
    if c.get("page"):
        owner[c["page"]] = cid
        if not (ROOT / c["page"]).exists():
            err(f"courses.js: {cid} 의 page '{c['page']}' 가 없습니다")

    mods = jsvar(f"modules-{cid}.js", "CM_MODULES")
    if mods is None:
        err(f"assets/modules-{cid}.js 가 없거나 읽을 수 없습니다")
        continue
    mods_of[cid] = mods

    for m in mods:
        if m.get("page"):
            owner[m["page"]] = cid
            if not (ROOT / m["page"]).exists():
                err(f"modules-{cid}.js: {m['id']} 의 page '{m['page']}' 가 없습니다")
        if m.get("lp"):                      # 표준 강의 교안 — 비우면 양식으로 보낸다
            owner.setdefault(m["lp"], cid)
            if not (ROOT / m["lp"]).exists():
                err(f"modules-{cid}.js: {m['id']} 의 lp '{m['lp']}' 가 없습니다")

    # 잠금 키가 모듈과 맞는지
    locks = jsvar(f"locks-{cid}.js", "CM_LOCKS")
    if locks is None:
        err(f"assets/locks-{cid}.js 가 없거나 읽을 수 없습니다")
    else:
        ids = {m["id"] for m in mods}
        for k in set(locks) - ids:
            err(f"locks-{cid}.js: '{k}' 는 modules-{cid}.js 에 없는 모듈입니다")
        for k in ids - set(locks):
            warn(f"locks-{cid}.js: '{k}' 의 잠금 값이 없습니다 (기본 열림으로 동작)")

    # 평가 자료 · 준비 교안도 그 과정 소유다
    items = jsvar(f"items-{cid}.js", "CM_ITEMS") or {}
    for mid, lst in items.items():
        for it in lst:
            link = it.get("link", "")
            tgt = norm((A / link)) if link.startswith("../") else None
            if tgt:
                owner.setdefault(tgt, cid)
                if not (ROOT / tgt).exists():
                    err(f"items-{cid}.js: {mid} '{it.get('title')}' 의 link '{link}' 가 없습니다")
    guides = jsvar(f"items-{cid}.js", "CM_GUIDES") or {}
    for mid in guides:
        g = f"guides/{mid}.html"
        owner.setdefault(g, cid)
        if not (ROOT / g).exists():
            err(f"items-{cid}.js: CM_GUIDES 의 '{mid}' 에 해당하는 {g} 가 없습니다")

# 허브 카드 — index.html 이 sections.js 로 그리므로 HTML 링크에는 안 나온다
hub = set()
for sec in (jsvar("sections.js", "CM_SECTIONS") or []):
    pg = sec.get("page", "")
    if pg and not pg.startswith("http"):
        hub.add(pg)
        if not (ROOT / pg).exists():
            err(f"sections.js: '{sec.get('name')}' 의 page '{pg}' 가 없습니다")
lp = jsvar("lesson-plan.js", "CM_LESSON_PLAN") or {}
for k in ("view", "file"):
    v = (lp.get(k) or "").lstrip("./")
    if v.startswith("../"):
        v = v[3:]
    if v:
        hub.add(v)
        if not (ROOT / v).exists():
            err(f"lesson-plan.js: {k} '{lp.get(k)}' 가 없습니다")


# ── 2. 모듈 파일명 규칙 ────────────────────────────────────────────
for p in sorted((ROOT / "modules").glob("*.html")):
    if not re.fullmatch(r"c\d+-m\d{2}\.html", p.name):
        err(f"modules/{p.name}: 파일명이 'c<과정>-m<번호>.html' 규칙에 맞지 않습니다")

# ── 3. 링크 검사 — 깨진 곳 · 과정 교차 · 외부 ──────────────────────
REF = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"')
STRIP = ("script", "code", "pre")          # 그 안은 예제 코드라 링크가 아니다
n_ref = 0

for p in sorted(ROOT.rglob("*.html")):
    if ".git" in p.parts:
        continue
    rel = norm(p)
    s = p.read_text(encoding="utf-8", errors="replace")
    for tag in STRIP:
        s = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", "", s, flags=re.S | re.I)
    s = s.replace("&lt;", "<").replace("&gt;", ">")
    for tag in STRIP:
        s = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", "", s, flags=re.S | re.I)

    src_course = owner.get(rel)
    for h in REF.findall(s):
        if h.startswith(("javascript:", "#", "mailto:", "data:", "//")):
            continue
        if h.startswith(("http://", "https://")):
            if any(b in h for b in EXT_BAN):
                err(f"{rel} → {h[:70]} (원본 사이트로 나갑니다)")
            elif not h.startswith(EXT_OK):
                warn(f"{rel} → 외부 {h[:70]}")
            continue
        n_ref += 1
        t = urllib.parse.unquote(h.split("#")[0].split("?")[0])
        if not t:
            continue
        tgt = (ROOT / t[1:]) if t.startswith("/") else (p.parent / t)
        if not tgt.exists():
            err(f"{rel} → {h} (대상 없음)")
            continue
        trel = norm(tgt)
        dst_course = owner.get(trel) if trel else None
        if src_course and dst_course and src_course != dst_course:
            err(f"{rel} ({src_course}) → {trel} ({dst_course}) — 다른 과정으로 넘어갑니다")

# ── 4. 어디서도 닿지 않는 페이지 ───────────────────────────────────
linked = set()
for p in ROOT.rglob("*.html"):
    if ".git" in p.parts:
        continue
    s = p.read_text(encoding="utf-8", errors="replace")
    for h in REF.findall(s):
        if h.startswith(("http", "javascript:", "#", "mailto:", "data:", "//")):
            continue
        t = urllib.parse.unquote(h.split("#")[0].split("?")[0])
        if not t.endswith(".html"):
            continue
        tgt = (ROOT / t[1:]) if t.startswith("/") else (p.parent / t)
        r = norm(tgt)
        if r:
            linked.add(r)
# 데이터(js)로만 연결되는 페이지도 닿은 것으로 본다
linked |= set(owner) | hub
for p in sorted(ROOT.rglob("*.html")):
    if ".git" in p.parts or "img" in p.parts:
        continue
    rel = norm(p)
    if rel == "index.html" or rel in linked:
        continue
    warn(f"{rel}: 어느 페이지에서도 연결되지 않습니다")

# ── 5. 정답·개인정보가 섞여 들어오지 않았는지 ──────────────────────
for d in ("answers", "students", "private", "plan"):
    dd = ROOT / d
    if dd.exists():
        extra = [x for x in dd.rglob("*") if x.is_file() and x.name != "README.txt"]
        if extra:
            err(f"{d}/ 에 파일 {len(extra)}개가 있습니다 — 공개 저장소입니다. "
                f"({', '.join(x.name for x in extra[:3])})")

# ── 6. 배포본 확인 (선택) ──────────────────────────────────────────
if "--live" in sys.argv:
    i = sys.argv.index("--live")
    base = sys.argv[i + 1] if len(sys.argv) > i + 1 else \
        "https://ncs-module-curriculums.github.io/COURSE-MANAGEMENT/"
    base = base.rstrip("/") + "/"
    import random
    print(f"\n배포본 확인 — {base}")
    targets = ["index.html"] + sorted(owner)
    for rel in targets:
        u = base + urllib.parse.quote(rel) + f"?cb={random.random()}"   # 캐시 우회
        try:
            req = urllib.request.Request(u, headers={"Cache-Control": "no-cache"})
            code = urllib.request.urlopen(req, timeout=30).status
        except Exception as e:
            code = getattr(e, "code", str(e))
        if code != 200:
            err(f"배포본 {rel} → {code}")
    print(f"  {len(targets)}개 확인")

# ── 결과 ──────────────────────────────────────────────────────────
print(f"\nHTML {len(list(ROOT.rglob('*.html')))}개 · 내부 참조 {n_ref}건 · "
      f"과정 {len(courses)}개 · 소유 페이지 {len(owner)}개")
if warns:
    print(f"\n경고 {len(warns)}건")
    for w in warns[:30]:
        print("  ⚠ " + w)
if errors:
    print(f"\n오류 {len(errors)}건")
    for e in errors[:40]:
        print("  ✗ " + e)
    sys.exit(1)
print("\n구조 이상 없습니다.")
