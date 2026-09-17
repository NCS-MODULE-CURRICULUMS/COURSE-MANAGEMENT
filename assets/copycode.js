/* 코드 상자에 «복사» 단추 달기
 *
 *   <script src="../assets/copycode.js"></script>
 *
 * 페이지 안의 <pre> 를 찾아 오른쪽 위에 단추를 붙인다.
 * 필요한 것이 이 파일 하나뿐이도록 모양(css)도 여기서 넣는다.
 * 다른 교안에 달 때도 위 한 줄만 더하면 된다.
 *
 * 단추는 <pre> 밖에 두어야 한다. 안에 넣으면 단추의 글자까지 복사된다.
 */
(function () {
  "use strict";

  var LABEL = "복사";
  var DONE = "복사됨";
  var FAIL = "복사 실패";
  var BACK = 1600;          // 단추 글자를 되돌리기까지 (밀리초)

  function style() {
    if (document.getElementById("copycode-css")) return;
    var s = document.createElement("style");
    s.id = "copycode-css";
    s.textContent = [
      ".codebox{position:relative}",
      /* 단추가 코드를 가리지 않도록 첫 줄 오른쪽을 비워 둔다 */
      ".codebox>pre{padding-right:76px}",
      ".codebox>.copy{position:absolute;top:8px;right:8px;z-index:2;",
      "  font-family:inherit;font-size:11.5px;line-height:1;padding:5px 9px;",
      "  border:1px solid #999;background:#fff;color:#333;cursor:pointer}",
      ".codebox>.copy:hover{border-color:#000;color:#000}",
      ".codebox>.copy:focus-visible{outline:2px solid #000;outline-offset:1px}",
      ".codebox>.copy[data-state=done]{border-color:#000;color:#000;font-weight:700}",
      ".codebox>.copy[data-state=fail]{border-color:#a00;color:#a00}",
      "@media print{.codebox>.copy{display:none}}"
    ].join("\n");
    document.head.appendChild(s);
  }

  /* 눈에 보이지 않는 칸에 넣고 예전 방식으로 복사한다.
     클립보드 API 를 쓸 수 없을 때의 대비책이다. */
  function copyOld(text) {
    return new Promise(function (ok, no) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-1000px";
      document.body.appendChild(ta);
      ta.select();
      var done = false;
      try { done = document.execCommand("copy"); } catch (e) { done = false; }
      document.body.removeChild(ta);
      done ? ok() : no(new Error("execCommand 가 거절했습니다"));
    });
  }

  /* 클립보드 API 는 https 와 localhost 에서만 쓸 수 있고, 그 안에서도
     창에 포커스가 없으면 거절한다(Document is not focused).
     그래서 거절당하면 곧바로 실패로 보지 말고 예전 방식으로 한 번 더 해 본다. */
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () {
        return copyOld(text);
      });
    }
    return copyOld(text);
  }

  function attach(pre) {
    if (pre.parentNode.classList.contains("codebox")) return;

    var box = document.createElement("div");
    box.className = "codebox";
    pre.parentNode.insertBefore(box, pre);
    box.appendChild(pre);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy";
    btn.textContent = LABEL;
    btn.setAttribute("aria-label", "코드 전체 복사");

    var timer = null;
    function say(msg, state) {
      btn.textContent = msg;
      if (state) { btn.setAttribute("data-state", state); }
      else { btn.removeAttribute("data-state"); }
      clearTimeout(timer);
      timer = setTimeout(function () { say(LABEL, null); }, BACK);
    }

    btn.addEventListener("click", function () {
      copy(pre.textContent).then(
        function () { say(DONE, "done"); },
        function () { say(FAIL, "fail"); }
      );
    });

    box.appendChild(btn);
  }

  function init() {
    style();
    var list = document.querySelectorAll("pre");
    for (var i = 0; i < list.length; i++) { attach(list[i]); }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
