const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");

test("busy overlay fills one straight bar from left to right", () => {
  const html = fs.readFileSync("index.html", "utf8");
  const css = fs.readFileSync("styles/legacy.css", "utf8");

  assert.match(html, /querySelector\('\.bring i'\).*style\.width/);
  assert.doesNotMatch(css, /@keyframes bslide|animation:bslide|infinite alternate/);
  assert.match(css, /#busy \.bring i\{[^}]*width:0[^}]*transition:width/);
});
