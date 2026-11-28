# Domain, Login, and Intro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 새 운영 도메인과 패스키 안내를 일치시키고, 쌍둥이 문제 제작 흐름·로그인 화면·인트로 첫 화면을 복구한다.

**Architecture:** 앱의 하단 담기 막대는 쌍둥이 문제 추가의 다음 행동을 직접 제시한다. 공개 URL은 정적 사이트와 패스키 함수의 한 운영 주소로 통일하고, 소개 첫 화면은 남아 있는 유형 지도 컴포넌트를 재사용한다.

**Tech Stack:** 정적 HTML/CSS/JavaScript, Supabase Edge Function TypeScript, Playwright 회귀 테스트.

**Spec:** `docs/superpowers/specs/2026-11-02-domain-login-and-intro-design.md`

## Global Constraints

- UI 문구는 한국어·Pretendard를 사용하고, 애니메이션은 300ms 이하의 transform/opacity만 쓴다.
- 배포 파일 변경 후 `sw.js` 캐시 버전과 정적 참조 버전을 갱신한다.
- 기존 패스키는 새 RP ID로 이관하지 않는다는 WebAuthn 제약을 정확히 안내한다.

## Review Focus

- 담기 막대가 화면 하단의 다른 고정 UI와 겹치지 않는지 브라우저 회귀에서 확인한다.
- 로그인 폼이 데스크톱과 휴대폰에서 모든 입력·역할 탭을 표시하는지 확인한다.
- 새 도메인 주소가 QR·SEO·패스키 런타임과 배포 명령에 일관되게 쓰이는지 검사한다.
- 유형 지도에서 동작 줄이기 환경에도 선택 상태와 문구가 보이는지 확인한다.

### Task 1: 제작 흐름과 도메인 전환

**Files:** `index.html`, `supabase/functions/passkey/index.ts`, URL을 쓰는 공개 문서, 회귀 테스트

- [ ] 먼저 쌍둥이 문제 담기 안내·새 운영 주소·패스키 오류 안내를 요구하는 회귀 테스트를 추가하고 실패를 확인한다.
- [ ] `addTwins()`가 하단 담기 막대에 다음 행동 문구를 전달하게 하고, 공개 주소와 패스키 기본값을 `solvi.win`으로 정리한다.
- [ ] 패스키 서버 재배포 명령을 운영 문서에 기록하고 관련 테스트를 통과시킨다.

### Task 2: 로그인과 인트로 첫 화면

**Files:** `intro.html`, `intro.css`, `intro.js`, `styles/screens.css`, 인트로·로그인 브라우저 회귀 테스트

- [ ] 유형 지도와 감성 문구, 로그인 공간 규칙을 요구하는 회귀 테스트를 추가하고 실패를 확인한다.
- [ ] 기존 유형 지도 상호작용을 히어로로 되돌리고 `#why` 문장을 추가하며, 기존 연결형 운영체제 전용 JS를 안전하게 제거한다.
- [ ] 로그인 카드의 내부 리듬과 반응형 배치를 조정하고 데스크톱·휴대폰 렌더 및 전체 회귀를 확인한다.
