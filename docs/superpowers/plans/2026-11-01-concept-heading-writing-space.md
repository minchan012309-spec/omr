# 개념 교재 단원명과 필기 공간 재조판 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 단원명은 전체 폭으로 보이고 그 아래부터 40mm 필기 공간과 140mm 개념 본문이 시작되는 개념 쪽을 만든다.

**Architecture:** `bkPack`의 전체 폭 `top/topH` 영역에 단원명 단위를 배치하고, 개념 쪽 객체가 그 높이를 렌더러에 전달한다. 개념 본문 단위는 140mm·11px로 측정하며 `bkPageHtml0`이 홀짝에 맞춘 40mm 직사각형 필기 면을 함께 그린다.

**Tech Stack:** 정적 JavaScript, HTML/CSS A4 렌더러, Playwright/Chrome, Node.js 회귀 테스트

**Spec:** `docs/superpowers/specs/2026-11-01-concept-heading-writing-space-design.md`

## Global Constraints

- 개념 정리 쪽에만 적용한다.
- 단원명 186mm, 본문 140mm, 간격 6mm, 필기 면 40mm, 좌우 안전 여백 12mm를 사용한다.
- 필기 면은 `var(--pl)` 단색이며 선·테두리·라운딩이 없다.
- 개념 본문은 11px로 측정·렌더링한다.
- `books.js` 변경 후 `index.html`의 버전과 `sw.js`의 `VER`을 올린다.

## Review Focus

- 단원명 높이가 과목마다 달라도 본문·필기 면은 카드 아래에서 시작해야 한다 — 실제 DOM 위치 검사.
- 단원명이 없는 이어지는 개념 쪽은 상단 공간을 불필요하게 비우지 않아야 한다 — 두 개념 쪽 비교 검사.
- 좁아진 본문에서 표·그림·문장이 잘리지 않아야 한다 — 높이 재측정과 PDF 생성.
- 홀짝 방향이 실제 쪽 번호를 따라야 한다 — `p.n`과 `data-side` 비교.
- `kind:'p'` 국어 지문에는 필기 면이 생기지 않아야 한다 — 별도 HTML 계약 검사.

---

### Task 1: 단원명·본문·필기 면 조판

**Files:**
- Modify: `books.js`
- Modify: `tests/book-pdf.cjs`

**Interfaces:**
- Consumes: `bkPack()`, `p.top`, `p.topH`, `bkPageHtml0()`.
- Produces: `.cntop`, `.cnbody`, `.cnnote[data-side]`, `BK_CONCEPTW=140`, `BK_CONCEPT_NOTE=40`.

- [x] **Step 1: 실제 개념서의 실패하는 레이아웃 테스트 작성**
  - 단원명 186mm, 본문 140mm, 필기 면 40mm, 간격 6mm, 본문 11px를 검사한다.
  - 단원명 카드가 있는 쪽의 본문·필기 면 상단이 카드 아래인지 검사한다.
  - 이어지는 쪽과 국어 지문 쪽의 기존 배치를 함께 검사한다.
- [x] **Step 2: `BASE=http://127.0.0.1:8766 node tests/book-pdf.cjs`가 새 계약에서 실패하는지 확인**
- [x] **Step 3: 단원명을 `bkPack`의 전체 폭 상단 단위로 만들고 개념 쪽에 `top/topH`를 전달**
- [x] **Step 4: 140mm·11px 본문과 홀짝 40mm 직사각형 필기 면을 렌더링**
- [x] **Step 5: 집중 테스트를 통과시키고 실제 PNG를 직접 확인**

### Task 2: 높이·배포 캐시·전체 회귀

**Files:**
- Modify: `books/heights.json`
- Modify: `index.html`
- Modify: `sw.js`
- Modify: `WORKLOG.md`

**Interfaces:**
- Consumes: Task 1의 개념 쪽 HTML/CSS 계약.
- Produces: 재측정 높이표와 새 배포 캐시 버전.

- [x] **Step 1: 전 과목 높이를 다시 측정**
- [x] **Step 2: `books.js` 및 서비스 워커 캐시 버전을 한 단계 올림**
- [x] **Step 3: 인쇄 회귀·정적 검사 실행 (`npm test` 전체는 사용자 요청으로 생략)**
- [x] **Step 4: WORKLOG 기록 후 관련 파일만 커밋·푸시하고 새 PR 생성**
