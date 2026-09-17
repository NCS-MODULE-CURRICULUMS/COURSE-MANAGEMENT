# 교안의 태그 짝을 검사한다.
#
# verify_guide.py 는 <div> 만 세어 m05 의 군더더기 </b> 를 놓쳤다.
# 여기서는 HTMLParser 로 «모든» 태그의 짝을 본다.
# 브라우저가 알아서 닫아 주는 태그(p · li · td …)는 규칙대로 봐 준다.
#
#   python check_tags.py [파일 또는 글ob …]        기본값: guides/*.html

import glob
import sys
from html.parser import HTMLParser

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "col",
        "area", "base", "embed", "param", "track", "wbr"}

# 여는 태그가 «무엇을» 저절로 닫는가
CLOSES = {"p": {"p"}, "li": {"li"}, "td": {"td", "th"}, "th": {"td", "th"},
          "tr": {"td", "th", "tr"}, "dd": {"dd", "dt"}, "dt": {"dd", "dt"},
          "option": {"option"}}
OPT = set(CLOSES)          # 닫는 태그를 생략해도 되는 것들


class Check(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.bad = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        for c in CLOSES.get(tag, ()):
            if self.stack and self.stack[-1][0] == c:
                self.stack.pop()
        self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack and self.stack[-1][0] in OPT and self.stack[-1][0] != tag:
            self.stack.pop()
        if not self.stack:
            self.bad.append((self.getpos()[0], f"여는 짝이 없는 </{tag}>"))
            return
        top, line = self.stack[-1]
        if top != tag:
            self.bad.append((self.getpos()[0],
                             f"<{top}> ({line}줄) 이 열린 채 </{tag}>"))
        else:
            self.stack.pop()


def main(argv):
    files = []
    for a in (argv or ["guides/*.html"]):
        files += glob.glob(a)
    bad = 0
    for f in sorted(set(files)):
        c = Check()
        c.feed(open(f, encoding="utf-8").read())
        left = [x for x in c.stack if x[0] not in OPT]
        if c.bad or left:
            bad += 1
            print(f)
            for line, msg in c.bad[:8]:
                print(f"   {line}줄 · {msg}")
            if left:
                print("   안 닫힌 것:", ", ".join(f"<{t}> {l}줄" for t, l in left[:8]))
    print(f"{len(set(files))}개 가운데 문제 {bad}개")
    return 1 if bad else 0


sys.exit(main(sys.argv[1:]))
