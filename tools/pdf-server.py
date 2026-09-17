# -*- coding: utf-8 -*-
"""
학습모듈 PDF 로컬 서버 — 과정관리 사이트가 내 PC 의 PDF 를 바로 열도록 해 준다.

왜 필요한가
  NCS 학습모듈은 공공누리 제2유형(출처표시·상업적 이용 금지)이고, 그 안에
  국가가 저작재산권을 갖지 않은 도표·사진·삽화가 섞여 있어 배포와 공중송신에
  원작자 동의가 필요하다. 그래서 원문을 사이트(공개 저장소)에 올리지 않는다.
  대신 내 PC 에서만 도는 이 서버가 내 브라우저에만 파일을 건네준다.

왜 사이트까지 같이 내보내는가
  배포된 https://ncs-module-curriculums.github.io 에서는 이 서버에 붙을 수 없다.
  Chrome 이 공개 사이트 -> 내 PC 주소 접속을 막는다(Local Network Access).
  실제로 확인했다 — 요청이 서버에 닿지도 않고, local-network-access 권한은
  denied 로 고정이며 fetch 의 targetAddressSpace 옵션도 먹지 않는다.
  그래서 사이트와 PDF 를 같은 곳(127.0.0.1)에서 내보낸다. 같은 출처가 되면
  막을 것이 없다 — 묻지도 않고 바로 열린다.

무엇을 하는가
  127.0.0.1 에만 붙는다(다른 PC 에서 접속 불가).
  과정관리 사이트를 통째로 내보낸다.
  지정한 폴더 아래의 .pdf 만, 읽기만, 목록 없이 내보낸다.
  pdf.js 가 큰 파일을 조금씩 읽도록 Range 를 지원한다(116MB 짜리도 있다).

쓰는 법
  python COURSE-MANAGEMENT/tools/pdf-server.py            # 조직 폴더에서 실행
  python COURSE-MANAGEMENT/tools/pdf-server.py --root D:/NCS --port 8765

  그리고 http://127.0.0.1:8765/ 로 들어간다. [PDF] 가 아무것도 묻지 않는다.
  배포 사이트에서 볼 때는 폴더 고르기로 동작한다. 둘 다 그대로 쓸 수 있다.
"""
import argparse
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ORIGINS = (
    "https://ncs-module-curriculums.github.io",
    "http://localhost:8000", "http://127.0.0.1:8000",   # 로컬에서 사이트를 띄웠을 때
)
ROOT = None                                  # 커리큘럼 저장소들이 있는 조직 폴더
SITE = Path(__file__).resolve().parent.parent  # COURSE-MANAGEMENT
RANGE = re.compile(r"bytes=(\d*)-(\d*)")
MIME = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8", ".csv": "text/csv; charset=utf-8",
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
    ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8",
    ".md": "text/markdown; charset=utf-8", ".pdf": "application/pdf",
    ".woff": "font/woff", ".woff2": "font/woff2",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".py": "text/plain; charset=utf-8",
}


def allow(origin):
    return origin if origin in ORIGINS else ORIGINS[0]


class H(BaseHTTPRequestHandler):
    server_version = "ncs-pdf/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):                      # 조용히
        if "--verbose" in sys.argv:
            super().log_message(fmt, *a)

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", allow(self.headers.get("Origin", "")))
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.send_header("Access-Control-Expose-Headers",
                         "Content-Range, Content-Length, Accept-Ranges")
        self.send_header("Access-Control-Max-Age", "86400")

    def fail(self, code, why=""):
        body = why.encode("utf-8")
        self.send_response(code)
        self.cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def resolve(self):
        """?p=<조직 폴더 기준 상대경로> 를 실제 파일로. 폴더 밖은 거절한다."""
        u = urllib.parse.urlparse(self.path)
        if u.path == "/ping":
            return "ping"
        if u.path != "/file":
            return "site"                                # 사이트 파일로 넘긴다
        rel = urllib.parse.parse_qs(u.query).get("p", [""])[0]
        if not rel:
            return None
        p = (ROOT / rel).resolve()
        try:
            p.relative_to(ROOT)                          # .. 로 빠져나가는 것 차단
        except ValueError:
            return None
        if p.suffix.lower() != ".pdf" or not p.is_file():
            return None
        return p

    def site_file(self):
        """과정관리 사이트 자체. 같은 출처에서 열려야 브라우저가 막지 않는다."""
        path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        rel = path.lstrip("/") or "index.html"
        p = (SITE / rel).resolve()
        try:
            p.relative_to(SITE)
        except ValueError:
            return None
        if p.is_dir():
            p = p / "index.html"
        return p if p.is_file() else None

    def send_site(self):
        p = self.site_file()
        if p is None:
            return self.fail(404, "없는 파일입니다.")
        body = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(p.suffix.lower(),
                                                  "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")     # 고치는 중에 헷갈리지 않게
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        t = self.resolve()
        if t == "ping":
            body = b'{"ok":true,"name":"ncs-pdf"}'
            self.send_response(200)
            self.cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        if t == "site":
            return self.send_site()
        if t is None:
            return self.fail(404, "없는 파일이거나 허용되지 않는 경로입니다.")

        size = t.stat().st_size
        start, end = 0, size - 1
        code = 200
        m = RANGE.match(self.headers.get("Range", "") or "")
        if m:
            a, b = m.group(1), m.group(2)
            if a:
                start = int(a)
                end = int(b) if b else size - 1
            elif b:                                       # bytes=-N (끝에서 N 바이트)
                start = max(0, size - int(b))
            if start >= size or start > end:
                self.send_response(416)
                self.cors()
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            end = min(end, size - 1)
            code = 206

        length = end - start + 1
        self.send_response(code)
        self.cors()
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        self.send_header("Content-Disposition",
                         "inline; filename=" + urllib.parse.quote(t.name))
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if self.command == "HEAD":
            return
        with t.open("rb") as f:
            f.seek(start)
            left = length
            while left > 0:
                chunk = f.read(min(262144, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return                                # 뷰어가 닫혔다. 정상이다
                left -= len(chunk)


def main():
    global ROOT
    ap = argparse.ArgumentParser(description="학습모듈 PDF 로컬 서버")
    ap.add_argument("--root", default=".", help="커리큘럼 저장소들을 담고 있는 폴더")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    ROOT = Path(a.root).resolve()
    if not ROOT.is_dir():
        sys.exit(f"폴더가 없습니다: {ROOT}")
    n = sum(1 for _ in ROOT.glob("CURRICULUM-*/modules/*/*/reference/*.pdf"))

    print(f"폴더   {ROOT}")
    print(f"사이트 {SITE}")
    print(f"PDF    {n}개")
    print()
    print(f"  →  http://127.0.0.1:{a.port}/   여기로 들어가세요")
    print()
    print("이 주소로 열면 [PDF] 가 아무것도 묻지 않고 바로 펼쳐집니다.")
    print("(배포된 github.io 주소에서는 브라우저가 내 PC 접속을 막기 때문에 안 됩니다.)")
    print("이 PC 에서만 열립니다. 끄려면 Ctrl+C.")
    if not n:
        print("! 이 폴더 아래에서 학습모듈 PDF 를 찾지 못했습니다. --root 를 확인하세요.")
    if not (SITE / "index.html").is_file():
        print(f"! 사이트를 찾지 못했습니다: {SITE}/index.html")

    try:
        ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
    except KeyboardInterrupt:
        print("\n끝냅니다.")
    except OSError as e:
        if getattr(e, "errno", 0) in (48, 98, 10048):
            sys.exit(f"{a.port} 번 포트가 이미 쓰이고 있습니다. --port 로 다른 번호를 주세요.")
        raise


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
