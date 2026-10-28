# 학원 통합 운영 개선 Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans; implement and verify each task before reporting completion.

**Goal:** 기존 Solvi 데이터와 정적 배포를 보존하며 국어 출력, 다크모드, 행정 업무와 인트로를 개선한다.
**Architecture:** 기존 index.html 전역 인터페이스와 lazy/admin.js, lazy/acad.js를 확장한다. DB 변경은 추가 마이그레이션으로 제공하며 기존 설치는 점진적으로 호환한다.
**Tech Stack:** 정적 HTML/CSS/JavaScript, Supabase PostgreSQL/RLS, Python/Node 검증, Playwright.
**Spec:** 이번 사용자 요청 및 2026-10-29 확인: 기존 구조 유지, 설계 검토 생략하고 바로 구현.

## Global Constraints
- Solvi·Pretendard와 기존 과목색 유지. 기존 데이터 삭제·초기화 금지.
- 운영 DB에 임의로 연결하거나 실제 개인정보·수납 데이터를 변경하지 않는다.
- 권한은 DB에서 강제하며 UI 숨김만으로 보호했다고 주장하지 않는다.
- 모바일 및 reduced-motion에서 모든 핵심 콘텐츠 제공. 스크롤 강제 이동 금지.
- 검증하지 못한 실제 DB·실물 인쇄·알림 발송은 완료로 표시하지 않는다.
- 원격 기본 브랜치 대상 한국어 PR, 병합 금지.

## Review Focus
- 다크모드 출력면 색상 및 일반 체크박스와 스위치 충돌.
- 국어 개념 HTML 최상위 텍스트 유실, 표/옛한글/한 페이지보다 긴 단위.
- 학원 간 외래키 참조와 행정 직원/강사의 수납·개인정보 접근.
- 월말 날짜·중복 청구·시간표 충돌 및 입력 오류.
- JavaScript 실패·모바일·reduced-motion에서 인트로 콘텐츠 접근.

### Task 1: 출력·다크모드 안정화
**Files:** index.html, books.js, tests/print-regression.cjs, tools/check_books.js
**Interfaces:** mount(el,html,css), bkCbUnits(sec,w), bkDocHtml(plan,all), 기존 QR/쪽 계획 유지.
- [x] 브라우저로 첨부 문제를 재현하고 실패 검증을 기록한다.
- [x] 출력 전용 light 색상 격리, 테마 카드 대비, 스위치 충돌을 수정한다.
- [x] 국어 개념 텍스트/표/폰트 유실 원인을 수정하고 다른 과목을 검사한다.
- [x] PDF 생성과 페이지 넘침·색상·문항 코드를 검증한다.

### Task 2: 스크롤 기반 인트로
**Files:** intro.html, intro.css, intro.js, tests/intro-regression.cjs
**Interfaces:** 실제 앱 링크와 기존 가격 RPC를 보존한다. intro 전용 파일만 변경.
- [x] 실제 기존 자산을 분석하고 연속 스크롤 구성을 구현한다.
- [x] 디바이스 변형·책 펼침·문제 선택→OMR→분석을 스크롤 위치와 연결한다.
- [x] 모바일·키보드·reduced-motion·no-JS 동작과 실제 브라우저 화면을 검증한다.

### Task 3: 기존 행정 기능 확장
**Files:** lazy/admin.js, lazy/acad.js, lib/academy-core.js, supabase/sql_24_operations.sql, tests/academy-core.test.cjs
**Interfaces:** AD/AC 기존 상태와 CRUD 유지. 날짜·충돌·CSV·금액 등 순수 계산은 AcademyCore로 노출.
- [x] 통합 학생 상세(출결·반·상담·수납·학습), 업무·상담 예약·휴강/대체수업을 기존 운영에 통합한다.
- [x] 시간표 충돌, 월말 조회, 반복 청구 멱등성, 검색/정렬/CSV 안전성을 구현한다.
- [x] 추가 DB 표·역할별 RLS·학원간 참조 방지를 구현한다.
- [x] 실제 DB가 없는 환경에서는 API 계약과 격리된 테스트를 실행하고 한계를 명시한다.

### Task 4: 통합 검증·리뷰·커밋·PR
**Files:** docs/verification/2026-10-29-platform.md, README.md
- [x] 경쟁 서비스 공식 자료와 구현 대비를 기록한다.
- [x] JS 구문, 국어 전체 검수, CSS 기존 실패 기준, 브라우저·PDF·순수 로직 테스트를 실행한다.
- [x] 독립 리뷰의 중요한 결함을 수정한다.
- [x] 기능별 한국어 커밋 후 push와 PR 생성을 시도하고 결과를 정확히 보고한다.


## 실행 기록 및 판정

사용자가 설계 검토 생략과 즉시 구현을 선택했다. 현재 checkout이 깨끗해 별도 작업 브랜치를 만들고 기존 경로에서 작업했다(앱 worktree attachment 조회 자체는 내부 DB 오류로 실패). 인트로와 행정 UI는 서로 다른 파일을 맡은 구현자가 순차 수행했고, 출력/국어 편집/SQL/통합 검증은 주 작업자가 수행했다. 보안 리뷰와 전체 리뷰에서 지적된 자격정보 우회·수납 설정 우회·청구 키·수업 예외·닫기 오류를 수정하고 재검증했다.

Ruling: 라이브 운영 DB는 변경하지 않는다. 새 SQL은 실제 메모리 PostgreSQL 전체 스키마 및 기존 함수와 함께 검증하고, 운영 적용/물리 프린터/실기기/외부 발송은 미검증으로 표시한다.
Ruling: 기존 쪽 QR 호환성과 교재 계획 보존을 위해 기존 해설 여백 경고 2곳은 자동 압축으로 쪽 번호를 바꾸지 않는다. 이번 출력 안정화의 남은 한계로 보고한다.
Ruling: 새 국어 원고는 독립적인 기기 저장·JSON 백업·인쇄 경로로 추가한다. 기존 문제은행 교재의 QR/배포 정의를 바꾸지 않으며, 새 원고의 클라우드 공동 편집/QR은 미구현으로 보고한다.
Ruling: 기본 CSS 중복 검사에서 작업 전부터 있던 동일 16건은 기준선을 올려 숨기지 않고 결과를 보고한다.
