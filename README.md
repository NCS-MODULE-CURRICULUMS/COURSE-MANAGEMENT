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

c2 는 [NCS_EXAM_PAGE](https://my-web-common-lecture.github.io/NCS_EXAM_PAGE/) 에서 운영한 과정을
그대로 가져온 것입니다. 강사·기간·평가일·사전평가·능력단위 점수는 원본 값이고,
**능력단위코드는 NCS-CATALOG 로 현행 코드에 매핑해 새로 붙였습니다**(원본에는 없던 정보).
준비 교안과 평가 자료 실물은 원본 사이트에 있어 그쪽으로 연결합니다.

과정 목록은 `assets/courses.js`, 과정별 모듈은 `assets/modules-<과정id>.js` 에 있습니다.
과정을 늘리면 `modules-c3.js` · `locks-c3.js` 를 만들고 `courses/c3.html` 을 복사해 `CID` 만 바꿉니다.
관리자로 로그인하면 표에서 직접 고치고 **[설정 파일 저장]** 으로 그 js 파일을 내려받아
덮어쓴 뒤 push 하는 방식입니다(빌드·DB 없음).

`assets/locks-<과정id>.js` 의 `true` 는 **잠김** — 일반(학생) 계정은 그 능력단위 상세를 열 수 없습니다.
표의 `잠김/열림` 버튼으로 바꾸고 역시 [설정 파일 저장] → push 로 반영합니다.

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
