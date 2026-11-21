/* 물질과 에너지 개념 정리(bank/concept.json)에 이스케이프된 HTML · 날 문자열이 남지 않았는지 확인한다.
   그림 · 표 · 강조를 본문처럼 다시 이스케이프하면 개념학습 화면에 태그 글자가 그대로 보인다. */
const assert = require("node:assert/strict");
const fs = require("node:fs");

const concept = JSON.parse(fs.readFileSync("bank/concept.json", "utf8"));
for (const sec of concept.secs) {
  const h = sec.html;
  assert.doesNotMatch(h, /&lt;\/?(?:div|table|thead|tbody|tr|td|th|img|span|math|m[a-z]+|p|colgroup|col)\b/, `${sec.id}: 이스케이프된 태그가 남아 있다`);
  assert.doesNotMatch(h, /-&gt;|<=>|->/, `${sec.id}: 화살표가 →로 바뀌지 않았다`);
  assert.doesNotMatch(h, /\\(?:frac|Delta|times|text|left|right)\b/, `${sec.id}: TeX 명령이 수식으로 바뀌지 않았다`);
  assert.doesNotMatch(h, /<mi[^>]*>[A-Za-z0-9]*_\d/, `${sec.id}: \\mathrm 안의 아래 첨자가 밑줄 글자로 남아 있다`);
  assert.doesNotMatch(h, /\u0000/, `${sec.id}: 자리표시가 남아 있다`);
  assert.doesNotMatch(h, /<p>\s*<div/, `${sec.id}: 그림 · 표가 <p> 안에 들어 있다`);
}
const rate = concept.secs.find((s) => s.title.includes("반응 속도식") && s.html.includes("연습 1"));
assert.ok(rate, "반응 속도식 연습 절이 있어야 한다");
assert.match(rate.html, /<div class="tbw"><table class="tb">/, "연습 표는 실제 표로 들어가야 한다");
console.log("PASS me concept html has no escaped tags or raw TeX");
