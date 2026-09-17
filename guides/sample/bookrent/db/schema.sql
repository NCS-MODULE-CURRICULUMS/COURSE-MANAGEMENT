-- 도서 관리 시스템 — 표 구성
--
-- 운영 서버(MySQL)에 만들어 둔 것과 같다.
-- 서버가 바뀌면 이 파일로 다시 만든다.

CREATE TABLE IF NOT EXISTS books (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    author     VARCHAR(100),
    publisher  VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 처음 넣어 두는 자료
INSERT INTO books (title, author, publisher) VALUES
    ('객체지향의 사실과 오해', '조영호', '위키북스'),
    ('모던 자바 인 액션',     '라울-게이브리얼 우르마', '한빛미디어'),
    ('데이터베이스 개론',     '김연희', '한빛아카데미');
