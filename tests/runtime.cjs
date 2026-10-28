const fs = require("node:fs"),
  path = require("node:path"),
  os = require("node:os");
function resolvePackage(name, env, fallback) {
  if (process.env[env]) return process.env[env];
  try {
    return require.resolve(name);
  } catch (e) {
    return fallback;
  }
}
const pw = resolvePackage(
  "playwright",
  "PW",
  path.join(
    os.homedir(),
    ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright",
  ),
);
const pg = resolvePackage(
  "@electric-sql/pglite",
  "PGLITE",
  "/tmp/solvi-db-tests/node_modules/@electric-sql/pglite",
);
function browserOptions() {
  const mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  const executablePath =
    process.env.CHROME ||
    (process.platform === "darwin" && fs.existsSync(mac) ? mac : undefined);
  return { headless: true, ...(executablePath ? { executablePath } : {}) };
}
module.exports = {
  get chromium() {
    return require(pw).chromium;
  },
  browserOptions,
  get PGlite() {
    return require(pg).PGlite;
  },
  get pgcrypto() {
    let root = pg;
    while (!fs.existsSync(path.join(root, "package.json")))
      root = path.dirname(root);
    return require(path.join(root, "dist/contrib/pgcrypto.cjs")).pgcrypto;
  },
};
