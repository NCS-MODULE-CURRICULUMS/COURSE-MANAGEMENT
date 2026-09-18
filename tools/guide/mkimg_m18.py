# m18 «먼저 알아야 할 것» 그림. 기존 교안 그림과 같은 판면으로 그린다.
#   흰 바탕 · 검은 선 · Malgun Gothic · 설명은 #555
import io, pathlib

# 저장소를 어디에 두었든 저장소 안의 guides/img/ 를 찾는다
OUT = pathlib.Path(__file__).resolve().parent.parent.parent / "guides" / "img"

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        'width="{w}" height="{h}">'
        '<style>text{{font-family:"Malgun Gothic",sans-serif}}'
        'rect,line,path{{stroke-width:1}}</style>'
        '<defs><marker id="on" markerWidth="10" markerHeight="8" refX="9" refY="4" '
        'orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M1,1 L9,4 L1,7" fill="none" stroke="#000"/></marker>'
        '<marker id="og" markerWidth="10" markerHeight="8" refX="9" refY="4" '
        'orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M1,1 L9,4 L1,7" fill="none" stroke="#888"/></marker></defs>'
        '<rect width="{w}" height="{h}" fill="#fff"/>')


class S:
    def __init__(self, w, h, title):
        self.w, self.h, self.p = w, h, []
        self.p.append(HEAD.format(w=w, h=h))
        self.t(20, 28, title, 14, 700)
        self.line(20, 38, w - 20, 38, "#ccc")

    def t(self, x, y, s, size=12, weight=400, fill="#000", anchor="start", mono=False):
        f = ' font-family="Consolas,monospace"' if mono else ""
        self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
                      f'fill="{fill}" text-anchor="{anchor}"{f}>{s}</text>')
        return self

    def mid(self, x, y, s, size=12.5, weight=400, fill="#000"):
        return self.t(x, y, s, size, weight, fill, "middle")

    def box(self, x, y, w, h, label=None, size=12.5, weight=400,
            fill="#fff", stroke="#000", dash=None, sub=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                      f'fill="{fill}" stroke="{stroke}"{d}/>')
        if label is not None and sub is None:
            self.mid(x + w / 2, y + h / 2 + 4.5, label, size, weight)
        elif label is not None:
            self.mid(x + w / 2, y + h / 2 - 3, label, size, weight)
            self.mid(x + w / 2, y + h / 2 + 15, sub, 11, 400, "#555")
        return self

    def line(self, x1, y1, x2, y2, stroke="#000", dash=None, arrow=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        a = f' marker-end="url(#{arrow})"' if arrow else ""
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                      f'stroke="{stroke}"{d}{a}/>')
        return self

    def arr(self, x1, y1, x2, y2, label=None, gray=False, side=None):
        self.line(x1, y1, x2, y2, "#888" if gray else "#000",
                  arrow="og" if gray else "on")
        if label:
            if x1 == x2:                       # 세로 화살표 — 옆에 적는다
                self.t(x1 + (side or 12), (y1 + y2) / 2 + 4, label, 10.5)
            else:
                self.mid((x1 + x2) / 2, min(y1, y2) - 7, label, 10.5)
        return self

    def save(self, name):
        self.p.append("</svg>")
        (OUT / name).write_text("".join(self.p), encoding="utf-8")
        print(name, sum(len(x) for x in self.p), "bytes")


# ── 1. 데이터 · 정보 · 데이터베이스 ────────────────────────────
s = S(900, 306, "데이터 · 정보 · 데이터베이스 — 무엇이 다른가")
s.t(36, 70, "① 데이터 — 값 하나하나", 12, 700)
for i, v in enumerate(["홍길동", "010-1111-2222", "자바 기초", "180000"]):
    s.box(36 + i * 104, 86, 96, 34, v, 11.5)
s.t(36, 146, "그 자체로는 무슨 뜻인지 알 수 없습니다", 11.5, 400, "#555")

s.arr(452, 103, 496, 103)

s.t(516, 70, "② 정보 — 뜻이 붙은 것", 12, 700)
s.box(516, 86, 350, 34)
s.t(528, 108, "홍길동이 «자바 기초» 를 180,000원에 신청했다", 11.5)
s.t(516, 146, "누가 · 무엇을 · 얼마에 — 이제 뜻이 생겼습니다", 11.5, 400, "#555")

s.line(20, 170, 880, 170, "#ccc")
s.t(36, 198, "③ 데이터베이스 — 그런 것을 «여럿이 함께 쓰려고» 모아 둔 곳", 12, 700)
for i, (nm, sub) in enumerate([("회원", "누가"), ("강좌", "무엇을"),
                               ("강사", "누가 가르치나"), ("신청", "언제 신청했나")]):
    s.box(36 + i * 150, 216, 134, 48, nm, 12.5, 700, sub=sub)
s.box(650, 216, 216, 48, "= 데이터베이스", 12.5, 700, fill="#f2f2f2")
s.t(36, 292, "한 곳에 모아 두면 «같은 것을 두 번 적지 않아도» 됩니다", 11.5, 400, "#555")
s.save("io_data.svg")


# ── 2. 왜 파일이 아니라 데이터베이스인가 ────────────────────────
rows = [
    ("① 두 사람이 동시에 고치면",
     ["김 선생이 열어 고치는 중", "박 선생도 같은 파일을 염"],
     "나중에 저장한 쪽이 «덮어씁니다»",
     ["김 선생의 수정", "박 선생의 수정"],
     "둘 다 순서대로 반영됩니다"),
    ("② 중간에 전원이 꺼지면",
     ["절반만 저장된 파일"],
     "어디까지 저장됐는지 «알 수 없습니다»",
     ["확정 전이면 통째로 취소"],
     "한 묶음이 «다» 되거나 «다» 안 됩니다"),
    ("③ 50만 줄에서 한 줄을 찾으면",
     ["처음부터 끝까지 훑음"],
     "줄이 늘수록 «비례해» 느려집니다",
     ["찾아보기(색인)로 바로"],
     "50만 줄이어도 거의 그대로입니다"),
]
# 줄 수에 따라 칸 높이를 따로 잡는다 — 겹치지 않게
ys, y = [], 74
for r in rows:
    n = max(len(r[1]), len(r[3]))
    ys.append(y)
    y += 20 + n * 32 + 26 + 18
s = S(900, y + 6, "엑셀 파일로 하면 무엇이 곤란한가 — 왼쪽이 파일, 오른쪽이 데이터베이스")
s.line(450, 50, 450, y - 14, "#ccc")
for (title, lf, lcap, rt, rcap), y0 in zip(rows, ys):
    n = max(len(lf), len(rt))
    s.t(36, y0, title, 12, 700)
    for i, v in enumerate(lf):
        s.box(36, y0 + 12 + i * 32, 370, 28, v, 11.5)
    s.t(36, y0 + 12 + n * 32 + 20, lcap, 11.5, 400, "#555")
    for i, v in enumerate(rt):
        s.box(480, y0 + 12 + i * 32, 370, 28, v, 11.5)
    s.t(480, y0 + 12 + n * 32 + 20, rcap, 11.5, 400, "#555")
    if y0 != ys[-1]:
        s.line(20, y0 + 12 + n * 32 + 38, 880, y0 + 12 + n * 32 + 38, "#eee")
s.save("io_why.svg")


# ── 3. 데이터베이스와 DBMS 는 다른 것 ──────────────────────────
s = S(900, 384, "데이터베이스와 DBMS — 같은 말이 아닙니다")
s.box(300, 62, 300, 46, "사람 · 프로그램", 13, 700, sub="무엇을 해 달라고 «부탁» 합니다")
s.arr(450, 108, 450, 148, "SQL 로 말합니다")
s.box(240, 148, 420, 86, fill="#f2f2f2")
s.mid(450, 174, "DBMS  (데이터베이스 관리 시스템)", 13, 700)
s.mid(450, 196, "MySQL · Oracle · PostgreSQL · SQL Server", 11, 400, "#555")
s.mid(450, 218, "말을 알아듣고 · 순서를 지키고 · 권한을 보고 · 빠르게 찾아 줍니다", 11, 400, "#555")
s.arr(450, 234, 450, 274, "읽고 씁니다")
s.box(300, 274, 300, 46, "데이터베이스", 13, 700, sub="저장장치에 실제로 «앉아 있는 값»")

s.line(20, 338, 880, 338, "#ccc")
s.t(36, 360, "데이터베이스 = 모아 둔 «값»  ·  DBMS = 그 값을 다뤄 주는 «프로그램»", 12, 700)
s.t(36, 378, "흔히 둘 다 «DB» 라고 부릅니다. 이 교안에서는 갈라서 씁니다.", 11.5, 400, "#555")
s.save("io_dbms.svg")


# ── 4. 표 한 장의 각 부분 이름 ────────────────────────────────
s = S(900, 330, "표 한 장 — 부분마다 이름이 있습니다")
x0, y0, cw, rh = 230, 96, 128, 30
cols = ["member_id", "member_nm", "phone", "join_dt"]
data = [["hong", "홍길동", "010-1111-2222", "2026-03-01"],
        ["kim", "김영희", "010-3333-4444", "2026-03-01"],
        ["lee", "이철수", "010-5555-6666", "2026-03-02"]]
for j, c in enumerate(cols):
    s.box(x0 + j * cw, y0, cw, rh, c, 11.5, 700, fill="#f2f2f2")
for i, row in enumerate(data):
    for j, v in enumerate(row):
        s.box(x0 + j * cw, y0 + rh + i * rh, cw, rh, v, 11.5)

s.t(230, 80, "member   ← 테이블 이름", 12, 700)
s.arr(200, 111, 226, 111, gray=True)
s.t(36, 115, "칼럼 이름(열 이름)", 11.5, 700)
s.arr(200, 171, 226, 171, gray=True)
s.t(36, 175, "행 · 레코드 — 한 사람", 11.5, 700)
s.t(36, 193, "표에서 «가로 한 줄»", 11, 400, "#555")

for cx, nm, sub in ((294, "기본키", "겹치지 않는 값"),
                    (550, "칼럼(열)", "표에서 «세로 한 줄»"),
                    (678, "값", "칸 하나에 하나씩")):
    s.arr(cx, 240, cx, 214, gray=True)
    s.mid(cx, 258, nm, 11.5, 700)
    s.mid(cx, 274, sub, 11, 400, "#555")

s.line(20, 296, 880, 296, "#ccc")
s.t(36, 318, "표(테이블)가 여럿 모인 것이 데이터베이스 하나입니다", 11.5, 400, "#555")
s.save("io_table.svg")


# ── 5. SQL 한 문장 읽기 ───────────────────────────────────────
s = S(900, 322, "SQL — DBMS 에게 말을 거는 말")
s.box(36, 62, 828, 62, fill="#f2f2f2")
# 마디마다 자리를 따로 잡아 «바로 아래» 에 설명을 붙인다
for x, sql, ko in ((56,  "SELECT member_nm, phone", "&#8593; 무엇을 볼지"),
                   (330, "FROM member",             "&#8593; 어디서"),
                   (480, "WHERE member_id = 'hong';", "&#8593; 어떤 것만")):
    s.t(x, 88, sql, 14, 700, mono=True)
    s.t(x, 112, ko, 11.5, 400, "#555")

s.t(36, 158, "네 마디만 알면 됩니다", 12, 700)
parts = [("SELECT", "고른다", "SELECT member_nm FROM member"),
         ("INSERT", "새로 넣는다", "INSERT INTO member VALUES (...)"),
         ("UPDATE", "고친다", "UPDATE member SET phone = ... WHERE ..."),
         ("DELETE", "지운다", "DELETE FROM member WHERE ...")]
for i, (k, ko, ex) in enumerate(parts):
    y = 172 + i * 30
    s.box(36, y, 110, 26, k, 12, 700, fill="#f2f2f2")
    s.t(164, y + 18, ko, 12, 700)
    s.t(264, y + 18, ex, 11.5, 400, "#555", mono=True)

s.line(20, 300, 880, 300, "#ccc")
s.t(36, 318, "WHERE 를 빼면 «표 전체» 에 걸립니다 — UPDATE · DELETE 에서 특히 조심합니다",
    11.5, 400, "#555")
s.save("io_sql.svg")


# ── 6. 세 번의 모델링 ─────────────────────────────────────────
s = S(900, 300, "설계는 세 번에 나누어 합니다")
stages = [("개념 모델링", "무슨 덩어리가 있나",
           ["회원", "강좌", "신청"], "속성 · 자료형은 아직"),
          ("논리 모델링", "속성과 관계를 정한다",
           ["회원(아이디·이름·연락처)", "강좌(코드·이름·수강료)", "신청 = 회원 × 강좌"],
           "어느 DBMS 인지는 아직"),
          ("물리 모델링", "실제 표로 만든다",
           ["member VARCHAR(20)", "course VARCHAR(10)", "apply INT AUTO_INCREMENT"],
           "MySQL 에 맞춰 확정")]
for i, (nm, what, items, note) in enumerate(stages):
    x = 36 + i * 290
    s.box(x, 62, 262, 40, nm, 13, 700, fill="#f2f2f2")
    s.t(x, 122, what, 11.5, 700)
    for j, it in enumerate(items):
        s.box(x, 132 + j * 32, 262, 28, it, 11, 400)
    s.t(x, 248, note, 11, 400, "#555")
    if i < 2:
        s.arr(x + 266, 82, x + 292, 82)
s.line(20, 266, 880, 266, "#ccc")
s.t(36, 288, "이 교과의 능력단위요소 ① 이 «논리», ② 가 «물리» 입니다. "
              "개념은 앞 교과에서 끝난 것으로 봅니다", 11.5, 400, "#555")
s.save("io_model.svg")
