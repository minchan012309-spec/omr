# WORKLOG — 최근 작업 기록 (새 기록을 맨 위에)

다른 AI가 이어서 일할 수 있게, 작업이 끝날 때마다 맨 위에 추가합니다. 형식은 `AGENTS.md` 6절.

## 2026-10-30 · Claude Code · claude/cinematic-intro (PR #98 병합 뒤 후속 PR)
- 한 일
  - 인쇄: 개념학습 인쇄(개념 학습지 · 요약 노트 · 취약 유형 개념)를 A4 쪽(`.cpg`)으로 나눠 미리보기와 인쇄가 같게. 태블릿 · 휴대폰은 인쇄 창 「인쇄」가 쪽마다 A4 PDF 저장(`popPdf`). 개념 데이터 로드 실패를 저장하지 않아 O/X만 인쇄되는 화면에 갇히지 않게. 취약 유형 개념 인쇄에 본교재 개념 포함.
  - 메뉴: 「검색 · 이동」 → 홈 바로 아래 「통합검색」.
  - 학생 탭(`stuView`) 새로 만듦: 요약 숫자, 탭(목록 · 등록 · 반 일괄 등록 · 시험 일정), 표 한 줄에 한 학생 + 「⋯」 메뉴, 일괄 작업 막대, 모바일 카드형.
  - 로그인 화면: 솔비 로고 + 이 기기에 저장된 학원 로고(없으면 솔비 로고만).
  - eBook(`bkEbook`) 화면 전면 개편: 밝은 종이 바탕 · 과목 색, 위 막대 하나, 필기 도구는 필기 켤 때만, WebGL은 넘김 효과 켤 때만, 썸네일 공유 스타일시트.
  - `AGENTS.md` · `CLAUDE.md` · `WORKLOG.md` 추가, 오래된 `HANDOFF_PROMPT.md`(PR #87 지시서) 삭제.
- 바뀐 파일: `index.html`, `books.js`(`?v=66`), `styles/screens.css`, `styles/legacy.css`, 인트로 관련 파일(같은 PR의 인트로 작업 참고)
- 확인: Playwright로 데스크톱 · iPad 흉내(UA · 터치)에서 개념 · 학습지 PDF, 학생 탭 1440/390, eBook 1440/390, 로그인 화면 로고 유무
- 남은 일 · 주의: 실제 iPad Safari · Android에서 인쇄(PDF) 확인 못 함. 과목 문항이 안 보인다는 제보는 사용자가 경로를 잘못 본 것이었음(코드 문제 아님).

## 2026-10-30 · Claude Code · PR #98 (병합됨)
- 한 일: 인트로를 Pro Display XDR 중심 시네마틱 스크롤(GSAP ScrollTrigger pin + scrub 10장면)로 재제작, `policy.html` 초안, `tools/capture_cine.js` 추가, 쓰지 않는 인트로 이미지 삭제, 인트로 회귀 테스트 교체.
- 주의: `sw.js` VER `solvi-v157`. 기기 목업은 CSS 3D 자체 제작이었고, 사용자가 이후 실제 목업 이미지 사용 · 라이트/다크 분리 · 스크롤 속도 조절 · 무료 체험 신청 · 자체 문의 폼을 요청함.

## 2026-10-29 · Codex · PR #97 (병합됨)
- 한 일: 프런트엔드 UI 시스템 재구축(`styles/tokens.css` · `base` · `shell` · `components` · `screens`, 입장 화면 `entry-shell`, 화면 머리 `screen-head`). 백업 `backups/ui-rebuild-2026-10-29`(git 제외).

## 2026-10-29 · Codex · PR #96 (병합됨)
- 한 일: 교재 · 학습지 휴지통, QR · 모바일 채점 오류 수정.

## 2026-10-29 · Codex · PR #95 (병합됨)
- 한 일: 국어 교재 출력, 학원 운영(원생 · 반 · 시간표 · 상담 · 보강 · 운영 업무) · 권한 체계(원장 · 강사 · 행정) 고도화. 검증 `docs/verification/2026-10-29-platform.md`, `admin.md`.
