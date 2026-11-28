# 신규 자료 브라우저 LaTeX 출력 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 HTML 자료를 보존하면서 새 자료를 각 생성자의 브라우저에서 LaTeX PDF로 생성한다.

**Architecture:** 명시적 엔진 버전으로 자료를 구분한다. WebAssembly XeTeX·xdvipdfmx는 Worker에서 실행하고 최종 쪽 명세만 기존 Supabase에 저장한다. 별도 조판 서버는 사용하지 않는다.

**Tech Stack:** 정적 JavaScript, Web Worker, WebAssembly, IndexedDB, Supabase SQL RPC.

**Spec:** `docs/superpowers/specs/2026-11-19-latex-print-engine-design.md`

## 제약

원본 폰트를 공개 커밋하지 않는다. 기존 미커밋 파일을 보존한다. 기존 HTML 높이표와 자료 ID를 변경하지 않는다. 사용자가 구현·PR 등록을 요청했으므로 현재 세션에서 직접 구현하고 검토한다.

## 작업

- [x] 1. 버전 없는 자료의 HTML 기본값과 새/복제 자료의 명시적 버전, 고유 교재 ID, 회차 구분을 검증·구현한다.
- [x] 2. 보기·선지·표·병합 셀·MathML·CSS 분수·그림·긴 지문을 제한된 문서 모델에서 LaTeX로 변환한다.
- [x] 3. 지정 폰트와 원본 7쪽을 브라우저에서 재현한다. HWP 내부 서식과 용지를 읽어 A4 표지에 적용한다.
- [x] 4. 정적 엔진·고정 패키지·폰트 등록, Worker 취소·제한 시간, 최종 shipout 명세와 안정된 쪽 안내를 구현한다.
- [x] 5. 새 자료 생성·설정·PDF·재출력·QR 채점·제출 잠금·여러 쪽 선택·로그인 복귀를 연결한다. 기존 HTML 설정은 유지한다.
- [x] 6. 기존 Supabase의 불변 명세 저장·개별 조회 SQL, RLS, 배포 준비 문서·라이선스·캐시 갱신을 작성한다.
- [x] 7. 최종 전체 회귀·PDF QR 해독·화면 검증·리뷰와 WORKLOG 정리를 완료했다. 커밋·푸시 후 한국어 PR을 등록하며 병합하지 않는다.

## 중점 검토

기존 자료 재분류, 새 교재/회차 덮어쓰기, 최종 PDF 쪽수와 문항 번호, 재출력 시 제출 잠금, 분수·국어 지문 누락, 표지/빠른 정답/노트/뒤표지에 따른 쪽 이동, 기존 QR 스캐너 전역 변수 충돌을 확인한다. 검증 결과와 운영 미적용 항목은 `docs/verification/2026-11-19-latex-print.md`에 기록한다.
