# 로그인·로딩·인트로 정제 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 로그인·로딩의 상태 전달을 명확히 하고, 기존 인트로를 Apple 레퍼런스의 전시형 고급 톤으로 정제한다.

**Architecture:** `index.html`의 전역 busy 상태는 진행률 기반 텍스트를 추가하고 로그인 렌더에서 보조 행동을 제거한다. 기존 CSS 계층에서 로그인은 `screens.css`, 인트로는 `intro.css`로 독립적으로 다듬고, 브라우저 회귀는 기존 계약에 새 사용자 가시 상태를 더한다.

**Tech Stack:** 정적 HTML, vanilla JavaScript, CSS, Playwright regression tests.

**Spec:** `docs/superpowers/specs/2026-11-03-login-loading-apple-intro-design.md`

## Global Constraints

- Pretendard·기존 기능·실제 캡처를 유지하고 새 의존성을 추가하지 않는다.
- 로딩 남은 시간은 추정값으로 보이며, 진행률은 0–100의 정수다.
- 전환은 300ms 이하의 transform/opacity만 사용하고 hover 미디어 규칙을 지킨다.
- 변경된 정적 자산의 캐시 버전을 올린다.

## Review Focus

- 실제 진행률 콜백이 오면 자동 진행률보다 낮아지지 않고, 100%에서 남은 시간이 사라지는지 확인한다.
- 로그인 역할 전환 뒤에도 제거한 번호 채점 버튼이 다시 렌더되지 않는지 확인한다.
- 1440·820·390 폭에서 인트로 표면이 가로 넘침이나 캡처·카피 겹침을 만들지 않는지 확인한다.
- 밝은/어두운 구간에서 헤더 대비와 링크 포커스가 유지되는지 확인한다.
- 서비스 워커가 변경된 intro CSS/JS와 앱 스타일을 같은 버전으로 가져오는지 확인한다.

### Task 1: 로딩과 로그인 상태

**Files:**
- Modify: `index.html:1183-1185,2755-2766`
- Modify: `styles/legacy.css`, `styles/screens.css`
- Test: `tests/app-ui.cjs`

- [ ] **Step 1: Write failing browser assertions** for `.busy` percent/remaining text and the absent login number-grading control.
- [ ] **Step 2: Run `BASE=http://127.0.0.1:8765 node tests/app-ui.cjs`** and confirm the new assertions fail.
- [ ] **Step 3: Implement progress text updates** in `busyPaint()` and remove the login-only button while making form spacing tokenized and balanced.
- [ ] **Step 4: Re-run `BASE=http://127.0.0.1:8765 node tests/app-ui.cjs`** and confirm pass.

### Task 2: 인트로 전시형 표면

**Files:**
- Modify: `intro.css`
- Modify: `intro.html`, `sw.js`
- Test: `tests/intro-regression.cjs`

- [ ] **Step 1: Write failing intro assertions** for the refined hero/tile surface classes and compact responsive spacing.
- [ ] **Step 2: Run `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`** and confirm fail.
- [ ] **Step 3: Implement the chosen bright gallery palette, navy emphasis tiles, hierarchy, and responsive rhythm** without changing the font or section semantics.
- [ ] **Step 4: Increment intro cache query versions and `sw.js` `VER`, then re-run the intro regression** and confirm pass.

### Task 3: 전체 검증과 기록

**Files:**
- Modify: `WORKLOG.md`

- [ ] **Step 1: Run `node scripts/verify-static.cjs` and `npm test`.**
- [ ] **Step 2: Inspect desktop 1440, tablet 820, and phone 390 captures** for the login and intro views.
- [ ] **Step 3: Record actual verification and remaining device limitations at the top of `WORKLOG.md`.**
