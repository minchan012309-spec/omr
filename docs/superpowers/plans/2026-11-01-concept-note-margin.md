# 개념 정리 바깥쪽 필기 여백 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 개념 정리 쪽을 148mm 본문으로 다시 조판하고 홀수 오른쪽·짝수 왼쪽에 선 없는 32mm 과목색 필기 면을 만든다.

**Architecture:** 개념 단위 측정 폭과 실제 렌더 폭을 같은 `BK_CONCEPTW=148` 상수로 묶는다. `bkPageHtml0(plan, i)`는 `p.k === 'cn' && p.kind === 'c'`인 쪽에만 쪽 번호에 따른 바깥쪽 필기 면을 추가하므로 미리보기·eBook·인쇄·PDF가 한 구현을 공유한다.

**Tech Stack:** 정적 JavaScript, HTML/CSS A4 렌더러, Playwright/Chrome, Node.js 회귀 테스트

**Spec:** `docs/superpowers/specs/2026-11-01-concept-note-margin-design.md`

## Global Constraints

- 개념 정리 쪽에만 적용하고 문제·지문·해설·표지·차례·노트 쪽은 바꾸지 않는다.
- 본문 148mm, 간격 6mm, 필기 면 32mm, 기존 바깥 안전 여백 12mm를 사용한다.
- 홀수는 오른쪽, 짝수는 왼쪽에 필기 면을 둔다.
- 선·점·라벨·테두리는 금지하고 `--pl` 과목색 면만 사용한다.
- 머리글·바닥글은 기존 전체 폭을 유지한다.
- `books.js` 변경 뒤 `index.html` 버전과 `sw.js`의 `VER`을 올린다.

## Review Focus

- 표지·차례 뒤 실제 쪽 번호를 기준으로 홀짝이 결정되어야 한다 — Task 1 브라우저 위치 검사로 고정한다.
- `k:'cn', kind:'p'`인 국어 지문 쪽에는 필기 면이 생기면 안 된다 — Task 1 음성/언어 주교재 HTML 계약 검사로 고정한다.
- 7mm 제본 여백과 함께 써도 필기 면·본문이 A4 밖으로 잘리면 안 된다 — Task 1 bounding-box 검사로 고정한다.
- 148mm에서 표·그림의 줄바꿈이 늘어도 본문 높이 넘침이 없어야 한다 — Task 2 높이 재측정과 경고 검사로 고정한다.
- 과목색 면이 인쇄/PDF에서 사라지거나 선·테두리가 생기면 안 된다 — Task 1 computed style 및 실제 PDF 생성으로 고정한다.

---

### Task 1: 개념 본문 재조판과 바깥쪽 필기 면

**Files:**
- Modify: `books.js:4, 25-170, 480-490, 630-645, 805-820, 1015-1030, 1146-1165`
- Modify: `tests/book-pdf.cjs`

**Interfaces:**
- Consumes: `bkCbUnits(sec, width)`, `bkPack(units, columns, height)`, `p.n`, `p.k`, `p.kind`, `bkVars()`의 `--pl`.
- Produces: `BK_CONCEPTW = 148`, 개념 쪽의 `.cnp`, `.cnbody`, `.cnnote[data-side]` HTML/CSS 계약.

- [x] **Step 1: 실패하는 실제 교재 테스트 작성**
  - `tests/book-pdf.cjs`에서 실제 `hl-c` 개념 쪽 두 장의 HTML을 연다.
  - `.cnp` 두 장과 각 `.cnnote` 하나를 요구한다.
  - 홀수 쪽 `data-side="right"`, 짝수 쪽 `data-side="left"`를 실제 `p.n`과 비교한다.
  - `.cnbody` 너비 148mm, `.cnnote` 너비 32mm, 둘 사이 6mm, 각 요소가 A4 안쪽인지 bounding box로 검사한다.
  - `.cnnote`의 배경이 투명이 아니고 border/background-image가 없는지 검사한다.
  - 같은 테스트에서 `hl-hs`의 `kind:'p'` 지문 쪽에는 `.cnnote`가 없음을 검사한다.

- [x] **Step 2: 테스트가 현재 구현에서 실패하는지 확인**
  - Run: `node tests/book-pdf.cjs`
  - Expected: `.cnp` 또는 `.cnnote`가 없어 FAIL.

- [x] **Step 3: 개념 전용 측정 폭 추가**
  - `books.js`에 `BK_CONCEPTW=148`을 추가한다.
  - 기본 개념서, 주교재 개념, 맞춤 교재 개념, 자유 구성 교재 개념의 `bkU`/`bkCbUnits` 폭을 `BK_FULLW`에서 `BK_CONCEPTW`로 바꾼다.
  - 문제·지문에서 쓰는 `BK_FULLW`는 유지한다.

- [x] **Step 4: 개념 쪽 HTML/CSS 구현**
  - `bkPageHtml0(plan, i)`에서 `p.k==='cn' && p.kind==='c'`일 때만 `.bp.bk.cnp`를 만든다.
  - `p.n % 2`로 `data-side`를 정하고 본문 `.bd.one.cnbody`와 빈 `.cnnote`를 배치한다.
  - CSS는 홀수 본문 왼쪽/필기 면 오른쪽, 짝수는 반대로 배치한다. 필기 면은 `background:var(--pl)`만 사용한다.

- [x] **Step 5: 실제 교재 테스트 통과 확인**
  - Run: `node tests/book-pdf.cjs`
  - Expected: 네이티브 PDF와 앱 PDF가 생성되고 개념 여백 계약 PASS.

### Task 2: 높이·캐시·전체 회귀

**Files:**
- Modify: `index.html:1054`
- Modify: `sw.js:2`
- Modify: `WORKLOG.md`
- Test: `tools/measure_books.js`, `tests/print-regression.cjs`, 전체 테스트

**Interfaces:**
- Consumes: Task 1의 `BK_CONCEPTW`, `.cnp/.cnbody/.cnnote` 계약.
- Produces: 배포 캐시 `books.js?v=69`, `solvi-v170`, 검증 기록.

- [x] **Step 1: 교재 높이 재측정**
  - Run: `node tools/measure_books.js`
  - Expected: 모든 과목 측정 완료, 처리되지 않은 넘침 오류 없음.

- [x] **Step 2: 인쇄 회귀 실행**
  - Run: `node tests/print-regression.cjs && node tests/book-pdf.cjs`
  - Expected: 두 명령 모두 exit 0.

- [x] **Step 3: 캐시 버전 갱신**
  - `index.html`의 `books.js?v=68`을 `v=69`로 올린다.
  - `sw.js`의 `solvi-v169`를 `solvi-v170`으로 올린다.

- [x] **Step 4: 정적·전체 회귀 실행**
  - Run: `node scripts/verify-static.cjs && npm test`
  - Expected: `PASS 16 executable scripts parsed`, `PASS all isolated verification commands`.

- [x] **Step 5: 출력물 직접 확인**
  - `/tmp/solvi-concept-print.png`와 생성 PDF 첫 두 개념 쪽을 확인한다.
  - 홀수 오른쪽·짝수 왼쪽, 32mm 과목색 면, 선 없음, 본문 잘림 없음이 보여야 한다.

- [x] **Step 6: 기록·커밋·PR**
  - `WORKLOG.md` 맨 위에 변경·검증·미확인 기기를 기록한다.
  - 사용자 설치 스킬과 `skills-lock.json`은 제외하고 관련 파일만 커밋·푸시한다.
  - 한국어 제목과 설명으로 새 PR을 만들고 병합하지 않는다.
