/* 학습모듈 PDF 보기 — 모달로 띄운다.
 *
 * PDF 원문은 한국직업능력연구원 저작물(공공누리 제2유형)이고 제3자 저작물이
 * 섞여 있어 배포·공중송신에 원작자 동의가 필요하다. 그래서 이 저장소에 없다
 * (291개 3.0GB). 대신 강사 PC 에 받아 둔 파일을 브라우저가 직접 연다.
 *
 * 두 갈래가 있고 뷰어가 알아서 고른다.
 *
 *   이 페이지가 tools/pdf-server.py 에서 나왔으면 (127.0.0.1)
 *       → 같은 출처라 아무것도 묻지 않고 바로 연다
 *   배포된 github.io 에서 보고 있으면
 *       → 폴더를 한 번 고른다. 그 뒤로는 기억한다
 *         (여기서 내 PC 의 서버로 붙는 길은 없다. Chrome 이 공개 사이트에서
 *          루프백으로 나가는 것을 막는다 — Local Network Access)
 *   폴더 고르기가 안 되는 브라우저면
 *       → 서버 쪽 방법과 ncs.go.kr 내려받기를 알려 준다
 *
 * 폴더 권한은 브라우저가 관리한다. 파일은 읽기만 하고 어디로도 보내지 않는다.
 * 쓰는 것 : window.CM_PDF (assets/modules-pdf.js) · assets/pdfjs/ (vendored pdf.js)
 */
(function () {
  "use strict";

  var DB = "ncs-pdf", STORE = "h", KEY = "root";
  var NCS = "https://www.ncs.go.kr/unity/hth01/hth0101/downloadFile.do";
  var pdfjs = null, root = null, task = null, doc = null, blob = null;
  var page = 1, scale = 1.2, rendering = false, dirty = false;
  var local = null;                           // null 아직 안 봄 · true 켜짐 · false 없음

  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  /* ── 폴더 손잡이를 기억해 둔다 (IndexedDB 에만 들어간다) ───────────── */
  function idb(mode, fn) {
    return new Promise(function (ok, no) {
      var rq = indexedDB.open(DB, 1);
      rq.onupgradeneeded = function () { rq.result.createObjectStore(STORE); };
      rq.onerror = function () { no(rq.error); };
      rq.onsuccess = function () {
        var tx = rq.result.transaction(STORE, mode), r = fn(tx.objectStore(STORE));
        tx.oncomplete = function () { rq.result.close(); ok(r && r.result); };
        tx.onerror = function () { rq.result.close(); no(tx.error); };
      };
    });
  }
  var saveRoot = function (h) { return idb("readwrite", function (s) { s.put(h, KEY); }); };
  var loadRoot = function () { return idb("readonly", function (s) { return s.get(KEY); }); };

  function supported() {
    return typeof window.showDirectoryPicker === "function";
  }

  /* 저장해 둔 폴더의 읽기 권한 상태. 브라우저를 다시 열면 보통 'prompt' 로 돌아오는데,
     권한 요청은 사용자가 누른 직후에만 되므로 여기서 조르지 않고 상태만 돌려준다. */
  function perm(h) {
    if (!h || !h.queryPermission) return Promise.resolve("denied");
    return h.queryPermission({ mode: "read" })
      .catch(function () { return "denied"; });
  }

  /* 경로 조각을 따라 내려가 파일을 집는다. */
  function resolve(h, parts) {
    var i = 0;
    function step(dir) {
      if (i === parts.length - 1) return dir.getFileHandle(parts[i]);
      return dir.getDirectoryHandle(parts[i++]).then(step);
    }
    return step(h);
  }

  /* ── 모달 ──────────────────────────────────────────────────────── */
  var el = {};
  function build() {
    if (el.wrap) return;
    var w = document.createElement("div");
    w.className = "pv";
    w.innerHTML =
      '<div class="pv-box" role="dialog" aria-modal="true" aria-label="학습모듈 PDF">' +
      '<div class="pv-top">' +
      '<b class="pv-t"></b>' +
      '<span class="pv-nav">' +
      '<button type="button" class="pv-b" data-a="prev">이전</button>' +
      '<span class="pv-pg"><i class="pv-c">–</i> / <i class="pv-n">–</i></span>' +
      '<button type="button" class="pv-b" data-a="next">다음</button>' +
      '<button type="button" class="pv-b" data-a="out">축소</button>' +
      '<button type="button" class="pv-b" data-a="in">확대</button>' +
      '</span>' +
      '<button type="button" class="pv-b pv-x" data-a="close">닫기</button>' +
      '</div>' +
      '<div class="pv-body"><div class="pv-msg"></div><canvas class="pv-cv"></canvas></div>' +
      '</div>';
    document.body.appendChild(w);
    el = {
      wrap: w, box: w.querySelector(".pv-box"), title: w.querySelector(".pv-t"),
      nav: w.querySelector(".pv-nav"), cur: w.querySelector(".pv-c"),
      num: w.querySelector(".pv-n"), body: w.querySelector(".pv-body"),
      msg: w.querySelector(".pv-msg"), cv: w.querySelector(".pv-cv")
    };
    w.addEventListener("click", function (e) {
      var a = e.target.getAttribute && e.target.getAttribute("data-a");
      if (e.target === w) return close();
      if (!a) return;
      if (a === "close") close();
      else if (a === "prev") go(page - 1);
      else if (a === "next") go(page + 1);
      else if (a === "in") zoom(0.25);
      else if (a === "out") zoom(-0.25);
      else if (a === "pick") pick();
      else if (a === "grant") grant();
      else if (a === "retry") { local = null; if (wanted) open(wanted); }
    });
    document.addEventListener("keydown", function (e) {
      if (!el.wrap.classList.contains("on")) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowLeft" || e.key === "PageUp") go(page - 1);
      else if (e.key === "ArrowRight" || e.key === "PageDown") go(page + 1);
    });
  }

  function close() {
    el.wrap.classList.remove("on");
    document.body.style.overflow = "";
    if (task) { try { task.cancel(); } catch (e) {} task = null; }
    if (doc) { try { doc.destroy(); } catch (e) {} doc = null; }
    if (blob) { URL.revokeObjectURL(blob); blob = null; }   // 10MB 짜리를 물고 있지 않는다
    el.cv.width = el.cv.height = 0;
    el.cv.style.display = "none";
    el.nav.style.visibility = "hidden";
  }

  function say(html) {
    el.msg.innerHTML = html;
    el.msg.style.display = "";
    el.cv.style.display = "none";
  }

  function ncsLink(meta) {
    var d = (meta.d || "").split("|");
    if (d.length !== 3 || !d[1]) return "";
    return NCS + "?sysDstinCd=" + encodeURIComponent(d[0]) +
      "&fileMstky=" + encodeURIComponent(d[1]) +
      "&filedetlSeq=" + encodeURIComponent(d[2]);
  }

  /* ── pdf.js ────────────────────────────────────────────────────── */
  function lib() {
    if (pdfjs) return Promise.resolve(pdfjs);
    var base = (window.CM_BASE || "") + "assets/pdfjs/";
    return import(base + "pdf.min.mjs").then(function (m) {
      m.GlobalWorkerOptions.workerSrc = base + "pdf.worker.min.mjs";
      pdfjs = m;
      return m;
    });
  }

  function render() {
    if (!doc) return;
    if (rendering) { dirty = true; return; }   // 그리는 중이면 표시만 해 두고 나간다
    rendering = true;
    dirty = false;
    doc.getPage(page).then(function (pg) {
      var vp = pg.getViewport({ scale: scale * (window.devicePixelRatio || 1) });
      el.cv.width = vp.width; el.cv.height = vp.height;
      el.cv.style.width = (vp.width / (window.devicePixelRatio || 1)) + "px";
      el.msg.style.display = "none";
      // site.css 가 .pv-cv 를 display:none 으로 두므로 빈 문자열로 되돌리면
      // 다시 숨는다. 그려 놓고 안 보이던 원인이 이것이었다.
      el.cv.style.display = "block";
      task = pg.render({ canvasContext: el.cv.getContext("2d"), viewport: vp });
      return task.promise;
    }).then(function () {
      el.cur.textContent = page;
      done();
    }).catch(function (e) {
      // 취소는 실패가 아니다 — 다음 쪽을 그리라고 우리가 끊은 것이다.
      // 여기서 그냥 돌아가면 화면이 빈 채로 남는다(실제로 그랬다).
      if (e && e.name === "RenderingCancelledException") return done();
      rendering = false;
      say("<b>이 쪽을 그리지 못했습니다.</b><br>" + esc(e && e.message));
    });
  }

  /* 그리기가 끝났다. 그 사이에 쪽이나 배율이 바뀌었으면 한 번 더 그린다. */
  function done() {
    rendering = false;
    if (dirty) render();
  }

  function redraw() {
    if (task) { try { task.cancel(); } catch (e) {} }
    render();
  }

  function go(n) {
    if (!doc) return;
    n = Math.max(1, Math.min(doc.numPages, n));
    if (n === page) return;
    page = n;
    redraw();
  }
  function zoom(d) {
    var s = Math.max(0.5, Math.min(4, scale + d));
    if (s === scale) return;
    scale = s;
    redraw();
  }

  /* 이 페이지 자체가 tools/pdf-server.py 에서 나온 것인지 확인한다.
   *
   * 배포된 https://…github.io 에서 내 PC 의 127.0.0.1 로 붙는 길은 없다 —
   * Chrome 이 공개 사이트에서 사설·루프백 주소로 나가는 것을 막는다
   * (Local Network Access). 확인해 보면 요청이 서버에 닿지도 않고,
   * local-network-access 권한은 denied 고정이며 fetch 의 targetAddressSpace
   * 옵션도 먹지 않는다. 그래서 '다른 출처의 로컬 서버'는 아예 시도하지 않는다.
   *
   * 대신 서버가 사이트까지 같이 내보내므로, 같은 출처이면 막을 것이 없다. */
  function localUp() {
    if (local !== null) return Promise.resolve(local);
    if (!/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)) {
      local = false;
      return Promise.resolve(false);
    }
    var ctl = window.AbortController ? new AbortController() : null;
    var t = ctl ? setTimeout(function () { ctl.abort(); }, 1500) : 0;
    return fetch("/ping", { signal: ctl && ctl.signal, cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { local = !!(j && j.ok); return local; })
      .catch(function () { local = false; return false; })
      .finally(function () { clearTimeout(t); });
  }

  function localURL(meta) {
    return "/file?p=" + encodeURIComponent(meta.p.join("/"));
  }

  function show(src, meta) {
    say("PDF 를 여는 중… <small>" + esc(meta.n) + " · " + meta.mb + " MB</small>");
    return lib().then(function (m) {
      if (blob) { URL.revokeObjectURL(blob); blob = null; }
      var url = src;
      if (typeof src !== "string") { blob = URL.createObjectURL(src); url = blob; }
      return m.getDocument({ url: url }).promise;
    }).then(function (d) {
      doc = d; page = 1;
      el.num.textContent = d.numPages;
      el.nav.style.visibility = "visible";
      render();
    });
  }

  /* 폴더 고르기 — 반드시 사용자가 누른 직후에만 부른다. */
  var wanted = null;
  function pick() {
    window.showDirectoryPicker({ id: "ncs-org", mode: "read" })
      .then(function (h) { root = h; return saveRoot(h); })
      .then(function () { if (wanted) open(wanted); })
      .catch(function (e) {
        if (e && e.name === "AbortError") return;
        say("<b>폴더를 열지 못했습니다.</b><br>" + esc(e && e.message));
      });
  }

  /* 폴더는 그대로인데 브라우저가 권한만 잊은 경우 — 다시 고를 필요는 없다. */
  function grant() {
    loadRoot().then(function (h) {
      if (!h) return pick();
      return h.requestPermission({ mode: "read" }).then(function (st) {
        if (st !== "granted") return say("<b>권한을 주지 않으면 열 수 없습니다.</b>");
        root = h;
        if (wanted) open(wanted);
      });
    }).catch(function () { pick(); });
  }

  function askGrant(meta) {
    say('<b>폴더 읽기 권한을 다시 확인해 주세요.</b>' +
      '<p>브라우저를 다시 열면 권한이 초기화됩니다. 폴더는 기억하고 있으니 ' +
      '허용만 누르면 됩니다.</p>' +
      '<p class="pv-row"><button type="button" class="pv-b" data-a="grant">허용</button>' +
      '<button type="button" class="pv-b" data-a="pick">다른 폴더 고르기</button></p>');
  }

  /* Chrome/Edge 가 아니면 폴더 고르기를 못 한다 — 로컬 서버 쪽만 안내한다. */
  function askServer(meta) {
    say('<b>이 브라우저는 폴더 열기를 지원하지 않습니다.</b>' +
      '<p>조직 폴더에서 아래를 실행하고 <code>http://127.0.0.1:8765/</code> 로 ' +
      '들어가면 어느 브라우저에서든 PDF 가 바로 열립니다.</p>' +
      '<p><code>python COURSE-MANAGEMENT/tools/pdf-server.py</code></p>' +
      '<p class="pv-row">' +
      '<a class="pv-b" href="' + (window.CM_BASE || "") + 'tools/pdf-server.py" download>서버 내려받기</a>' +
      (ncsLink(meta) ? ' <a class="pv-b" href="' + esc(ncsLink(meta)) +
        '">ncs.go.kr 에서 받기</a>' : "") + '</p>');
  }

  function askFolder(meta) {
    say('<b>PDF 를 어디서 읽을지 한 번만 정해 주세요.</b>' +
      '<p>학습모듈은 <b>공공누리 제2유형</b>(출처표시·상업적 이용 금지)이고, 그 안에 ' +
      '국가가 저작재산권을 갖지 않은 도표·사진이 섞여 있어 배포·공중송신에 원작자 동의가 ' +
      '필요합니다. 그래서 원문을 사이트에 올려 두지 않고, 이 PC 에 받아 둔 파일을 ' +
      '그대로 엽니다 — 읽기만 하고 어디로도 보내지 않습니다.</p>' +

      '<p><b>1. 지금 바로</b> — 폴더를 고르면 이 브라우저가 기억해서 다음부터 ' +
      '묻지 않습니다. <code>' + esc(meta.p[0]) + '</code> 이 들어 있는 <b>상위 폴더</b>를 ' +
      '고르세요.</p>' +
      '<p class="pv-row"><button type="button" class="pv-b" data-a="pick">폴더 고르기</button>' +
      (ncsLink(meta) ? ' <a class="pv-b" href="' + esc(ncsLink(meta)) +
        '">ncs.go.kr 에서 받기</a>' : "") + '</p>' +

      '<p><b>2. 아예 묻지 않게</b> — 조직 폴더에서 아래를 실행하고 ' +
      '<code>http://127.0.0.1:8765/</code> 로 들어가면 폴더도 안 묻습니다. ' +
      '(지금 보고 계신 주소로는 브라우저가 내 PC 접속을 막아서 안 됩니다.)</p>' +
      '<p><code>python COURSE-MANAGEMENT/tools/pdf-server.py</code></p>' +
      '<p class="pv-row">' +
      '<a class="pv-b" href="' + (window.CM_BASE || "") + 'tools/pdf-server.py" download>서버 내려받기</a></p>');
  }

  function open(code) {
    build();
    var meta = (window.CM_PDF || {})[code];
    el.wrap.classList.add("on");
    document.body.style.overflow = "hidden";
    el.nav.style.visibility = "hidden";
    if (!meta) { el.title.textContent = "학습모듈"; return say("<b>이 능력단위에는 학습모듈이 없습니다.</b>"); }
    el.title.textContent = meta.n.replace(/\.pdf$/i, "");
    wanted = code;

    say("여는 중…");
    localUp().then(function (up) {
      if (up) return "local";                    // 서버가 떠 있으면 폴더는 건너뛴다
      if (!supported()) return "nofs";           // 폴더 열기가 안 되는 브라우저
      if (root) return root;
      return loadRoot().then(function (h) {
        if (!h) return null;
        return perm(h).then(function (st) {
          if (st === "granted") return h;
          return st === "prompt" ? "ask" : null;
        });
      });
    })
      .then(function (h) {
        if (h === "local") return localURL(meta);
        if (h === "nofs") { askServer(meta); return null; }
        if (h === "ask") { askGrant(meta); return null; }
        if (!h) { askFolder(meta); return null; }
        root = h;
        return resolve(h, meta.p).then(function (fh) { return fh.getFile(); });
      })
      .then(function (src) { if (src) return show(src, meta); })
      .catch(function (e) {
        // 서버는 떠 있는데 그 폴더에 파일이 없을 수 있다 — 조용히 폴더 쪽으로 물러난다
        if (local) { local = false; return open(code); }
        var miss = e && (e.name === "NotFoundError" || e.name === "TypeMismatchError");
        say("<b>" + (miss ? "그 폴더에서 파일을 찾지 못했습니다." : "파일을 열지 못했습니다.") + "</b>" +
          '<p><code>' + esc(meta.p.join("/")) + '</code></p>' +
          (miss ? "<p>고른 폴더가 다를 수 있습니다. 다시 골라 보세요.</p>"
                : "<p>" + esc(e && e.message) + "</p>") +
          '<p class="pv-row"><button type="button" class="pv-b" data-a="pick">폴더 다시 고르기</button>' +
          (ncsLink(meta) ? ' <a class="pv-b" href="' + esc(ncsLink(meta)) +
            '">ncs.go.kr 에서 받기</a>' : "") + '</p>');
      });
  }

  window.CM_PDFVIEW = { open: open };
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-pdf]");
    if (!a) return;
    e.preventDefault();
    open(a.getAttribute("data-pdf"));
  });
})();
