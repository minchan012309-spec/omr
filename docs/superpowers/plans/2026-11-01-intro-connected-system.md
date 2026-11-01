# Intro Connected System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 인트로를 학습 흐름과 학원 운영이 한 학생 기록으로 연결되는 올인원 시스템으로 재설계한다.

**Architecture:** 기존 정적 `intro.html`/`intro.css`/`intro.js` 구조와 스크롤 진행도 엔진을 유지한다. 히어로와 연결 장면은 동일한 연결 언어를 공유하고, 기능과 과목 영역은 HTML에 모든 정보를 남긴 채 CSS/JS로 탐색성을 높인다.

**Tech Stack:** 정적 HTML, vanilla CSS, vanilla JavaScript, Playwright 기반 Node 회귀 테스트

**Spec:** `docs/superpowers/specs/2026-11-01-intro-connected-system-design.md`

## Global Constraints

- UI 문구와 상태명은 한국어로 쓴다.
- 새 외부 라이브러리, 무거운 blur, `backdrop-filter`, 큰 그림자를 추가하지 않는다.
- 모션은 transform/opacity만 사용하고 300ms 이하, `cubic-bezier(.23,1,.32,1)`를 사용한다.
- 탭·범위·키보드 동작은 이동 애니메이션 없이 즉시 반응한다.
- 모든 hover는 `@media(hover:hover) and (pointer:fine)` 안에 둔다.
- 브라우저 기본 스크롤을 유지하고 휴대폰에서 가로 방향 화면 밖 진입을 사용하지 않는다.
- 실제 제품에 없는 기능·수치·후기를 만들지 않는다.
- 사용자 요청이 없으므로 커밋·푸시·PR은 하지 않는다.

## Review Focus

- 390px 모바일에서 연결 장면과 과목 목록이 가로 폭을 늘리지 않아야 한다 — Task 2·4 회귀 테스트.
- `prefers-reduced-motion`과 JavaScript 비활성 상태에서 핵심 흐름과 전체 과목이 보여야 한다 — Task 2·4 회귀 테스트.
- 고정 헤더가 앵커 대상 제목을 가리지 않아야 한다 — Task 1 앵커 테스트.
- sticky 학원의 하루에서 시간 버튼을 누르면 정확한 단계가 활성화되어야 한다 — Task 1 단계 이동 테스트.
- 기능 분야 변경 시 숨김 카드가 키보드 탐색과 개수 계산에 남지 않아야 한다 — Task 3 분야 테스트.

---

### Task 1: 내비게이션과 직접 이동

**Files:**
- Modify: `intro.html:17-20,176-216`
- Modify: `intro.css` 내 `.nav`, `.day-steps`, 섹션 앵커 규칙
- Modify: `intro.js:10-23,69-72,208-231`
- Test: `tests/intro-regression.cjs`

**Interfaces:**
- Consumes: 기존 섹션 ID와 `DAY.update(p)`
- Produces: `goSection(id)`, `DAY.go(index)`, 모든 `.day-steps a[data-i]`

- [ ] **Step 1: 실패하는 앵커·시간 단계 테스트 작성**
  - 상단 목차의 내부 링크가 모두 존재하는 섹션을 가리키는지 검사한다.
  - 각 내부 링크 클릭 후 대상의 top이 헤더 하단과 2px 이내인지 검사한다.
  - 0·4·8번째 시간 항목을 클릭했을 때 `.day-steps li.on[data-i]`와 `.dd.on`이 해당 단계인지 검사한다.

- [ ] **Step 2: 회귀 테스트를 실행해 시간 단계 직접 이동이 실패하는지 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: `DAY.go` 또는 단계 이동 assertion FAIL.

- [ ] **Step 3: `goSection(id)`와 `DAY.go(index)` 구현**
  - 헤더 높이와 sticky run의 이동 가능 거리를 사용한다.
  - 일반 앵커는 브라우저 기본 해시와 `scroll-margin-top`을 유지한다.
  - 동작 줄이기에서는 smooth behavior를 사용하지 않는다.

- [ ] **Step 4: 회귀 테스트 통과 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: PASS.

### Task 2: 히어로 연결형 운영체제

**Files:**
- Modify: `intro.html:24-61,138-165`
- Modify: `intro.css` 내 히어로·연결 장면 규칙
- Modify: `intro.js` 내 히어로 상호작용·`LINK` 진행도
- Test: `tests/intro-regression.cjs`

**Interfaces:**
- Consumes: 기존 `LINK.update(p)`, `data-fx`, 스크롤 rAF
- Produces: `#systemMap`, `.sys-node[data-step]`, `.sys-path[data-step]`, `LINK.update(p)`의 단계별 활성 상태

- [ ] **Step 1: 실패하는 히어로 계약 테스트 작성**
  - 삭제 문구 `Solvi(솔비)는`와 `#tmap`이 0개인지 검사한다.
  - 히어로 로고가 단일 `.hero-logo` 컨테이너이며 두 SVG의 시각적 중앙 차이가 2px 이내인지 검사한다.
  - 시스템 노드가 `QR 채점`, `취약 개념`, `다음 학습지`, `수업 배정`, `상담 기록`, `학부모 알림` 순서로 존재하는지 검사한다.
  - 연결 장면 끝에서 모든 노드와 경로가 활성화되는지 검사한다.

- [ ] **Step 2: 회귀 테스트 실패 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: `#tmap` 제거 및 시스템 노드 assertion FAIL.

- [ ] **Step 3: 히어로 마크업과 카피 교체**
  - 제목은 `채점이 끝나면, 다음 수업이 시작됩니다.`로 한다.
  - 학생 기록 중앙 노드와 6개 실제 기능 노드를 사용하고 예시 데이터 표시를 둔다.

- [ ] **Step 4: 연결 진행도 모션 구현**
  - 스크롤 위치로 node/path의 opacity와 transform을 직접 계산한다.
  - 모바일은 세로 구조, 동작 줄이기는 완성 상태를 기본으로 한다.

- [ ] **Step 5: 폭·동작 줄이기·정적 문서 테스트 통과 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: PASS, 390px `scrollWidth === innerWidth`.

### Task 3: 기능 전체를 분야별 디렉터리로 재배치

**Files:**
- Modify: `intro.html:217-263`
- Modify: `intro.css` 내 `.spec`, `.cats`, `.spec-g`, `.sp`
- Modify: `intro.js:234-245`
- Test: `tests/intro-regression.cjs`

**Interfaces:**
- Consumes: 기존 `.sp[data-cat]` 33개와 `.cats button[data-cat]`
- Produces: `.spec-nav`, `.spec-panel`, `setSpecCategory(category)`

- [ ] **Step 1: 실패하는 디렉터리 레이아웃 테스트 작성**
  - 데스크톱에서 분야 목록과 콘텐츠 영역이 4:8에 가까운 두 열인지 검사한다.
  - 분야 선택 후 해당 카드만 visible이고 다른 카드의 `hidden`이 true인지 검사한다.
  - 선택 버튼의 `aria-pressed`, 결과 개수, 첫 결과 제목 포커스 이동이 일치하는지 검사한다.
  - 모바일에서 단일 열이고 가로 넘침이 없는지 검사한다.

- [ ] **Step 2: 회귀 테스트 실패 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: `.spec-nav` 또는 레이아웃 assertion FAIL.

- [ ] **Step 3: 마크업과 CSS를 비대칭 디렉터리 구조로 변경**
  - 기존 33개 기능 텍스트는 유지한다.
  - `전체`에서는 대표 요약과 모든 기능을 읽을 수 있게 하고, 개별 분야에서는 해당 분야만 보여 준다.

- [ ] **Step 4: `setSpecCategory(category)` 구현**
  - 이동 모션 없이 hidden/aria 상태와 개수를 동기화한다.
  - 사용자 클릭일 때만 결과 제목에 프로그램적 포커스를 준다.

- [ ] **Step 5: 회귀 테스트 통과 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: PASS.

### Task 4: 전체 지원·준비 과목 로드맵

**Files:**
- Modify: `intro.html:265-270`
- Modify: `intro.css` 내 `.subj`와 과목 로드맵 규칙
- Test: `tests/intro-regression.cjs`

**Interfaces:**
- Consumes: `index.html`의 `SUBJECTS` 27개 이름·그룹·학년·상태
- Produces: `.subject-roadmap`, `.subject-group[data-group]`, `.subject-item[data-status]`

- [ ] **Step 1: 실패하는 과목 동기화 테스트 작성**
  - 현재 지원 4개, 전체 27개, 준비 중 23개를 검사한다.
  - 과학·국어·사회·수능 맞춤형 그룹이 모두 존재하는지 검사한다.
  - `index.html`의 `SUBJECTS` 이름과 인트로의 과목 이름 집합이 같은지 정적 파싱으로 검사한다.
  - 동작 줄이기와 JavaScript 비활성 상태에서도 27개가 모두 보이는지 검사한다.

- [ ] **Step 2: 회귀 테스트 실패 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: 전체 과목 수 assertion FAIL.

- [ ] **Step 3: 과목 로드맵 마크업과 반응형 레이아웃 구현**
  - 지원 중과 준비 중을 텍스트·색·상태 표식으로 구분한다.
  - 표지 이미지는 지원 중 과목의 대표 시각물로 유지한다.

- [ ] **Step 4: 과목·모바일·정적 문서 테스트 통과 확인**
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: PASS.

### Task 5: 버전·문서·전체 검증

**Files:**
- Modify: `intro.html` asset query versions
- Modify: `sw.js:2-3`
- Modify: `AGENTS.md`
- Modify: `WORKLOG.md`
- Test: `tests/intro-scroll.cjs`, `tests/intro-regression.cjs`, 전체 정적 검증

**Interfaces:**
- Consumes: Task 1-4의 완성된 HTML/CSS/JS
- Produces: 배포 캐시 버전 `intro.*?v=17`, `solvi-v168`, 작업 기록

- [ ] **Step 1: 버전과 서비스 워커 캐시 목록 갱신**
  - `intro.css?v=17`, `intro.js?v=17`, `VER = 'solvi-v168'`로 맞춘다.

- [ ] **Step 2: 문서와 WORKLOG 맨 위 기록 갱신**
  - 실제 변경 파일, 실행한 검증, 확인하지 못한 실제 기기를 사실대로 기록한다.

- [ ] **Step 3: 정적·인트로 검증 실행**
  - Run: `node scripts/verify-static.cjs`
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-scroll.cjs`
  - Run: `BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs`
  - Expected: 모두 exit 0.

- [ ] **Step 4: 전체 테스트 실행**
  - Run: `npm test`
  - Expected: exit 0, `PASS all isolated verification commands`.

- [ ] **Step 5: 1440·820·390 캡처 직접 확인**
  - 로고 기준선, 앵커 위치, 기능 가독성, 과목 상태, 가로 넘침을 확인한다.
  - 발견한 시각 문제를 수정한 뒤 관련 테스트를 다시 실행한다.
