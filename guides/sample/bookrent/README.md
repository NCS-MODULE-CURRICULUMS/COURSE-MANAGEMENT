# 도서 관리 시스템 — 연습용 현행 시스템

현행 시스템 분석을 연습하기 위한 **연습용** 프로젝트입니다.
평가에서 받는 원본 파일이 아니며, 평가도구의 작업지시서 내용은 담고 있지 않습니다.
실제 평가에서는 이와 비슷한 구성의 프로젝트 파일을 제공받게 됩니다.

## 이 프로젝트로 하는 일

교안 **2절 st2 · st3** 에서 씁니다.
서버에 들어가 밖에서 조사한 값(1절)을, 이번에는 **소스를 열어** 확인합니다.
같은 사실이 두 경로에서 나오는지 맞춰 보는 것이 목적입니다.

**지금 되는 것은 도서 관리뿐입니다.**
인증도 없고 대여도 없습니다 — 그것이 곧 찾아내야 할 문제점입니다.

```
bookrent/
├── pom.xml                       빌드 설정 · 언어의 판 · 드라이버
├── .project  .classpath          이클립스가 만든 파일
├── .gitignore
├── db/
│   └── schema.sql                표 구성 (books 하나뿐)
└── src/main/
    ├── java/kr/bookrent/
    │   ├── controller/BookController.java   조회 · 등록 · 수정 · 삭제
    │   ├── dao/BookDAO.java
    │   ├── model/Book.java
    │   └── util/DBConnection.java           접속 주소
    └── webapp/
        ├── index.jsp
        ├── book/list.jsp
        ├── WEB-INF/web.xml
        └── META-INF/context.xml
```

## 돌려 보려면

조사만 하는 경우에는 **돌리지 않아도 됩니다.** 파일을 읽는 것으로 충분합니다.

돌려 볼 때는 `db/schema.sql` 을 MySQL 에 넣고 WAR 로 묶어 Tomcat 의 `webapps` 에 올립니다.
자료를 넣을 때 **문자셋을 UTF-8 로 지정**해야 합니다.
MySQL 5.7 은 서버 기본 문자셋이 `latin1` 이라, 지정하지 않으면
한글이 이중으로 인코딩되어 검색이 되지 않습니다.

```
mysql -h <서버> -u root -p bookrent --default-character-set=utf8 < db/schema.sql
```
