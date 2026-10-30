/* One command: serve a disposable static fixture origin, run checks, then close it. */
const http = require("node:http"),
  fs = require("node:fs"),
  path = require("node:path"),
  { spawn } = require("node:child_process");
const root = path.resolve(__dirname, ".."),
  types = {
    ".html": "text/html;charset=utf-8",
    ".js": "text/javascript;charset=utf-8",
    ".css": "text/css;charset=utf-8",
    ".json": "application/json;charset=utf-8",
    ".woff2": "font/woff2",
    ".webp": "image/webp",
    ".png": "image/png",
    ".svg": "image/svg+xml",
  };
const server = http.createServer((req, res) => {
  try {
    if (!["GET", "HEAD"].includes(req.method)) {
      res.writeHead(405);
      return res.end();
    }
    const pathname = new URL(req.url, "http://fixture.local").pathname;
    const file = path.resolve(
      root,
      "." + decodeURIComponent(pathname === "/" ? "/index.html" : pathname),
    );
    if (!file.startsWith(root + path.sep)) {
      res.writeHead(403);
      return res.end();
    }
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
      res.writeHead(404);
      return res.end();
    }
    res.writeHead(200, {
      "Content-Type": types[path.extname(file)] || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    if (req.method === "HEAD") return res.end();
    fs.createReadStream(file).pipe(res);
  } catch (e) {
    res.writeHead(400);
    res.end();
  }
});
const run = (args, env) =>
  new Promise((resolve, reject) => {
    const p = spawn(process.execPath, args, {
      cwd: root,
      env: { ...process.env, ...env },
      stdio: "inherit",
    });
    p.once("error", reject);
    p.once("exit", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(args.join(" ") + " failed (" + code + ")")),
    );
  });
(async () => {
  try {
    await new Promise((resolve, reject) => {
      server.once("error", reject);
      server.listen(0, "127.0.0.1", resolve);
    });
    const env = { BASE: "http://127.0.0.1:" + server.address().port };
    for (const args of [
      ["scripts/verify-static.cjs"],
      ["--test", "tests/academy-core.test.cjs", "tests/korean-editor.test.cjs"],
      ["tests/operations-db.cjs"],
      ["tests/full-schema-db.cjs"],
      ["tests/leads-db.cjs"],
      ["tests/print-regression.cjs"],
      ["tests/korean-browser.cjs"],
      ["tests/book-pdf.cjs"],
      ["tests/admin-regression.cjs"],
      ["tests/intro-regression.cjs"],
    ])
      await run(args, env);
    console.log("PASS all isolated verification commands");
  } finally {
    await new Promise((r) => server.close(r));
  }
})().catch((e) => {
  console.error(e.message);
  process.exitCode = 1;
});
