/* Korean manuscript editor: structured plain text, isolated A4 HTML, no executable imported markup. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.KoreanEditor = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const kinds = {
      concept: "개념 설명",
      summary: "핵심 정리",
      example: "예문 분석",
      passage: "지문 · 작품",
      question: "적용 문제",
      table: "문법 · 비교표",
      teacher: "교사용 해설",
    },
    areas = ["화법", "언어", "독서", "문학"];
  const esc = (s) =>
    String(s == null ? "" : s).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const inline = (s) =>
    esc(s)
      .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
      .replace(/__([^_\n]+)__/g, "<u>$1</u>");
  function validate(input) {
    if (
      !input ||
      typeof input !== "object" ||
      !Array.isArray(input.blocks) ||
      input.blocks.length > 200
    )
      throw new Error("원고 형식을 확인해 주세요 (최대 200개 블록)");
    const text = (v, n) => {
      if (v != null && typeof v !== "string")
        throw new Error("문자열 형식이 아니에요");
      const s = v || "";
      if (s.length > n) throw new Error("입력 분량이 너무 길어요");
      return s;
    };
    return {
      title: text(input.title, 150),
      layout: input.layout === "kice" ? "kice" : "school",
      paragraphs: !!input.paragraphs,
      lines: !!input.lines,
      blocks: input.blocks.map((b) => {
        if (!b || !Object.hasOwn(kinds, b.kind))
          throw new Error("지원하지 않는 블록이에요");
        return {
          kind: b.kind,
          area: areas.includes(b.area) ? b.area : "언어",
          title: text(b.title, 200),
          body: text(b.body, 30000),
          box: text(b.box, 10000),
          choices: text(b.choices, 10000),
          answer: text(b.answer, 10000),
          teacher: text(b.teacher, 10000),
          pageBreak: !!b.pageBreak,
        };
      }),
    };
  }
  function render(input, edition, base) {
    const d = validate(input),
      teach = edition === "teacher";
    base = String(base || "").replace(/[<>"']/g, "");
    let qn = 0;
    const content = d.blocks
      .filter((b) => teach || b.kind !== "teacher")
      .map((b) => {
        let body = "";
        if (b.kind === "table") {
          const rows = b.body
            .split("\n")
            .filter((x) => x.trim())
            .map((x) => x.split(/\t|\|/).slice(0, 8));
          body =
            "<table><thead><tr>" +
            (rows[0] || []).map((c) => "<th>" + inline(c) + "</th>").join("") +
            "</tr></thead><tbody>" +
            rows
              .slice(1)
              .map(
                (r) =>
                  "<tr>" +
                  r.map((c) => "<td>" + inline(c) + "</td>").join("") +
                  "</tr>",
              )
              .join("") +
            "</tbody></table>";
        } else if (b.kind === "question") {
          body =
            "<p>" +
            inline(b.body).replace(/\n/g, "<br>") +
            "</p>" +
            (b.box
              ? '<aside class="given"><b>〈보기〉</b><p>' +
                inline(b.box).replace(/\n/g, "<br>") +
                "</p></aside>"
              : "") +
            '<ol class="choices">' +
            b.choices
              .split("\n")
              .filter((x) => x.trim())
              .map(
                (c, i) =>
                  "<li><span>" +
                  esc("①②③④⑤⑥⑦⑧⑨⑩"[i] || String(i + 1)) +
                  "</span>" +
                  inline(c) +
                  "</li>",
              )
              .join("") +
            "</ol>";
        } else {
          body = b.body
            .split("\n")
            .map(
              (p, i) =>
                '<p class="' +
                (b.kind === "passage" && b.area === "문학" ? "verse" : "") +
                '">' +
                (b.kind === "passage" && (d.paragraphs || d.lines)
                  ? '<span class="ln">' +
                    (d.paragraphs ? "[" + (i + 1) + "] " : "") +
                    (d.lines ? "행 " + (i + 1) + " " : "") +
                    "</span>"
                  : "") +
                inline(p || "\u00a0") +
                "</p>",
            )
            .join("");
        }
        return (
          '<section class="block ' +
          b.kind +
          (b.pageBreak ? " new-page" : "") +
          '"><div class="area">' +
          esc(b.area) +
          " · " +
          kinds[b.kind] +
          "</div><h2>" +
          (b.kind === "question" ? ++qn + ". " : "") +
          inline(b.title || kinds[b.kind]) +
          "</h2>" +
          body +
          (teach && (b.teacher || b.answer)
            ? '<aside class="explanation"><b>정답 · 지도 도움말</b><p>' +
              inline([b.answer, b.teacher].filter(Boolean).join("\n")).replace(
                /\n/g,
                "<br>",
              ) +
              "</p></aside>"
            : "") +
          "</section>"
        );
      })
      .join("");
    return (
      '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' +
      esc(d.title || "국어 교재") +
      "</title><style>" +
      `@font-face{font-family:PrintKorean;src:url('${base}fonts/Pretendard-Regular.woff2')}@font-face{font-family:PrintKorean;src:url('${base}fonts/Pretendard-Bold.woff2');font-weight:700}@font-face{font-family:YetHangul;src:url('${base}fonts/KoPubDotum-Medium.subset.woff2');unicode-range:U+1100-11FF,U+A960-A97F,U+D7B0-D7FF,U+3165-318E,U+302E-302F}
@font-face{font-family:SolviSymbols;src:url('${base}fonts/SolviSymbols.woff2');unicode-range:U+2300-24FF,U+3200-32FF}@page{size:A4;margin:17mm 15mm 18mm}*{box-sizing:border-box}html{color-scheme:light;background:#e7e9ec}body{font:11pt/1.8 YetHangul,SolviSymbols,PrintKorean,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#18202c;background:#fff;width:210mm;min-height:297mm;margin:0 auto;padding:17mm 15mm 18mm;overflow-wrap:anywhere;word-break:keep-all}header{padding-bottom:8mm}h1{font-size:25pt;line-height:1.35;margin:0 0 3mm}header p{margin:0;color:#4a5360;font-size:10pt}h2{font-size:14pt;line-height:1.5;margin:0 0 3mm;break-after:avoid}.area{font-size:9pt;color:#4a5360;margin:0 0 1mm;break-after:avoid}.block{margin:0 0 9mm}.block p{margin:0 0 2.5mm;orphans:3;widows:3;white-space:pre-wrap}.passage p{text-align:justify;text-indent:1em}.passage .verse{text-align:left;text-indent:0;line-height:2}.ln{font-size:8pt;color:#5b6470;margin-right:2mm}.summary,.example,.explanation{background:#f4f6f8;padding:4mm}.given{border:1px solid #7a8390;padding:3mm;margin:4mm 0}.given b{display:block;text-align:center}.choices{list-style:none;padding:0;margin:3mm 0}.choices li{display:flex;gap:2mm;margin-bottom:1.5mm;break-inside:avoid}.choices span{flex:none}.explanation{margin-top:4mm;font-size:10pt}table{width:100%;border-collapse:collapse;font-size:10pt;table-layout:fixed}th,td{border:1px solid #9ba4af;padding:2mm;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#eef1f5}thead{display:table-header-group}tr{break-inside:avoid}u{text-underline-offset:3px}.new-page{break-before:page}.kice .question{font-size:10.5pt}.kice .passage{font-size:11pt;line-height:1.95}@media print{html{background:#fff}body{width:auto;min-height:0;margin:0;padding:0;print-color-adjust:exact;-webkit-print-color-adjust:exact}}` +
      '</style></head><body class="' +
      d.layout +
      '"><header><h1>' +
      esc(d.title || "국어 교재") +
      "</h1><p>Solvi · " +
      (d.layout === "kice" ? "평가원형" : "내신형") +
      " · " +
      (teach ? "교사용" : "학생용") +
      "</p></header>" +
      content +
      "</body></html>"
    );
  }
  let state = null,
    active = 0,
    timer,
    stateOwner = null;
  const $ = (s) => document.querySelector(s),
    key = () =>
      "solvi_korean_editor_v1:" +
      (typeof acctCur === "function" ? acctCur() || "local" : "local");
  const fresh = () => ({
    title: "새 국어 교재",
    layout: "school",
    paragraphs: true,
    lines: false,
    blocks: [
      {
        kind: "concept",
        area: "언어",
        title: "개념 설명",
        body: "",
        teacher: "",
        answer: "",
        choices: "",
        box: "",
      },
    ],
  });
  function open() {
    if (typeof teacher === "function" && !teacher()) return;
    if (!state || stateOwner !== key()) {
      stateOwner = key();
      active = 0;
      try {
        state = validate(JSON.parse(localStorage.getItem(key()) || "null"));
      } catch (e) {
        state = fresh();
      }
    }
    active = Math.min(active, Math.max(0, state.blocks.length - 1));
    draw();
  }
  function draw() {
    const b = state.blocks[active],
      f = (label, k, type) =>
        "<label>" +
        label +
        "<" +
        (type === "textarea" ? "textarea" : "input") +
        ' data-ko="' +
        k +
        '" ' +
        (type === "textarea" ? 'rows="5"' : 'value="' + esc(b[k] || "") + '"') +
        ">" +
        (type === "textarea" ? esc(b[k] || "") + "</textarea>" : "") +
        "</label>";
    $("#main").innerHTML =
      '<style>.ko-shell{display:grid;grid-template-columns:minmax(280px,420px) minmax(0,1fr);gap:20px}.ko-tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.ko-edit label{display:grid;gap:5px;margin-bottom:12px;color:var(--t);font-size:13px}.ko-edit textarea{padding:10px!important;min-height:90px;width:100%;font:inherit;line-height:1.7}.ko-preview{background:var(--sf2);overflow:auto;min-height:700px;padding:12px}.ko-preview iframe{display:block;width:794px;height:1123px;border:0;transform-origin:0 0;background:#fff}.ko-edit input,.ko-edit select{width:100%}.ko-blocks{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}.ko-blocks button[aria-pressed=true]{background:var(--b);color:var(--bg)}@media(max-width:900px){.ko-shell{grid-template-columns:1fr}.ko-preview{min-height:550px}}</style><div class="tsh"><div><h1>국어 원고 편집</h1><p>화법·언어·독서·문학을 한 권으로 구성해요. 이 기기에 저장되며 JSON으로 백업할 수 있어요.</p></div><button class="s" onclick="KoreanEditor.close()">교재함</button></div><div class="ko-tools"><button class="p" onclick="KoreanEditor.save()">원고 저장</button><button class="s" onclick="KoreanEditor.exportFile()">JSON 백업</button><label class="s">JSON 가져오기<input type="file" accept="application/json,.json" hidden onchange="KoreanEditor.importFile(this.files[0])"></label><button class="s" onclick="KoreanEditor.print()">인쇄 · PDF 저장</button><button class="s" onclick="KoreanEditor.download()">HTML 내려받기</button><span id="ko-status" role="status"></span></div><div class="ko-shell"><div class="card ko-edit"><label>교재 제목<input id="ko-title" value="' +
      esc(state.title) +
      '"></label><label>출력 서식<select id="ko-layout"><option value="school" ' +
      (state.layout === "school" ? "selected" : "") +
      '>내신형</option><option value="kice" ' +
      (state.layout === "kice" ? "selected" : "") +
      '>평가원형</option></select></label><label>미리보기 · 출력 버전<select id="ko-edition"><option value="student">학생용 (해설 제외)</option><option value="teacher">교사용 (해설 포함)</option></select></label><label class="chk"><span><input id="ko-paragraphs" type="checkbox" ' +
      (state.paragraphs ? "checked" : "") +
      '> 지문 문단 번호</span></label><label class="chk"><span><input id="ko-lines" type="checkbox" ' +
      (state.lines ? "checked" : "") +
      '> 원문 행 번호 (입력 줄바꿈 기준)</span></label><div class="ko-blocks">' +
      state.blocks
        .map(
          (x, i) =>
            '<button class="s sm" aria-pressed="' +
            (i === active) +
            '" onclick="KoreanEditor.select(' +
            i +
            ')">' +
            (i + 1) +
            " " +
            esc(x.title || kinds[x.kind]) +
            "</button>",
        )
        .join("") +
      '</div><div class="ko-tools"><select id="ko-add-kind" aria-label="추가할 블록">' +
      Object.entries(kinds)
        .map(([k, v]) => '<option value="' + k + '">' + v + "</option>")
        .join("") +
      '</select><button class="s" onclick="KoreanEditor.add()">블록 추가</button></div>' +
      (b
        ? '<label>영역<select data-ko="area">' +
          areas
            .map(
              (a) =>
                "<option " +
                (a === b.area ? "selected" : "") +
                ">" +
                a +
                "</option>",
            )
            .join("") +
          "</select></label>" +
          f("제목", "title") +
          f(
            b.kind === "table"
              ? "표: 첫 줄은 머리글, 열은 | 또는 탭으로 구분"
              : "본문: **굵게**, __밑줄__, 줄바꿈 유지",
            "body",
            "textarea",
          ) +
          (b.kind === "question"
            ? f("보기", "box", "textarea") +
              f("선택지 (한 줄에 하나)", "choices", "textarea") +
              f("정답 · 해설 (교사용)", "answer", "textarea")
            : "") +
          f("지도 메모 (교사용)", "teacher", "textarea") +
          '<label class="chk"><span><input data-ko="pageBreak" type="checkbox" ' +
          (b.pageBreak ? "checked" : "") +
          '> 새 쪽에서 시작</span></label><div class="ko-tools"><button class="s" onclick="KoreanEditor.move(-1)" ' +
          (active ? "" : "disabled") +
          '>위로</button><button class="s" onclick="KoreanEditor.move(1)" ' +
          (active < state.blocks.length - 1 ? "" : "disabled") +
          '>아래로</button><button class="s" onclick="KoreanEditor.remove()">블록 삭제</button></div>'
        : "<p>블록을 추가해 주세요.</p>") +
      '</div><div class="ko-preview"><iframe id="ko-preview" title="A4 국어 교재 미리보기" sandbox="allow-same-origin allow-modals"></iframe></div></div>';
    $("#main")
      .querySelectorAll(
        "[data-ko],#ko-title,#ko-layout,#ko-edition,#ko-paragraphs,#ko-lines",
      )
      .forEach((e) =>
        e.addEventListener("input", () => {
          read();
          clearTimeout(timer);
          timer = setTimeout(preview, 180);
        }),
      );
    preview();
  }
  function read() {
    if (!state) return;
    state.title = $("#ko-title").value;
    state.layout = $("#ko-layout").value;
    state.paragraphs = $("#ko-paragraphs").checked;
    state.lines = $("#ko-lines").checked;
    const b = state.blocks[active];
    if (b)
      $("#main")
        .querySelectorAll("[data-ko]")
        .forEach(
          (e) =>
            (b[e.dataset.ko] = e.type === "checkbox" ? e.checked : e.value),
        );
  }
  const base = () => location.origin + location.pathname.replace(/[^/]*$/, "");
  function html() {
    read();
    return render(state, ($("#ko-edition") || {}).value || "student", base());
  }
  function preview() {
    const f = $("#ko-preview");
    if (!f) return;
    try {
      f.srcdoc = html();
      const parent = f.parentElement,
        s = Math.min(1, (parent.clientWidth - 24) / 794);
      f.style.transform = "scale(" + s + ")";
      parent.style.height = 1123 * s + 24 + "px";
      parent.style.minHeight = "0";
      $("#ko-status").textContent =
        "미리보기 반영됨 · 저장 버튼으로 보관해 주세요";
    } catch (e) {
      $("#ko-status").textContent = e.message;
    }
  }
  function save() {
    read();
    try {
      state = validate(state);
      localStorage.setItem(key(), JSON.stringify(state));
      $("#ko-status").textContent = "이 기기에 저장했어요";
      return true;
    } catch (e) {
      toast("저장하지 못했어요: " + e.message);
      return false;
    }
  }
  function select(i) {
    read();
    active = i;
    draw();
  }
  function add() {
    read();
    if (state.blocks.length >= 200) {
      toast("블록은 200개까지 넣을 수 있어요");
      return;
    }
    const kind = $("#ko-add-kind").value;
    state.blocks.push({ kind, area: "언어", title: kinds[kind], body: "" });
    active = state.blocks.length - 1;
    draw();
  }
  function move(d) {
    read();
    const j = active + d;
    if (j < 0 || j >= state.blocks.length) return;
    [state.blocks[active], state.blocks[j]] = [
      state.blocks[j],
      state.blocks[active],
    ];
    active = j;
    draw();
  }
  function remove() {
    read();
    if (!confirm("현재 블록을 삭제할까요?")) return;
    state.blocks.splice(active, 1);
    active = Math.max(0, active - 1);
    draw();
  }
  function downloadBlob(content, type, name) {
    const u = URL.createObjectURL(new Blob([content], { type })),
      a = document.createElement("a");
    a.href = u;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(u), 3000);
  }
  function exportFile() {
    read();
    downloadBlob(
      JSON.stringify(validate(state), null, 2),
      "application/json",
      "국어원고.json",
    );
  }
  async function importFile(file) {
    if (!file) return;
    try {
      if (file.size > 3000000)
        throw new Error("3MB 이하 JSON만 가져올 수 있어요");
      const next = validate(JSON.parse(await file.text()));
      if (
        !confirm(
          "현재 편집 중인 원고를 가져온 파일로 바꿀까요? 저장한 JSON 백업은 유지돼요.",
        )
      )
        return;
      state = next;
      active = 0;
      draw();
    } catch (e) {
      toast("가져오지 못했어요: " + e.message);
    }
  }
  function print() {
    const h = html(),
      w = window.open("", "_blank");
    if (!w) {
      toast("인쇄 창의 팝업을 허용해 주세요");
      return;
    }
    w.document.write(h);
    w.document.close();
    Promise.all([
      w.document.fonts.ready,
      ...[...w.document.images].map((i) => i.decode().catch(() => {})),
    ]).then(() => {
      w.focus();
      w.print();
    });
  }
  function download() {
    downloadBlob(html(), "text/html;charset=utf-8", "국어교재.html");
  }
  function close() {
    if (!save()) return;
    state = null;
    BKV = { v: "shelf", id: null };
    bkShow();
  }
  return {
    validate,
    render,
    open,
    save,
    select,
    add,
    move,
    remove,
    exportFile,
    importFile,
    print,
    download,
    close,
  };
});
