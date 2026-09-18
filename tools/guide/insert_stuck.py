# 검수(audit.py)가 «막힘» 으로 잡은 실습에 「안 될 때 볼 곳」 을 붙인다.
# 적는 오류는 전부 실제로 내 보고 받아 적은 것이다.
import re, sys
from pathlib import Path

G = Path(r"C:\Users\jwg13\Downloads\TMP_NCS_20260916\COURSE-MANAGEMENT\guides")

def T(rows, head="나오는 것"):
    body = "".join(f'    <tr><td>{a}</td><td>{b}</td></tr>\n' for a, b in rows)
    return ('  <h5>안 될 때 볼 곳</h5>\n\n  <table class="wide">\n'
            f'    <tr><th style="width:330px">{head}</th><th>볼 곳</th></tr>\n'
            f'{body}  </table>\n\n')

C = lambda x: f"<code>{x}</code>"

BLOCKS = {
("m05","2-6"): T([
 (C("ERROR 1007 (HY000): Can't create database 'bookdb'; database exists"),
  "이미 만들었습니다. 지우고 다시 하려면 "+C("DROP DATABASE bookdb;")+" — <b>안의 표가 다 지워집니다</b>"),
 (C("SELECT DATABASE();")+" 가 "+C("NULL"),
  C("USE bookdb;")+" 를 <b>안 쳤습니다</b>"),
 ("콜레이션이 "+C("utf8mb4_0900_ai_ci")+" 로 나옴",
  "<b>MySQL 8 의 기본값</b>입니다. 지시서가 "+C("utf8mb4_general_ci")+" 를 요구하면 "
  "<b>만들 때 적어야</b> 합니다 — 나중에 바꾸려면 "+C("ALTER DATABASE")),
]),
("m05","2-8"): T([
 (C("ERROR 1396 (HY000): Operation CREATE USER failed for 'dbconn'@'%'"),
  "이미 있습니다. "+C("DROP USER 'dbconn'@'%';")+" 뒤에 다시 만드십시오"),
 (C("ERROR 1410 (42000): You are not allowed to create a user with GRANT"),
  "<b>계정을 먼저 만들어야</b> 합니다. "+C("GRANT")+" 는 계정을 만들어 주지 않습니다"),
 ("없는 데이터베이스에 "+C("GRANT")+" 했는데 <b>오류가 안 남</b>",
  "<b>정상입니다.</b> MySQL 은 아직 없는 데이터베이스에도 권한을 줍니다 — "
  "<b>이름을 잘못 써도 안 알려 줍니다</b>. 철자를 직접 보십시오"),
 ("만들었는데 원격에서 접속이 안 됨",
  C("@'%'")+" 가 아니라 "+C("@'localhost'")+" 로 만들었을 수 있습니다. "
  +C("SELECT user, host FROM mysql.user")+" 로 <b>host 칸</b>을 보십시오"),
]),
("m06","2-2"): T([
 (C("ERROR 1050 (42S01): Table 'tbl_member' already exists"),
  "이미 만들었습니다. "+C("DROP TABLE tbl_member;")+" 뒤에 다시 하십시오"),
 (C("ERROR 1046 (3D000): No database selected"),
  C("USE bookdb;")+" 를 <b>안 쳤습니다</b>"),
 ("한글 칼럼값이 "+C("?")+" 로 들어감",
  "접속할 때 "+C("--default-character-set=utf8mb4")+" 를 <b>안 붙였습니다</b>"),
]),
("m06","2-6"): T([
 ("결과가 <b>한 줄도 안 나옴</b>",
  C("TABLE_SCHEMA = 'bookdb'")+" 의 <b>철자와 대소문자</b>를 보십시오. "
  "틀리면 오류 없이 <b>빈 결과</b>가 나옵니다"),
 ("FK 가 하나도 안 보임",
  "실습 2-2 는 <b>일부러 제약조건 없이</b> 만들었습니다. "
  "<b>안 나오는 것이 맞습니다</b> — 그것이 이 실습에서 보려는 것입니다"),
 (C("ERROR 1044: Access denied for user")+" 가 남",
  C("information_schema")+" 는 <b>자기 권한이 있는 것만</b> 보여 줍니다. "
  "관리자 계정으로 치십시오"),
]),
("m06","2-7"): T([
 (C("ERROR 1061 (42000): Duplicate key name 'idx_rental_book'"),
  "이미 만들었습니다. <b>오류가 아닙니다</b> — "
  "다시 만들려면 "+C("DROP INDEX idx_rental_book ON tbl_rental;")),
 (C("ERROR 1072: Key column 'Book_code' doesn't exist in table"),
  "<b>칼럼 이름의 대소문자</b>를 보십시오. 만들 때 쓴 것과 같아야 합니다"),
 (C("STATISTICS")+" 에 "+C("PRIMARY")+" 가 섞여 나옴",
  "<b>정상입니다.</b> 기본키도 인덱스라 함께 나옵니다"),
]),
("m06","2-9"): T([
 (C("ERROR 1050 (42S01): Table 'ShowRental_view' already exists"),
  "뷰도 표와 같은 이름 자리를 씁니다. "+C("DROP VIEW ShowRental_view;")+" 뒤에 다시 하십시오. "
  "또는 "+C("CREATE OR REPLACE VIEW")+" 를 쓰십시오"),
 ("칸 이름이 지시서와 <b>다르게</b> 나옴",
  C("AS")+" 로 준 <b>별칭이 곧 뷰의 칸 이름</b>입니다. 지시서의 철자·대소문자 그대로 적으십시오"),
 (C("\\G")+" 가 안 먹음",
  "명령 끝에 <b>세미콜론을 같이 붙이면</b> 안 됩니다. "+C("\\G")+" <b>하나로</b> 끝냅니다"),
]),
("m06","2-10"): T([
 ("고친 뒤 값이 "+C("사서,관리자")+" 로 <b>잘 들어감</b>",
  "<b>그것이 문제입니다.</b> 오류가 안 나는 것이 이 실습에서 보려는 것입니다 — "
  "한 칸에 둘을 넣어도 데이터베이스는 <b>말리지 않습니다</b>"),
 (C("Rows matched: 0  Changed: 0"),
  C("WHERE Member_id = 1")+" 에 <b>해당하는 줄이 없습니다</b>. 먼저 "+C("SELECT")+" 로 확인하십시오"),
 ("「사서」 만 찾는 검색이 <b>되기도 함</b>",
  C("LIKE '%사서%'")+" 는 걸립니다. 그런데 <b>「관리자,사서」 순서로 든 줄</b>이나 "
  "<b>「부사서」</b> 까지 걸립니다 — 그래서 못 쓰는 것입니다"),
]),
("m06","2-11"): T([
 (C("ERROR 1452: Cannot add or update a child row: a foreign key constraint fails"),
  "가리키는 "+C("member_id")+" 가 "+C("tbl_member")+" 에 <b>없습니다</b>. 먼저 회원을 넣으십시오"),
 (C("ERROR 1062: Duplicate entry")+" 가 남",
  "같은 사람에게 <b>같은 역할</b>을 두 번 넣었습니다. "+C("UNIQUE")+" 를 건 것이 일한 것입니다"),
 ("조인 결과가 <b>비어 있음</b>",
  C("tbl_role")+" 에 넣기만 하고 "+C("tbl_member")+" 와 <b>id 가 안 맞습니다</b>. "
  "양쪽을 각각 "+C("SELECT")+" 해 보십시오"),
]),
("m07","2-3"): T([
 (C("fatal: not a git repository"),
  C("git init")+" 을 <b>안 했거나</b> 다른 폴더에 있습니다. "+C("cd")+" 로 자리를 확인하십시오"),
 (C("error: remote origin already exists"),
  "이미 이어 두었습니다. 바꾸려면 "+C("git remote set-url origin <주소>")),
 (C("git status")+" 에 "+C("?? bin/")+" 가 보임",
  "<b>.gitignore 가 없습니다.</b> 빌드 결과가 올라가면 채점자가 받을 때 충돌합니다"),
 ("줄 끝 경고 "+C("LF will be replaced by CRLF"),
  "<b>경고일 뿐입니다.</b> 윈도에서 나오는 것이고 커밋은 정상으로 됩니다"),
]),
("m07","2-6"): T([
 (C("error: src refspec develop does not match any"),
  "그 이름의 <b>가지가 없습니다.</b> "+C("git branch")+" 로 이름과 철자를 보십시오"),
 (C("fatal: 'origin' does not appear to be a git repository"),
  C("git remote add origin")+" 를 <b>안 했습니다</b> (실습 2-3)"),
 (C("git branch -a")+" 에 "+C("remotes/")+" 가 <b>안 보임</b>",
  "<b>아직 안 올렸습니다.</b> 올린 뒤에야 원격 가지가 보입니다"),
 ("사용자 이름·비밀번호를 묻고 <b>거절됨</b>",
  "GitHub 은 비밀번호를 안 받습니다. <b>토큰</b>을 만들어 비밀번호 자리에 넣으십시오"),
]),
("m07","2-7"): T([
 (C("! [remote rejected] main -> main (protected branch hook declined)"),
  "<b>이것이 이 실습에서 보려는 화면입니다.</b> 규칙이 걸린 증거이니 <b>캡처하십시오</b>"),
 ("막힐 줄 알았는데 <b>그냥 올라감</b>",
  "규칙을 <b>저장 안 했거나</b> 가지 이름 패턴이 안 맞습니다. "
  "<b>관리자는 예외</b>로 두는 설정도 확인하십시오"),
 ("되돌리고 싶음",
  C("git reset --hard origin/main")+" — <b>커밋 안 한 변경이 사라집니다.</b> 먼저 확인하십시오"),
]),
("m07","2-9"): T([
 ("이슈 번호를 적었는데 <b>안 이어짐</b>",
  C("#2")+" 처럼 <b>우물 정과 숫자</b>가 붙어 있어야 합니다. 띄우면 안 걸립니다"),
 (C("nothing to commit, working tree clean"),
  C("git add")+" 를 <b>안 했거나</b> 고친 것이 없습니다"),
 ("한 커밋에 <b>여러 줄</b>이 들어감",
  "<b>체크리스트 한 줄이 한 커밋</b>입니다. "+C("git add <파일 하나>")+" 로 나눠 담으십시오"),
]),
("m07","2-11"): T([
 ("PR 을 여는데 <b>비교할 것이 없다</b>고 나옴",
  "<b>안 올렸습니다.</b> "+C("git push")+" 를 먼저 하십시오"),
 ("<b>승인 단추가 안 보임</b>",
  "<b>자기 PR 은 자기가 승인 못 합니다.</b> 조원에게 부탁하십시오"),
 ("병합 단추가 <b>회색</b>",
  "보호 규칙이 <b>승인 수</b>를 요구합니다. 실습 2-7 에서 건 규칙이 일하는 것입니다"),
]),
("m07","2-12"): T([
 (C("--graph")+" 인데 <b>선이 한 줄</b>로만 보임",
  C("--no-ff")+" 없이 병합해 <b>갈라진 자국이 안 남았습니다</b>. "
  "이미 병합했으면 <b>다음 병합부터</b> 붙이십시오"),
 (C("git pull")+" 에서 충돌",
  "같은 줄을 둘이 고쳤습니다. 표시를 지우고 "+C("git add")+" · "+C("git commit")+" 하십시오"),
 ("SourceTree 에 <b>가지가 안 보임</b>",
  "왼쪽에서 <b>원격</b>을 펼치고, "+C("git fetch")+" 를 한 번 돌리십시오"),
]),
("m08","2-9"): T([
 ("돈이 <b>음수</b>가 됨",
  "가진 돈을 <b>확인하기 전에 빼고</b> 있습니다. 빼기 전에 "+C("if")+" 로 막으십시오"),
 ("사과 개수가 <b>안 맞음</b>",
  "나누기가 <b>정수 나눗셈</b>이라 남는 돈이 버려집니다. "
  "지시서가 나머지를 돌려주라고 했는지 보십시오"),
 ("파는 쪽 돈이 <b>안 늘어남</b>",
  "받는 쪽 메서드에 <b>객체를 안 넘겼습니다</b>. 값만 넘기면 상대의 상태가 안 바뀝니다"),
]),
("m09","2-5"): T([
 ("커밋이 <b>한 덩이</b>로 뭉침",
  C("git add .")+" 를 한 번만 썼습니다. <b>파일별로 add 하고 그때마다 commit</b> 하십시오"),
 ("비밀번호를 지웠는데 "+C("git show 첫커밋:db.properties")+" 로 <b>그대로 나옴</b>",
  "<b>이것이 이 실습의 요점입니다.</b> "+C("git rm --cached")+" 는 <b>이력을 안 지웁니다</b>. "
  "새 저장소로 옮기거나 비밀번호를 <b>바꾸는</b> 수밖에 없습니다"),
 (C("nothing to commit"),
  C(".gitignore")+" 가 그 파일을 이미 빼고 있습니다. <b>의도한 것인지</b> 보십시오"),
]),
("m09","2-6"): T([
 (C("class ChatServer is public, should be declared in a file named ChatServer.java"),
  "<b>파일 이름과 클래스 이름이 다릅니다.</b> 대소문자까지 같아야 합니다"),
 (C("package chat does not exist"),
  "폴더 구조가 "+C("src/chat/")+" 인지 보십시오. <b>패키지 이름과 폴더가 같아야</b> 합니다"),
 ("제공된 UI 가 "+C("cannot find symbol")+" 을 냄",
  "UI 는 "+C("chat.ChatServer")+" 를 찾습니다. "
  "<b>대문자 Chat 으로 만들면 안 맞습니다</b>"),
]),
("m10","2-5"): T([
 ("검사 SQL 이 <b>한 줄도 안 뱉음</b>",
  "<b>그것이 통과입니다.</b> 어긴 줄을 찾는 SQL 이라 <b>0건이 정상</b>입니다"),
 ("일부러 넣은 나쁜 줄이 <b>안 잡힘</b>",
  C("NOT IN")+" 에 넣은 값의 <b>따옴표와 대소문자</b>를 보십시오"),
 (C("ERROR 1062: Duplicate entry")+" 로 <b>못 넣음</b>",
  C("tx_no")+" 에 "+C("UNIQUE")+" 가 걸려 있습니다. <b>다른 번호</b>로 넣으십시오"),
]),
("m11","2-6"): T([
 (C("You have an error in your SQL syntax … near '브라이언''"),
  "<b>이것이 이 실습에서 보려는 화면입니다.</b> 이름 안의 따옴표가 <b>SQL 을 끊었습니다</b>"),
 (C("?")+" 로 바꿨는데 "+C("java.sql.SQLException: No value specified for parameter 1"),
  C("setString(1, …)")+" 을 <b>안 불렀습니다.</b> 물음표 개수와 set 개수가 같아야 합니다"),
 ("한글 이름이 <b>깨져 들어감</b>",
  "접속 주소에 "+C("characterEncoding=UTF-8")+" 을 넣고, <b>넣을 때의 클라이언트 문자셋</b>도 보십시오"),
]),
("m11","2-9"): T([
 (C("HTTP 404")+" 가 남",
  C("@RequestMapping")+" 의 앞부분과 메서드 경로가 <b>겹쳐서</b> "
  +C("/member/member/list")+" 가 됐을 수 있습니다"),
 (C("HTTP 405 Method Not Allowed"),
  "화면은 "+C("POST")+" 로 보내는데 메서드가 "+C("@GetMapping")+" 입니다"),
 ("제공된 화면의 링크가 <b>안 걸림</b>",
  "<b>경로를 바꾸지 마십시오.</b> 화면이 이미 규칙대로 걸어 두었습니다"),
]),
("m11","2-12"): T([
 (C("java -version")+" 이 <b>다른 판</b>을 가리킴",
  C("JAVA_HOME")+" 과 "+C("PATH")+" 가 서로 다른 JDK 를 보고 있습니다. "
  "<b>보고서에는 실제로 빌드에 쓰인 판</b>을 적으십시오"),
 (C("gradlew.bat --version")+" 이 <b>안 돎</b>",
  "프로젝트 폴더 <b>맨 위</b>에서 쳐야 합니다"),
 ("판을 <b>기억으로</b> 적음",
  "<b>세 명령을 실제로 쳐서</b> 나온 줄을 그대로 옮기십시오. 표의 값이 곧 채점 근거입니다"),
]),
("m12","2-4"): T([
 (C("git ls-files")+" 에 "+C("build/")+" 나 "+C(".gradle/")+" 이 보임",
  "<b>.gitignore 가 늦었습니다.</b> 이미 담긴 것은 "+C("git rm -r --cached build")+" 로 빼야 합니다"),
 (C("git log --graph")+" 가 <b>한 줄</b>",
  C("--no-ff")+" 없이 병합했습니다. <b>갈라진 자국이 남지 않습니다</b>"),
 (C("nothing to commit, working tree clean"),
  C("git add")+" 를 <b>안 했습니다</b>"),
 ("커밋이 <b>한 덩이</b>",
  "<b>기능 단위로 나누는 것</b>이 채점 대상입니다. 앞으로라도 나눠 쌓으십시오"),
]),
("m12","2-5"): T([
 ("컨트롤러에서 "+C("Repository")+" 가 <b>0건이 아님</b>",
  "<b>계층이 어긋난 것입니다.</b> Service 를 거치게 고치십시오 — 항목 10 이 이것을 봅니다"),
 ("Service 에서 "+C("ResponseEntity")+" 가 나옴",
  "Service 는 <b>HTTP 를 몰라야</b> 합니다. 상태 코드는 컨트롤러 몫입니다"),
 ("찾기에서 <b>주석까지</b> 걸림",
  "<b>세는 데 넣지 마십시오.</b> 실제로 부르는 줄만 셉니다"),
]),
("m12","2-11"): T([
 ("수정했는데 <b>안 바뀜</b>",
  "<b>조회해 온 것이 아니라 새 객체</b>를 고쳤습니다. "
  +C("findById")+" 로 가져온 그 객체를 고쳐야 합니다"),
 (C("save")+" 를 <b>안 불렀는데</b> 바뀌어 불안함",
  "<b>정상입니다.</b> "+C("@Transactional")+" 안에서 조회한 객체는 "
  "메서드가 끝날 때 <b>바뀐 것이 저절로 반영</b>됩니다"),
 ("바뀌긴 하는데 <b>SQL 이 안 보임</b>",
  C("spring.jpa.show-sql=true")+" 를 켜십시오. "
  "<b>안 바뀐 필드만 있으면 UPDATE 가 아예 안 나갑니다</b>"),
]),
("m12","2-12"): T([
 (C("HTTP 404")+" 가 남",
  C("@RequestMapping(\"/api/products\")")+" 와 메서드 경로가 <b>겹쳤는지</b> 보십시오"),
 (C("HTTP 415 Unsupported Media Type"),
  "Postman 에서 <b>Body → raw → JSON</b> 으로 보내야 합니다"),
 (C("HTTP 400")+" 인데 <b>어느 칸이 틀렸는지</b> 안 나옴",
  C("@Valid")+" 는 붙였는데 <b>전역 핸들러가 칸별 메시지를 안 모으고</b> 있습니다"),
 ("무엇이 잘못돼도 <b>200</b> 이 나옴",
  "<b>가장 나쁜 경우입니다.</b> 화면이 없어 사람이 못 알아챕니다 — "
  "상태 코드를 <b>갈라서</b> 내보내십시오"),
]),
}


def main():
    done = 0
    for (mod, no), block in BLOCKS.items():
        p = G / f"{mod}.html"
        s = p.read_text(encoding="utf-8")
        m = re.search(r'<b class="t">실습 ' + re.escape(no) + r"</b>", s)
        if not m:
            print(f"  ✗ {mod} 실습 {no} 못 찾음"); continue
        if "안 될 때 볼 곳" in s[m.start():m.start() + 9000]:
            print(f"  · {mod} 실습 {no} 이미 있음"); continue
        j = s.find("<p><b>제출물</b>", m.end())
        if j < 0:
            print(f"  ✗ {mod} 실습 {no} 제출물 자리를 못 찾음"); continue
        p.write_bytes((s[:j] + block + s[j:]).encode("utf-8"))
        done += 1
        print(f"  ✓ {mod} 실습 {no:5} (+{len(block):,}자)")
    print(f"\n붙인 곳 {done} / {len(BLOCKS)}")


main()
