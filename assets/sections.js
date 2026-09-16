/* 과정관리 허브 카드 목록.
 *
 * 손으로 고친 뒤 git 에 올리면 모두에게 적용됩니다.
 *
 *   group : 묶음 제목
 *   name  : 카드 제목
 *   desc  : 한 줄 설명
 *   page  : 들어갈 페이지. 비우면 '준비 중' 카드가 됩니다
 *   adm   : true 면 관리자에게만 보입니다
 */
window.CM_SECTIONS = [
  { group:"운영 가이드", name:"국기훈련 과정개발 절차", desc:"KSQA 집체(통합)훈련심사 4단계와 신청 전 준비", page:"guides/g01.html" },
  { group:"운영 가이드", name:"NCS 기반 훈련과정 편성", desc:"직무 선정 → 능력단위 선정 → 훈련시간 산정 → 편성표", page:"guides/g02.html" },
  { group:"운영 가이드", name:"평가도구 설계", desc:"능력단위별 평가방법 선정과 루브릭 작성 기준", page:"guides/g03.html" },

  { group:"평가도구", name:"훈련과정 편성표 생성기", desc:"NCS 세분류를 고르면 능력단위 1,254건에서 편성표를 만듭니다", page:"tools/t01.html" },
  { group:"평가도구", name:"평가계획서 · 평가표 생성기", desc:"능력단위별 평가방법·배점·루브릭을 만들어 인쇄/저장", page:"tools/t02.html" },
  { group:"평가도구", name:"훈련과정 자가점검표", desc:"심사 신청 전 기본요건·과정적정성 셀프 체크", page:"tools/t03.html" },

  { group:"자료", name:"표준 강의 교안 양식", desc:"교과목 운영계획서 6개 시트 — 브라우저에서 바로 보고 xlsx 로 내려받기", page:"docs/표준강의교안-샘플.html" },
  { group:"자료", name:"NCS 분류체계 (20.정보통신)", desc:"세분류 123건 · 능력단위 1,254건 원본 데이터", page:"https://github.com/NCS-MODULE-CURRICULUMS/NCS-CATALOG" },
  { group:"자료", name:"로그인 해시 생성기", desc:"이 사이트의 아이디·비밀번호를 바꿀 때 사용", page:"tools/hash.html", adm:true }
];
