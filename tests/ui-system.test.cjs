const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
/* legacy.css 는 토큰 바로 다음: 새 디자인 층(base → shell → components → screens)이 legacy 를 덮는다 */
const files = ['tokens.css', 'legacy.css', 'base.css', 'shell.css', 'components.css', 'screens.css'];

test('external UI styles are linked in a stable cascade and cached', () => {
  const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const sw = fs.readFileSync(path.join(root, 'sw.js'), 'utf8');
  let last = -1;
  for (const file of files) {
    assert.ok(fs.existsSync(path.join(root, 'styles', file)), `${file} exists`);
    const href = `styles/${file}`;
    const link = html.match(new RegExp(`<link rel="stylesheet" href="(${href.replace('.', '\\.')}(?:\\?v=\\d+)?)">`));
    assert.ok(link, `${file} is linked`);
    assert.ok(html.indexOf(link[0]) > last, `${file} linked in order`);
    assert.ok(sw.includes(`'${link[1]}'`), `${link[1]} is precached with the same version as index.html`);
    last = html.indexOf(link[0]);
  }
});

test('tokens and shared components expose the rebuild contract', () => {
  const css = files.map(file => fs.readFileSync(path.join(root, 'styles', file), 'utf8')).join('\n');
  for (const token of ['--ui-ground', '--ui-surface', '--ui-raised', '--ui-border', '--ui-text', '--ui-muted', '--ui-accent', '--ui-accent-soft', '--ui-radius-panel', '--ui-radius-control']) {
    assert.match(css, new RegExp(token));
  }
  for (const className of ['app-shell', 'screen-head', 'ui-panel', 'metric-strip', 'ui-segment', 'status-pill', 'ui-empty', 'ui-actions']) {
    assert.match(css, new RegExp(`\\.${className}\\b`));
  }
});

test('obsolete override and glass layers are absent from production markup', () => {
  const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  assert.doesNotMatch(html, /id="(?:shellcss|polishcss|tidycss)"/);
  assert.doesNotMatch(html, /data-glass/);
  assert.doesNotMatch(html, /backdrop-filter/);
  assert.doesNotMatch(html, /유리 효과/);
  assert.doesNotMatch(html, /glass(?:Sync|Cycle|RowHtml)\b/);
  assert.doesNotMatch(html, /id="(?:sbGl|lg-refract)"/);
});
