const assert = require("node:assert/strict");
const fs = require("node:fs");

const concept = JSON.parse(fs.readFileSync("hl/concept.json", "utf8"));
const pages = concept.secs.map((section) => section.html).join("\n");

assert.match(
  pages,
  /<p class="kp">/,
  "개념 본문은 긴 줄글 대신 짧은 개조식 항목으로 표시해야 한다",
);

assert.match(
  pages,
  /원리 더하기/,
  "원리 더하기 보조 설명은 개념서에서 유지해야 한다",
);
assert.doesNotMatch(
  pages,
  /\[\[[^\]]+\]\]|_{3,}|<span class="bk">\s*<\/span>/,
  "개념서 본문에는 채워지지 않은 빈칸이 남으면 안 된다",
);
assert.doesNotMatch(
  pages,
  /<td[^>]*>\s*<\/td>|〃|\/\//,
  "표의 반복 항목은 비우거나 기호로 줄이지 말고 내용을 적어야 한다",
);

const spelling = concept.secs
  .filter((section) => section.sub === "Ⅲ-A" || section.sub === "Ⅲ-B" || section.sub === "Ⅲ-C")
  .map((section) => section.html)
  .join("\n");
for (const fact of [
  "한글 맞춤법의 구성",
  "표준어를 소리대로 적되",
  "어법에 맞도록",
  "문장의 각 단어는",
  "조사는",
]) {
  assert.match(spelling, new RegExp(fact), `핑크 교재의 핵심 내용 누락: ${fact}`);
}

console.log("PASS Korean concept content is complete and follows the pink textbook core");
