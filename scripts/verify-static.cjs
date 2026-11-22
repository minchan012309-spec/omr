/* Static project has no build step: check every shipped JS and inline executable script. */
const fs = require("node:fs"),
  vm = require("node:vm");
let n = 0;
for (const f of [
  "index.html",
  "intro.html",
  "books.js",
  "intro.js",
  "lead.js",
  "dev.js",
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
// 병합 충돌 표시가 배포 파일에 남으면 서비스 워커·앱이 통째로 멈춘다
{
  const bad = [];
  const walk = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      if (["node_modules", ".git", "backups"].includes(e.name)) continue;
      const p = d === "." ? e.name : d + "/" + e.name;
      if (e.isDirectory()) walk(p);
      else if (/\.(html|js|cjs|css|json|sql|webmanifest)$/.test(e.name) && fs.statSync(p).size < 4e6) {
        if (/^(<<<<<<<|>>>>>>>) /m.test(fs.readFileSync(p, "utf8"))) bad.push(p);
      }
    }
  };
  walk(".");
  if (bad.length) throw new Error("merge conflict markers in: " + bad.join(", "));
}
console.log("PASS " + n + " executable scripts parsed, no merge conflict markers");
