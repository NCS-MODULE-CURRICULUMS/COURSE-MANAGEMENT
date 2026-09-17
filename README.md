# COURSE-MANAGEMENT

국가기간·전략산업직종훈련(국기) 과정의 **개발 · 편성 · 평가도구** 페이지.
GitHub Pages 로 배포되는 정적 사이트입니다.

**https://ncs-module-curriculums.github.io/COURSE-MANAGEMENT/**

## 구성

| 경로 | 내용 |
|---|---|
| `index.html` | 허브 — 로그인 게이트 + **운영 과정 카드** + 가이드·도구 카드 |
| `courses/c1.html` | 생성형 AI 엔지니어 양성과정 — 능력단위 모듈 목록 (9개 / 160시간) |
| `courses/c2.html` | (디지털 컨버전스) 공공데이터 융합 풀스택 개발자 양성과정E — 능력단위 모듈 목록 (17개 / 900시간) |
| `modules/m01~m09.html` | c1 능력단위 상세 — NCS 정의·수준·시간·차시 전개·실습·평가 |
| `modules/c2-m01~m17.html` | c2 능력단위 상세 — 평가 개요 + **평가 자료 · 준비 교안 · 표준 강의 교안** 카드 |
| `guides/m01~m17.html` | c2 준비 교안 17종 (NCS_EXAM_PAGE 에서 그대로 가져옴) |
| `exam/m01/`, `exam/dbms/` | c2 평가 자료 — 포트폴리오 제출서 · 채점판 · 평가도구 · 샘플 문제지 |
| `guides/g01.html` | 국기훈련 과정개발 절차 (KSQA 집체(통합)훈련심사 4단계) |
| `guides/g02.html` | NCS 기반 훈련과정 편성 (직무 선정 → 편성표 제출) |
| `guides/g03.html` | 평가도구 설계 (평가방법 13종 · 루브릭) |
| `tools/t01.html` | **훈련과정 편성표 생성기** — 세분류 선택 → 능력단위 체크 → 시간 · NCS 적용비율 자동 계산 → CSV |
| `tools/t02.html` | **평가계획서 · 평가표 생성기** — 편성표 연동, 평가방법 · 배점 · 루브릭 |
| `tools/t03.html` | **훈련과정 자가점검표** — 심사 신청 전 셀프 체크 |
| `tools/hash.html` | 로그인 해시 생성기 (관리자 카드) |
| `data/*.csv` | NCS 분류체계 · 능력단위 원본 ([NCS-CATALOG](https://github.com/NCS-MODULE-CURRICULUMS/NCS-CATALOG) 에서 복사) |
| `assets/` | `site.css` · `guide.css` · `auth.js` · `sections.js` · `courses.js` · `modules.js` · `locks.js` |

`t01 → t02` 는 `localStorage` 로 이어집니다. 편성표에서 고른 능력단위를
평가계획서에서 **"편성표에서 불러오기"** 로 그대로 가져옵니다.

## 화면 구조

```
index.html  운영 과정 카드 / 가이드 / 평가도구 / 자료
   ├ courses/c1.html   생성형 AI 엔지니어 양성과정 (9개 능력단위)
   │    └ modules/mNN.html
   └ courses/c2.html   공공데이터 융합 풀스택 개발자 양성과정E (17개 능력단위)
        └ modules/c2-mNN.html
```

c2 는 NCS_EXAM_PAGE 에서 운영한 과정을 **자료까지 통째로** 가져온 것입니다.
강사·기간·평가일은 원본 값이고, **능력단위코드는 NCS-CATALOG 로 현행 코드에
매핑해 새로 붙였습니다**(원본에는 없던 정보).

준비 교안(`guides/m01~m17`)과 평가 자료(`exam/`)도 이 저장소에 있습니다.
**링크는 모두 사이트 안에 머뭅니다** — 바깥 사이트로 새어 나가지 않습니다.

과정 목록은 `assets/courses.js`, 과정별 모듈은 `assets/modules-<과정id>.js` 에 있습니다.
과정을 늘리면 `modules-c3.js` · `locks-c3.js` 를 만들고 `courses/c3.html` 을 복사해 `CID` 만 바꿉니다.
관리자로 로그인하면 표에서 직접 고치고 **[설정 파일 저장]** 으로 그 js 파일을 내려받아
덮어쓴 뒤 push 하는 방식입니다(빌드·DB 없음).

`assets/locks-<과정id>.js` 의 `true` 는 **잠김** — 일반(학생) 계정은 그 능력단위 상세를 열 수 없습니다.
표의 `잠김/열림` 버튼으로 바꾸고 역시 [설정 파일 저장] → push 로 반영합니다.

## 능력단위 모듈 목록의 단추

| 칸 | 가는 곳 | 없을 때 |
|---|---|---|
| 능력단위명 | 상세 페이지 (`modules/cN-mNN.html`) | 잠기면 점선 |
| 준비 교안 | `guides/mNN.html` 직행 | `—` |
| 평가 자료 | 상세의 평가 자료 카드 (`자료 N`) | `—` |
| **표준 교안** | `modules-cN.js` 의 `lp` 경로 | 비우면 **[양식]** → 표준 강의 교안 뷰어 |

상세 단추는 두지 않습니다 — **능력단위명 자체가 상세 링크**라 같은 곳으로 두 번 가게 됩니다.

`lp` 는 관리자 화면에서 행을 **수정**해 채우고 **[설정 파일 저장]** → push 하면 반영됩니다.
비워 두면 양식 뷰어로 보내므로, 아직 안 쓴 교과도 무엇을 채워야 하는지 바로 볼 수 있습니다.

## 구조 검사

```bash
python .github/scripts/check_site.py          # 정적 검사
python .github/scripts/check_site.py --live https://ncs-module-curriculums.github.io/COURSE-MANAGEMENT/
```

푸시·PR 때 자동으로 돌고, 매주 월요일에는 배포본까지 확인합니다.

**무엇을 잡는가**

| 검사 | 왜 |
|---|---|
| **과정 교차 링크** | c2 페이지가 c1 과정으로 넘어가던 사고가 실제로 있었다. 파일이 있으니 404 가 안 나서 링크 검사를 통과했다 |
| 깨진 내부 참조 | `<script>` · `<code>` · `<pre>` 안의 예제 코드는 제외 |
| 원본 사이트 링크 | 자료를 이 저장소로 가져왔으므로 더는 가리키면 안 된다 |
| 데이터 ↔ 파일 | `courses.js` · `modules-cN.js` · `locks-cN.js` · `items-cN.js` · `sections.js` 의 경로가 실재하는지, 잠금 키가 모듈과 맞는지 |
| 모듈 파일명 | `modules/c<과정>-m<번호>.html` 규칙 |
| 고아 페이지 | 어디서도 연결되지 않는 문서 (js 로만 연결되는 것은 제외) |
| 정답 · 개인정보 | `answers/` · `students/` · `private/` · `plan/` 에 파일이 들어왔는지 |

`--live` 는 캐시를 우회해서 확인합니다. 캐시를 안 끄면 고친 것도 안 고쳐진 것처럼 보입니다.

## 배포

빌드 없음. **GitHub Pages — `main` 브랜치 루트(`/`)** 에서 그대로 서비스합니다.
`git push` 하면 몇 분 뒤 반영됩니다.

> `data/*.csv` 를 `fetch` 로 읽기 때문에 **`file://` 로 직접 열면 도구가 동작하지 않습니다.**
> 반드시 Pages 주소로 열거나, 로컬에서 볼 때는 `python -m http.server` 로 띄우세요.

## 로그인

`assets/auth.js` 가 아이디·비밀번호의 SHA-256 해시만 비교합니다.
계정은 `user`(열람)와 `admin`(관리자 카드까지 보임) 두 가지입니다.

바꾸려면 `tools/hash.html` 에서 해시를 만들어 `auth.js` 의 `H_USER` / `H_ADMIN` 을 교체하고 push 합니다.

> ⚠️ **이 로그인은 보안 장치가 아닙니다.** 정적 사이트라 해시가 공개되고 짧은 비밀번호는 대입으로 뚫립니다.
> 학생이 우연히 들어오는 것을 막는 **가림막**으로만 쓰세요.
> 평가문항 원본 · 모범답안 · 채점 기준 · 훈련생 개인정보는 **이 저장소에 올리지 않습니다** (`.gitignore` 로 차단).

## 데이터 갱신

NCS가 개정되면 [NCS-CATALOG](https://github.com/NCS-MODULE-CURRICULUMS/NCS-CATALOG) 에서
`fetch_ncs.py` 를 돌린 뒤 `data/` 의 CSV 두 개를 다시 복사해 push 합니다.

```bash
cp ../NCS-CATALOG/data/taxonomy.csv          data/
cp ../NCS-CATALOG/data/competency-units.csv  data/
```

## 기준

NCS 29차 개정 · 대분류 20.정보통신 · 2026-09-16 수집
출처 [ncs.go.kr](https://www.ncs.go.kr) · [ksqa.or.kr](https://www.ksqa.or.kr) · [work24.go.kr](https://www.work24.go.kr)

훈련시간 · NCS 적용비율 · 훈련비 단가 등 **수치 기준은 해마다 바뀝니다.**
KSQA 당해년도 계획공고를 함께 확인하세요.
