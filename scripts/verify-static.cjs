/* Static project has no build step: check every shipped JS and inline executable script. */
const fs = require("node:fs"),
  vm = require("node:vm");
let n = 0;
for (const f of [
  "index.html",
  "intro.html",
  "books.js",
  "intro.js",
  "lazy/admin.js",
  "lazy/acad.js",
  "lazy/tset.js",
  "lazy/omr-report.js",
  "lib/academy-core.js",
  "lib/korean-editor.js",
  "sw.js",
]) {
  const s = fs.readFileSync(f, "utf8");
  if (f.endsWith(".html")) {
    for (const m of s.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
      if (
        /\bsrc\s*=/.test(m[1]) ||
        /type\s*=\s*["']application\/ld\+json/.test(m[1])
      )
        continue;
      new vm.Script(m[2], { filename: f + ":inline-" + ++n });
    }
  } else {
    new vm.Script(s, { filename: f });
    n++;
  }
}
console.log("PASS " + n + " executable scripts parsed");
