# Solvi UI Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild Solvi's shared app UI and four core entry/work screens while preserving its static deployment, data contracts, print output and existing workflows.

**Architecture:** Keep the current vanilla HTML/JS runtime and public render functions, but move app styling into focused files under `styles/`. Introduce small HTML render helpers inside `index.html` for the unified login, worksheet start, weak-type and student-list compositions; those helpers consume the same globals and call the same actions as today. Protect the rewrite with static contract tests and Playwright fixtures that execute the production render functions.

**Tech Stack:** Static HTML, CSS custom properties, vanilla JavaScript, Node.js tests, Playwright, Taste Skill inspector.

**Spec:** `docs/superpowers/specs/2026-10-29-solvi-ui-rebuild-design.md`

## Global Constraints

- Keep the build-free static deployment and current public function names.
- Preserve localStorage/sessionStorage keys, Supabase RPCs, routes, print markup and generated document CSS.
- Keep Pretendard, Solvi navy/yellow, existing brand marks and the current SVG outline icon system.
- Touch targets are at least 44px on coarse pointers; body text is at least 14px; supporting text is at least 12px.
- App titles are 20–28px; resting surfaces have a border or tone step and no shadow.
- App chrome contains no emoji, page/card/button gradients, glass or backdrop blur.
- Progress/data gradients and print highlights may remain when they encode meaning.
- Back up original UI files with commit/status metadata and SHA-256 before product edits.

## Review Focus

- Logged-out role switching must preserve teacher, student, parent and number-grading entry paths without losing keyboard focus.
- Empty teacher accounts and all/class/student scopes must render useful first actions instead of blank grids.
- At 390px, navigation, filters, selected-type actions and student details must not produce page-level horizontal scrolling.
- Print/eBook/export markup must remain visually and structurally unaffected by app token changes.
- Service-worker caching must include the extracted CSS and stop serving stale inline-only layouts.

---

### Task 1: Recoverable source backup

**Files:**
- Modify: `.gitignore`
- Create: `tests/ui-backup.test.cjs`
- Create at execution time: `backups/ui-rebuild-2026-10-29/MANIFEST.txt`
- Copy at execution time: `index.html`, `intro.html`, `intro.css`, `intro.js`, `sw.js`, `tests/intro-regression.cjs`, `tests/runtime.cjs`

**Interfaces:**
- Produces: a byte-identical local backup whose `MANIFEST.txt` lists commit, branch, status and SHA-256 for every copied file.

- [ ] **Step 1: Write the failing backup contract test**

  Add `tests/ui-backup.test.cjs` asserting the backup directory exists, every required file exists, every manifest checksum matches its copied file, and `.gitignore` contains `backups/`.

- [ ] **Step 2: Run the test and verify RED**

  Run: `node --test tests/ui-backup.test.cjs`

  Expected: FAIL because the backup and ignore entry do not exist.

- [ ] **Step 3: Create the backup and manifest, then ignore it**

  Use explicit file paths, `cp -p`, `shasum -a 256`, `git rev-parse HEAD`, `git branch --show-current`, and `git status --short`. Add `backups/` to `.gitignore` with `apply_patch`.

- [ ] **Step 4: Run the backup test and verify GREEN**

  Run: `node --test tests/ui-backup.test.cjs`

  Expected: PASS.

### Task 2: External CSS architecture and token contract

**Files:**
- Create: `styles/tokens.css`
- Create: `styles/base.css`
- Create: `styles/shell.css`
- Create: `styles/components.css`
- Create: `styles/screens.css`
- Create: `styles/legacy.css`
- Modify: `index.html:28-1301`
- Modify: `sw.js`
- Create: `tests/ui-system.test.cjs`

**Interfaces:**
- Produces: CSS variables named `--ui-ground`, `--ui-surface`, `--ui-raised`, `--ui-border`, `--ui-text`, `--ui-muted`, `--ui-accent`, `--ui-accent-soft`, `--ui-radius-panel`, `--ui-radius-control`, `--ui-space-*`.
- Produces: classes `.app-shell`, `.screen-head`, `.ui-panel`, `.metric-strip`, `.ui-segment`, `.status-pill`, `.ui-empty`, `.ui-actions`.
- Consumes: current DOM ids and current class names retained in `styles/legacy.css` for untouched screens.

- [ ] **Step 1: Write the failing static UI contract**

  Add assertions that all six stylesheets exist and are linked in order, required tokens/classes exist, `sw.js` caches them, and production app source no longer contains `id="shellcss"`, `id="polishcss"`, `id="tidycss"`, `data-glass`, `backdrop-filter`, or the glass settings label.

- [ ] **Step 2: Run the test and verify RED**

  Run: `node --test tests/ui-system.test.cjs`

  Expected: FAIL because external files and contracts are missing.

- [ ] **Step 3: Extract existing CSS mechanically before redesign**

  Move reusable font/reset rules to `tokens.css`/`base.css`, sidebar and responsive frame rules to `shell.css`, reusable controls/panels/states to `components.css`, named-screen rules to `screens.css`, and untouched feature rules to `legacy.css`. Keep inline print strings and generated document styles in JavaScript.

- [ ] **Step 4: Replace shell/glass/polish override layers**

  Link the new files from `index.html`, remove the three override style blocks and glass runtime/settings, and update `sw.js` cache entries. Use opaque surfaces and the token values from the spec.

- [ ] **Step 5: Run static checks and verify GREEN**

  Run: `node --test tests/ui-system.test.cjs && npm run check`

  Expected: PASS with no syntax errors.

### Task 3: Unified login and grading entry

**Files:**
- Modify: `index.html` (`enterView`, teacher settings/auth entry, login helpers)
- Modify: `styles/screens.css`
- Create: `tests/ui-login-regression.cjs`
- Modify: `tests/run.cjs`

**Interfaces:**
- Produces: `entryShellHtml(activeRole)` returning the two-column entry shell.
- Produces: `entryRoleSet(role)` supporting `teacher`, `student`, and `parent` while preserving existing auth functions.
- Consumes: current `auth`, `stLogin`, `sgOpen`, passkey and `openByNumber` functions.

- [ ] **Step 1: Write failing Playwright tests**

  Test one `h1`, teacher/student/parent role switching, number-grading shortcut, preserved input labels, visible primary action, keyboard focus after role changes, 390px no horizontal overflow, and no update toast overlapping the form.

- [ ] **Step 2: Run the test and verify RED**

  Run with the existing local server harness: `BASE=http://127.0.0.1:8765 node tests/ui-login-regression.cjs`

  Expected: FAIL on missing unified role controls and layout contract.

- [ ] **Step 3: Implement the unified entry markup**

  Recompose `enterView` and teacher-auth opening into the shared shell without changing authentication calls, stored sessions or hashes. Add role-specific title/help copy and preserve passkey support.

- [ ] **Step 4: Implement desktop/mobile entry styles**

  Use two columns from 900px upward and one column below; keep one filled primary per active role and place number grading as a secondary action.

- [ ] **Step 5: Run regression and static tests**

  Run: `BASE=http://127.0.0.1:8765 node tests/ui-login-regression.cjs && npm run check`

  Expected: PASS.

### Task 4: Worksheet builder and weak-type workspace

**Files:**
- Modify: `index.html` (`startView`, `weakView`, selection summary helpers)
- Modify: `styles/screens.css`
- Create: `tests/ui-learning-workflows.cjs`
- Modify: `tests/run.cjs`

**Interfaces:**
- Produces: `scopeQuestion(kind)` returning student or aggregate screen question text.
- Produces: `weakFindingHtml(rows, scope)` using current calculated weak data.
- Consumes: current `SCOPE`, `CUR_S`, `scopeStu`, `typeRows`, `W`, `makeNow`, `quickPractice` and selection handlers.

- [ ] **Step 1: Write failing workflow tests**

  Stub realistic teacher/student/history data and assert: builder shows two recommended starts; aggregate scope keeps weak-type recommendation enabled; weak screen title changes by scope; finding names a real weakest type and evidence; filters occupy one row; selected summary is a desktop side panel and mobile bottom bar; existing click handlers remain callable.

- [ ] **Step 2: Run the test and verify RED**

  Run: `BASE=http://127.0.0.1:8765 node tests/ui-learning-workflows.cjs`

  Expected: FAIL on missing new regions and scope-aware findings.

- [ ] **Step 3: Recompose `startView`**

  Add `screen-head`, two recommendation blocks, grouped secondary methods and one filled action while preserving the existing builder mode/state assignments.

- [ ] **Step 4: Recompose `weakView`**

  Add scope-aware question/finding, one-row controls, dominant map/list region and selected summary using existing data and selection logic. Replace emoji status marks with text/SVG/shape classes.

- [ ] **Step 5: Add responsive styles and verify GREEN**

  Run: `BASE=http://127.0.0.1:8765 node tests/ui-learning-workflows.cjs && npm run check`

  Expected: PASS with no page-level overflow at 390px.

### Task 5: Student operations list and detail panel

**Files:**
- Modify: `index.html` (`stuView`, registration helpers, student actions)
- Modify: `styles/screens.css`
- Create: `tests/ui-students-regression.cjs`
- Modify: `tests/run.cjs`

**Interfaces:**
- Produces: `studentRowHtml(student, metrics)` with one `상세 보기` action and overflow menu.
- Produces: `studentDetailOpen(id)` and `studentDetailHtml(student)` using existing account/report/attendance/fee/edit/delete functions.
- Consumes: `STU`, `hist`, `stuAdd`, account issue, report, attendance, fee, edit and delete handlers.

- [ ] **Step 1: Write failing student-list tests**

  Assert a divided metric strip, search/scope controls, no permanently visible registration column, one visible main action per row, details containing all former operations, Escape/focus return behavior, destructive action separation, and phone list rows with no horizontal page overflow.

- [ ] **Step 2: Run the test and verify RED**

  Run: `BASE=http://127.0.0.1:8765 node tests/ui-students-regression.cjs`

  Expected: FAIL on the current two-column form/list and many row actions.

- [ ] **Step 3: Implement list, registration dialog and detail panel**

  Reuse current handlers, move forms/actions into accessible floating surfaces, keep selection/bulk operations available, and preserve CSV export.

- [ ] **Step 4: Add desktop/tablet/phone compositions**

  Desktop uses list plus pushed detail; phone shows one region at a time and returns to the saved list position.

- [ ] **Step 5: Run regression and static tests**

  Run: `BASE=http://127.0.0.1:8765 node tests/ui-students-regression.cjs && npm run check`

  Expected: PASS.

### Task 6: Global chrome cleanup and final verification

**Files:**
- Modify: `index.html`
- Modify: `styles/*.css`
- Modify: `tests/ui-system.test.cjs`
- Modify: `tests/run.cjs`
- Create: `.taste-skill/ui-rebuild/critique.md`

**Interfaces:**
- Produces: a source allowlist for semantic exceptions: progress/data gradients, print highlights, literal educational symbols and floating overlay shadows.

- [ ] **Step 1: Extend the failing static contract**

  Assert visible workflow strings contain no decorative emoji, non-print app CSS has no banned ground/button/card gradient, resting panel shadows are absent, and all remaining exceptions carry `taste-skill-ignore` with a reason.

- [ ] **Step 2: Run the contract and verify RED**

  Run: `node --test tests/ui-system.test.cjs`

  Expected: FAIL with the remaining unclassified patterns.

- [ ] **Step 3: Replace global decorative effects**

  Convert workflow emoji to SVG/text, flatten hero/card/button gradients, remove resting shadows, retain only documented semantic exceptions, and ensure overlays remain visually distinct.

- [ ] **Step 4: Run the complete automated suite**

  Run: `npm test && npm run check`

  Expected: all configured tests pass; report any unrelated database/environment failures by name.

- [ ] **Step 5: Run Taste Skill gates**

  Run app lint on `index.html`, then app inspector against login and authenticated fixture URLs at 1440, 768 and 390px. Fix every `FAIL`; defend or fix every `WARN`.

- [ ] **Step 6: Inspect final screenshots and write critique**

  Open every final screenshot, record each named screen's question, visible hierarchy, colour use, alignment, state behavior and phone composition in `.taste-skill/ui-rebuild/critique.md`. Fix the three most visible problems, re-inspect once, and keep the final report.

- [ ] **Step 7: Verify backup recoverability and final diff**

  Run: `node --test tests/ui-backup.test.cjs && git diff --check && git status --short`

  Expected: backup test passes, diff check is clean, and only planned source/test/spec files plus ignored inspection artifacts are present.

