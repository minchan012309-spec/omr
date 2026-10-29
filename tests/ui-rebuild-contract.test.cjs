const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const screens = fs.readFileSync(path.join(__dirname, '..', 'styles', 'screens.css'), 'utf8');

test('core workflow renderers keep public behavior hooks and new composition', () => {
  for (const fn of ['enterView', 'entryShellHtml', 'entryRoleSet', 'startView', 'weakView', 'stuView']) {
    assert.match(html, new RegExp(`function ${fn}\\(`), `${fn} is available`);
  }
  for (const cls of ['entry-shell', 'screen-head', 'workflow-grid', 'student-list', 'student-row']) {
    assert.match(html + screens, new RegExp(cls), `${cls} is composed`);
  }
  for (const action of ['openByNumber', 'quickPractice', 'stuAdd', 'setStu', 'bGo']) {
    assert.match(html, new RegExp(`${action}\\(`), `${action} remains wired`);
  }
});

test('entry roles and responsive contracts are explicit', () => {
  for (const role of ['teacher', 'student', 'parent']) assert.match(html, new RegExp(`'${role}'`));
  assert.match(screens, /@media\(max-width:900px\)/);
  assert.match(screens, /@media\(max-width:600px\)/);
});
