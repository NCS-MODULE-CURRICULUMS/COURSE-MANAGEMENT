/* 학습모듈 PDF 보기 — 모달로 띄운다.
 *
 * PDF 원문은 한국직업능력연구원 저작물이라 이 저장소에 없다(291개 3.0GB).
 * 대신 강사 PC 에 받아 둔 파일을 브라우저가 직접 연다.
 *
 *   [PDF] 를 처음 누르면  → 조직 폴더를 한 번 고른다 (TMP_NCS_20260916 같은 상위 폴더)
 *   그 다음부터        → 고른 폴더를 기억해 바로 열린다
 *   폴더가 없거나 브라우저가 못 하면 → ncs.go.kr 에서 받는 길을 보여 준다
 *
 * 폴더 권한은 브라우저가 관리한다. 파일은 읽기만 하고 어디로도 보내지 않는다.
 * 쓰는 것 : window.CM_PDF (assets/modules-pdf.js) · assets/pdfjs/ (vendored pdf.js)
 */
(function () {
  "use strict";

  var DB = "ncs-pdf", STORE = "h", KEY = "root";
  var NCS = "https://www.ncs.go.kr/unity/hth01/hth0101/downloadFile.do";
  var pdfjs = null, root = null, task = null, doc = null, blob = null;
  var page = 1, scale = 1.2, rendering = false, pending = null;

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
    if (!doc || rendering) { pending = page; return; }
    rendering = true;
    doc.getPage(page).then(function (pg) {
      var vp = pg.getViewport({ scale: scale * (window.devicePixelRatio || 1) });
      el.cv.width = vp.width; el.cv.height = vp.height;
      el.cv.style.width = (vp.width / (window.devicePixelRatio || 1)) + "px";
      el.msg.style.display = "none";
      el.cv.style.display = "";
      task = pg.render({ canvasContext: el.cv.getContext("2d"), viewport: vp });
      return task.promise;
    }).then(function () {
      rendering = false;
      el.cur.textContent = page;
      if (pending !== null && pending !== page) { page = pending; pending = null; render(); }
      else pending = null;
    }).catch(function (e) {
      rendering = false;
      if (e && e.name === "RenderingCancelledException") return;
      say("<b>이 쪽을 그리지 못했습니다.</b><br>" + esc(e && e.message));
    });
  }

  function go(n) {
    if (!doc) return;
    n = Math.max(1, Math.min(doc.numPages, n));
    if (n === page) return;
    page = n;
    if (task) { try { task.cancel(); } catch (e) {} }
    render();
  }
  function zoom(d) {
    scale = Math.max(0.5, Math.min(4, scale + d));
    if (task) { try { task.cancel(); } catch (e) {} }
    render();
  }

  function show(file, meta) {
    say("PDF 를 여는 중… <small>" + esc(meta.n) + " · " + meta.mb + " MB</small>");
    return lib().then(function (m) {
      if (blob) URL.revokeObjectURL(blob);
      blob = URL.createObjectURL(file);
      return m.getDocument({ url: blob }).promise;
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

  function askFolder(meta) {
    say('<b>PDF 가 있는 폴더를 한 번 알려 주세요.</b>' +
      '<p>학습모듈 원문은 한국직업능력연구원 저작물이라 이 사이트에 올려 두지 않습니다. ' +
      '대신 이 PC 에 받아 둔 파일을 그대로 엽니다 — 읽기만 하고 어디로도 보내지 않습니다.</p>' +
      '<p>커리큘럼 저장소들을 담고 있는 <b>상위 폴더</b>를 고르세요 ' +
      '(<code>' + esc(meta.p[0]) + '</code> 이 들어 있는 폴더).</p>' +
      '<p class="pv-row"><button type="button" class="pv-b" data-a="pick">폴더 고르기</button>' +
      (ncsLink(meta) ? ' <a class="pv-b" href="' + esc(ncsLink(meta)) +
        '">ncs.go.kr 에서 받기</a>' : "") + '</p>');
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

    if (!supported()) {
      return say('<b>이 브라우저는 폴더 열기를 지원하지 않습니다.</b>' +
        '<p>Chrome 이나 Edge 에서 열면 PDF 를 바로 볼 수 있습니다. ' +
        '지금은 아래에서 원문을 받으세요.</p>' +
        (ncsLink(meta) ? '<p class="pv-row"><a class="pv-b" href="' + esc(ncsLink(meta)) +
          '">ncs.go.kr 에서 받기</a></p>' : ""));
    }

    say("여는 중…");
    (root ? Promise.resolve(root)
          : loadRoot().then(function (h) {
              if (!h) return null;
              return perm(h).then(function (st) {
                if (st === "granted") return h;
                return st === "prompt" ? "ask" : null;
              });
            }))
      .then(function (h) {
        if (h === "ask") { askGrant(meta); return null; }
        if (!h) { askFolder(meta); return null; }
        root = h;
        return resolve(h, meta.p).then(function (fh) { return fh.getFile(); });
      })
      .then(function (file) { if (file) return show(file, meta); })
      .catch(function (e) {
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
