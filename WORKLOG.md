# WORKLOG — 최근 작업 기록 (새 기록을 맨 위에)

다른 AI가 이어서 일할 수 있게, 작업이 끝날 때마다 맨 위에 추가합니다. 형식은 `AGENTS.md` 6절.

## 2026-10-30 · Claude Code · claude/intro-mockups-system-audit · PR #101 (https://github.com/minchan012309-spec/omr/pull/101)
- 시작: `origin/main` b72f028(PR #100 병합)과 같은 위치. 열린 PR 없음.
- 요청: 인트로에서 깨진 장면(책 목업 · 노트북 키보드가 화면보다 크게 · 학원 운영 장면 기기 겹침 · 대시보드 위 문구 겹침) 고치기, 2장면(「복잡했던 학원 운영이…」 디스플레이 확대 + 강조 상자) 폐지 후 새로 만들기, 앱 전반 디자인 점검 후 고치기.
- 인트로 깨짐의 실제 원인
  - GSAP `scale` 은 가로 · 세로만 줄이고 깊이(z)는 그대로다. 줄인 노트북의 바닥판(깊이 0.69W) · 디스플레이 두께 · 책 두께가 원래 크기로 남아 노트북 키보드가 화면보다 크게, 책 표지가 어긋나 보였다. → `build()` 에서 각 `.obj` 안을 `.zs` 껍질로 감싸고 `zsync()` 가 타임라인마다 `scaleZ(scaleX)` 를 건다.
  - 원근 1700px 이 짧아 화면 아래쪽 기기가 크게 일그러짐 → `perspective:3400px`. 기기를 z 로 앞뒤에 둘 때는 `Z()` 로 원근을 되돌려 화면 위치 · 크기를 맞춤.
  - 장면마다 vw 비율로 박아 둔 위치 때문에 넓은 화면 · 낮은 화면에서 문구와 기기가 겹치고 잘림 → `area(장면)` 이 그 장면 문구의 실제 크기를 재서 「문구 오른쪽(왼쪽 문구 장면) / 문구 아래(가운데 · 휴대폰)」 자리를 주고, 기기 크기를 그 자리에 맞춘다.
- 장면별
  - 2장면 새로 만듦: 확대 · 강조 상자 · 캡션 · 어둡게 깔기 제거. 디스플레이가 히어로에서 오른쪽으로 비켜서며 살짝 돌아서고, 왼쪽에 새 문구(「아침에 볼 것은, 한 화면에.」). 화면은 대시보드 → 반 시간표 → 학습지 만들기 순.
  - 5장면(기기): 문구를 가운데 → 왼쪽으로. 책 → 태블릿 → 뒤에서 열리는 노트북을 문구 오른쪽에서.
  - 8장면(학원 운영): 노트북 빼고 디스플레이(뒤) · 학부모 화면 휴대폰(앞 왼쪽, `phone-parent` 추가) · 출결 단말(앞 오른쪽). 연결선 · 이름표 삭제(겹치고 어수선).
  - 9장면(생태계): 가운데 문구가 올라오는 동안 기기가 비켜 내려갔다가 문구 아래 한 줄로 선다. 흔들림 ±6° → ±3°.
  - 3 · 4 · 7장면: 문제 카드 · 학습지 · 펼친 책 · 책 줄 · 분석 카드 · 노트북을 문구 오른쪽 자리에 맞는 크기로. 책장 그림자 0.28 → 0.22(표지 0.1).
  - 지운 무대 요소의 CSS(`.hl` · `.hl-cap` · `.scrim` · `.links` · `.tags` · `.floor`)도 정리.
- 앱 디자인 점검(교사 17화면 · 학생 미리보기 6화면 × 1440 · 820 · 390 · 다크 캡처) 후 고친 것
  - 학생 홈 파란 머리의 「오늘의 문제 · 내 과제 보기」가 남색 바탕 + 파란 글자로 거의 안 보임(`components.css` 의 `#main button.p` !important) → 흰 버튼.
  - 휴대폰에서 취약 유형 · 고정 막대(`.stick`)가 없어진 아래 탭 바 자리(62px) 위에 떠서 아래로 내용이 비침 → legacy 의 `.stick{bottom:62px}` 삭제(이미 있는 `--navh` 규칙 사용).
  - 학습 현황(교사 · 학생 미선택)이 없는 「오른쪽 위」 선택기를 가리킴 → 학생 선택이 들어 있는 `needStu()`.
  - 학원 운영 대시보드 숫자 칸 8개가 7+1로 하나만 다음 줄 → 4×2(수납 권한 없으면 3×2), 휴대폰 2열, 「580,000 원」이 꺾이지 않게.
  - 오답노트 머리 버튼이 휴대폰에서 두 줄로 찌그러짐 → 줄바꿈되는 버튼 줄(`.wnact`).
  - 학습지 만들기 머리의 「내 학습지」 보조 버튼이 바탕과 같은 색이라 글자만 떠 보임 → 화면 머리 보조 버튼에 테두리 · 면.
  - 고정 막대가 있는 화면에서 토스트가 막대를 가리지 않게 위로.
- 캐시 · 버전: CSS 6개 `?v=3`(index.html · sw.js · tests/app-ui.cjs), lazy `?v=4`(sw.js SHELL 도 같은 URL), `intro.*?v=9`, `sw.js` VER `solvi-v160`.
- 바뀐 파일: `intro.js`, `intro.css`, `intro.html`, `index.html`, `lazy/admin.js`, `styles/legacy.css`, `styles/screens.css`, `sw.js`, `tests/intro-regression.cjs`, `tests/app-ui.cjs`, `WORKLOG.md`.
- 테스트: `tests/intro-regression.cjs` 의 「카메라가 디스플레이 안으로」 → 「디스플레이가 문구 오른쪽으로」, 새 검사 — 1440×900 · 1280×720 · 1990×1150에서 2 · 3 · 4 · 5 · 7 · 8 · 9장면이 자리 잡은 순간 기기 · 카드가 그 장면 문구와 겹치지 않고 화면 밖으로 잘리지 않음(무대가 비어 있으면 실패).
- 확인: 인트로를 1990×1150(라이트 · 다크) · 1440×900 · 1280×720 · 820×1180 · 390×844에서 장면마다 캡처해 직접 봄. `node scripts/verify-static.cjs` 통과, `intro-regression` · `intro-scroll` 통과, `npm test` 전체 통과(exit 0, 「PASS all isolated verification commands」).
- 주의: Playwright `fullPage` 캡처는 고정 사이드바 때문에 앱 화면 왼쪽이 잘린 것처럼 찍힌다(앱 문제 아님, 화면 크기 캡처로 확인).
- 남은 일: 실제 Mac 트랙패드 · iPad · iPhone에서 인트로를 만져 보지 못함. 휴대폰 폭 인트로는 문구가 위, 기기가 아래라 다음 장면 문구가 올라올 때 잠깐 기기 위를 지나감(구조상). 업데이트 알림 토스트가 휴대폰에서 아래쪽 카드를 잠깐 가림(한 번만 뜸).

## 2026-10-30 · Claude Code · claude/intro-scroll-ui-fixes · PR #100 (https://github.com/minchan012309-spec/omr/pull/100)
- 시작: `origin/main` 3836e04(PR #99 병합) 위에서 새 브랜치. 직전 작업은 PR #99(인트로 라이트/다크 · 스크롤 거리 1.5배), PR #98(시네마틱 인트로), PR #97(UI 재구축, Codex). 열린 PR 없음. 직전 세션은 사용자가 「아직도 스크롤이 너무 빨라」라고 한 뒤 한도로 끊겨 손대지 못한 상태였음.
- 목적: 인트로에서 휠 · 트랙패드를 조금만 움직여도 장면이 통째로 넘어가는 문제 해결, 그리고 남은 앱 문제(CSS 순서, 테스트 진입점, 로그인 탭 접근성, entry-mode, 학생 목록 모바일, 장식, YetHangul, 서비스 워커 캐시).
- 인트로 스크롤 원인: wheel · touch 핸들러나 scroll-snap은 원래 없었다(측정: 휠 80px → scrollY 80px 그대로). 원인은 구조였다. `#film`(100vh, overflow:hidden)을 GSAP ScrollTrigger `pin`으로 약 35화면 동안 고정하고 `scrub:1.2`로 타임라인 하나에 10장면을 묶어서, ① 글이 스크롤을 따라 움직이지 않고 ② 문구가 18~24단위(≈250~320px) 안에 통째로 페이드 교체되며 ③ 손을 뗀 뒤에도 1.2초 동안 장면이 계속 진행됐다. 그래서 짧은 트랙패드 관성 한 번이 「한 장」 전환으로 보였다.
- 바꾼 스크롤 구조(`intro.js` · `intro.css` · `intro.html`)
  - 제거: ScrollTrigger(`pin` · `scrub:1.2` · `anticipatePin` · `ignoreMobileResize`, 스크립트 태그와 `sw.js` 캐시 항목), 문구 페이드 교체(`copyIn`) · 히어로 문구 페이드, 목차 `data-go` 클릭을 가로채 `scrollTo({behavior:'smooth'})`로 보내던 처리, `100vh` 고정 필름과 `--tb` 보정.
  - 새 구조: 장면 섹션 10개가 보통 문서 흐름(섹션 높이 = 장면 길이 × 화면 높이 1.7%/단위, 휴대폰 1.4%, 문구보다 짧지 않게). 문구는 섹션 안 `position:sticky`라 들어오고 나갈 때 스크롤과 1:1로 움직인다. 3D 무대 · 배경만 `position:sticky; height:100svh`. 타임라인 시간은 스크롤 위치에서 지연 없이 계산(`timeAt` · 섹션 경계 사이 직선 보간). 스크롤 위치를 바꾸는 코드는 크기 변경 · 테마 전환으로 다시 짤 때 같은 장면에 되돌려 놓는 한 곳뿐.
  - 목차는 보통 앵커(`#bank` 등) + IntersectionObserver로 `aria-current`. wheel · touch · key 리스너 없음, snap 없음, `scroll-behavior` 강제 없음. 동작 줄이기 · 저사양 · 스크립트 없음은 원래대로 정적 장면.
  - 같이 고침: 무대의 3D 책과 장면 섹션이 둘 다 `id="book"`이던 중복 id → 무대 쪽 `bookO`. 다음 장면 문구가 밝은 대시보드 위로 올라올 때 읽히도록 아래쪽 어둡게 깔기(scrim)를 일찍 켜고 늦게 끔. 장식 그라디언트(디스플레이 글로우 · 바닥)와 휴대폰 폭의 디스플레이 윗 · 아랫면(가는 줄로 보임) 숨김, 받침대 휴대폰 폭 단색. 무대 속 가짜 UI 조각(문항 타일 · 오답 분석 · 이름표 · 캡션)에 `data-ui`.
- CSS 순서: `index.html` 링크를 `tokens → legacy → base → shell → components → screens`로 바꾸고 모두 `?v=2`(같은 값을 `sw.js` SHELL에). 순서 변경 전후 계산 스타일을 1440 · 390 · 다크에서 비교: 의도 밖 변화는 `shell.css`의 `main{max-width:1180px}`이 모든 legacy 화면 폭을 1320→1180으로 줄이는 것 하나라 그 규칙을 지움. 나머지 차이는 글꼴(Pretendard), 본문 색(`--ui-text`), 새 화면(취약 유형 · 학생 목록 · 패널)의 screens/components 규칙이 실제로 적용되는 것.
- YetHangul 범위: `legacy.css`의 `body` 글꼴에서 YetHangul · SolviSymbols를 빼서 앱 UI는 Pretendard. 문항 · 교재 · 인쇄 · PDF는 그림자 DOM(`mount`)과 인쇄 창 템플릿이 자기 글꼴(YetHangul 포함)을 그대로 씀(바꾸지 않음).
- 테스트 실행 구조: `npm test`(`tests/run.cjs`)에 `ui-system` · `ui-rebuild-contract`(node --test), 새 `tests/intro-scroll.cjs`, 새 `tests/app-ui.cjs`를 넣음. git 제외 `backups/`를 요구해 깨끗한 clone에서 실패하던 `tests/ui-backup.test.cjs`는 `scripts/verify-local-ui-backup.cjs`로 옮김(백업 파일은 그대로). 로컬 백업 확인: `npm run verify:local-backup` → pass 2.
- 로그인(`index.html`): 역할 탭에 roving tabindex · ←/→/Home/End · `aria-controls` · 탭 패널(`#stbody` `role=tabpanel` `aria-labelledby`). 선생님 탭은 새로고침(`location.reload`) 대신 같은 패널에 이메일 · 비밀번호 폼(`entryTLogin` → 기존 `auth('in')` → `load()`). 역할을 바꿔도 적어 둔 아이디 · 이메일은 이 화면에 있는 동안 기억(저장소에 쓰지 않음). 모든 입력에 `<label>`, 아이디 칸에서도 Enter로 제출. 소개의 `#login`은 이 선생님 탭으로 열림(로그인 안 하는 환경은 예전처럼 설정 창). 로그인 아닌 화면에 중복으로 그리던 역할 탭 제거.
- entry-mode: 화면 함수마다 붙이고 떼던 것을 `entrySync()` 하나로(`#main`에 `.entry-shell`이 있을 때만) 모으고 `#main` MutationObserver로 어떤 경로든 맞춤. 토스트는 숨기지 않음(앱이 `alert`를 토스트로 바꿔 둬서, 로그인 화면의 「번호로 바로 채점」 → 「먼저 로그인하세요」 안내가 보이지 않던 문제). 대신 로그인 전에는 업데이트 알림 토스트를 띄우지 않음(폼을 가리던 것).
- 학생 목록(≤900px): 이름 · 반 · 정답률 · 최근 풀이 · 주의 유형 · 푼 문항 · 약한 유형(데이터 없음 포함)을 줄을 나눠 모두 남김(예전엔 약한 유형이 사라지고 숫자 칸이 25px로 눌림). 계정 상태만 「⋯」 메뉴로. 「⋯」 메뉴: 열면 첫 항목 포커스, ↑/↓/Home/End, Escape로 닫고 버튼으로 복귀, 바깥 클릭 닫힘(원래), 메뉴 폭을 화면 안으로. 삭제는 원래대로 빨간 글씨 · 구분선.
- 장식 정리(앱 화면만): 문항 신고 버튼 · 신고 창의 🚩, 취약 유형의 ▦ · ☰ · ⚡ 제거, 신고 창 인라인 style → 클래스. 학습지 만들기 시작 화면의 중복 제목 막대(← 학습지 만들기 · 과목 알약)를 화면 머리 하나로. 앱에 backdrop-filter는 원래 없었음(테스트로 확인). 인쇄 · PDF · 교재 템플릿은 건드리지 않음.
- 취약 유형: 보는 범위(학생 · 반 · 전체)에 맞춘 질문과, 실제 기록에서 정답률이 가장 낮은 유형 · 정답률 · 채점 문항 수 한 줄 추가.
- 서비스 워커: `VER` `solvi-v159`, CSS 6개를 `?v=2`로 캐시(HTML 링크와 같은 URL), ScrollTrigger 제거, `intro.*?v=8`. 네트워크 우선 CSS 정책은 그대로.
- 바뀐 파일: `intro.js`, `intro.css`, `intro.html`, `index.html`, `styles/legacy.css`, `styles/shell.css`, `styles/screens.css`, `sw.js`, `package.json`, `tests/run.cjs`, `tests/ui-system.test.cjs`, `tests/intro-regression.cjs`, `tests/intro-scroll.cjs`(새), `tests/app-ui.cjs`(새), `scripts/verify-local-ui-backup.cjs`(이동), `AGENTS.md`.
- `AGENTS.md`를 고친 이유: 저장소 장기 규칙이 실제로 바뀜 — CSS 로드 순서 줄(legacy 위치 · `?v=N`), 인트로 구조 설명(pin · scrub 금지), 필수 명령(`npm test` 범위, 로컬 백업 검증 명령).
- 새 · 수정 테스트
  - `tests/intro-scroll.cjs`: 1440 · 768 · 390에서 휠 80(≈80px, 화면 1/4 미만, 히어로 문구가 1:1로 이동, 타임라인 12단위 미만), 장면 경계 40px 앞에서 휠 80(시작점으로 끌려가지 않음, 들어오는 문구가 1:1), 휠 80×5(모두 반영 · ≈400px), 휠 900(≈900px)과 900×6(섹션 여러 개 통과), 역방향 −80 두 번, `scrollTo(본문 45%)` 뒤 1.2초 위치 그대로, PageDown/PageUp/Space/Shift+Space(한 화면 안쪽)/ArrowDown/ArrowUp(200px 미만)/End/Home, 섹션 중간 정지 · 문구가 화면 안, 가로 넘침 없음. 휴대폰 터치(CDP `Input.dispatchTouchEvent` 터치 시작 · 이동 · 끝) 위 · 아래 스와이프가 스와이프 거리만큼 움직임. 처음엔 `synthesizeScrollGesture`를 썼으나 리눅스 CI 헤드리스에서 0px이 나와 바꿈, 동작 줄이기, file://. 수정 전 코드(origin/main)에서 돌리면 「hero copy travels with the scroll 1:1」에서 실패함을 확인.
  - `tests/app-ui.cjs`(가짜 Supabase 응답 · 예시 학생 「가학생」 「나학생」): 로그인 1440 · 390(탭 키보드 · 포커스 · 값 유지 · 새로고침 없음 · Enter 제출(학생 · 학부모 RPC) · 번호 채점 안내 · 가로 넘침 · 폼 가림 · 선생님 로그인 뒤 entry-mode 해제 · 뒤로/앞으로 · 로그아웃), 세션 자동 복구, `#login` · `#student` 해시, 학습지 만들기(시작점 · 제목 하나 · bGo로 빌더 창 · 취약 유형 추천 · 선택 요약 · 하단 버튼 · bdGo), 취약 유형(전체 · 반 · 학생 질문, 최약 유형 · 정답률 · 표본, 선택 · 해제, 바로 풀기(quickPractice) · 학습지 만들기, 휴대폰 하단 요약), 학생 목록(행 · 검색 · 반 필터 · 상세 · 390 핵심 정보 · 메뉴 키보드 · Escape · 바깥 클릭 · 기존 핸들러 · 빈 상태), 공통(Pretendard · YetHangul 없음 · backdrop-filter 없음 · 장식 이모지 없음, 다크, 동작 줄이기, 서비스 워커가 새 순서의 CSS를 캐시하고 오프라인에서 열림).
  - `tests/intro-regression.cjs`: pin 검사 → ScrollTrigger 없음 · 무대 sticky, 장면 이동은 `__intro.yAt`, 목차는 앵커 + `aria-current`. `tests/ui-system.test.cjs`: 새 CSS 순서와 `sw.js`의 같은 `?v=` 확인.
- 확인(실제 실행)
  - `npm run check` 통과, `git diff --check` 통과.
  - `npm test`: 통과(모든 변경 반영 뒤 마지막 실행 exit 0, 「PASS all isolated verification commands」 · intro scroll · app UI 포함).
  - `node --test tests/ui-system.test.cjs tests/ui-rebuild-contract.test.cjs` 5/5, `npm run verify:local-backup` 2/2(로컬 전용).
  - 1440 · 768 · 390 캡처를 직접 봄: 인트로 10장면(문구 위치 · 겹침 · 가로 넘침 0), 앱 로그인 · 선생님 탭 · 학생 목록 · 메뉴 · 다크 · 취약 유형 · 학습지 만들기.
  - file://: `intro-scroll.cjs`가 file://로 열어 휠 80 확인(BASE 없이 돌리면 전부 file://).
  - Taste Skill inspector(`intro.html`): 수정 전 5 FAIL → 지금 1 FAIL · 6 WARN. 남은 FAIL은 `empty-screens`(데스크톱 12장 중 8장이 빈 바탕 20% 미만, 수정 전 9장)로 시네마틱 장면 구성 자체의 밀도 문제라 이번 범위에서 고치지 않음.
- 남은 위험 · 후속
  - 실제 Mac 트랙패드 · iOS Safari · Android Chrome에서 직접 만져 보지 못함(Playwright 휠 · CDP 터치 이벤트로만 확인).
  - 인트로 페이지가 데스크톱 약 43화면 길이. 스크롤바를 끌면 장면이 빨리 지나감(위치 보정은 없음). 길이 비율은 `intro.js`의 `layout()`(1.7 / 1.4).
  - 다음 장면 문구가 들어올 때 이전 장면 기기 위를 잠깐 지나감(inspector WARN `pinned-over-picture` · `long-pin`).
  - 900~1180px 폭에서는 학생 행의 약한 유형 · 계정 칸이 여전히 숨음(390 · 768은 보임).
  - 로그인 화면 「번호로 바로 채점」은 여전히 브라우저 `prompt` 창을 쓰고, 로그인 전에는 채점할 수 없다는 안내로 끝남(기존 동작).
- 커밋: 45d1b88(구현 · 테스트), 이 기록 줄은 뒤이은 docs 커밋

## 2026-10-30 · Claude Code · claude/print-students-ebook-intro · PR #99
- 한 일
  - 인쇄: 개념학습 인쇄(개념 학습지 · 요약 노트 · 취약 유형 개념)를 A4 쪽(`.cpg`)으로 나눠 미리보기와 인쇄가 같게. 태블릿 · 휴대폰은 인쇄 창 「인쇄」가 쪽마다 A4 PDF 저장(`popPdf`). 개념 데이터 로드 실패를 저장하지 않아 O/X만 인쇄되는 화면에 갇히지 않게. 취약 유형 개념 인쇄에 본교재 개념 포함.
  - 메뉴: 「검색 · 이동」 → 홈 바로 아래 「통합검색」.
  - 학생 탭(`stuView`) 새로 만듦: 요약 숫자, 탭(목록 · 등록 · 반 일괄 등록 · 시험 일정), 표 한 줄에 한 학생 + 「⋯」 메뉴, 일괄 작업 막대, 모바일 카드형.
  - 로그인 화면: 솔비 로고 + 이 기기에 저장된 학원 로고(없으면 솔비 로고만).
  - eBook(`bkEbook`) 화면 전면 개편: 밝은 종이 바탕 · 과목 색, 위 막대 하나, 필기 도구는 필기 켤 때만, WebGL은 넘김 효과 켤 때만, 썸네일 공유 스타일시트.
  - `AGENTS.md` · `CLAUDE.md` · `WORKLOG.md` 추가, 오래된 `HANDOFF_PROMPT.md`(PR #87 지시서) 삭제.
  - 무료 체험 신청 `trial.html` · 자체 문의 `contact.html`(+`lead.js` · `lead.css`) → 서버 표 `site_leads` → 개발자 탭 「체험 신청 · 문의」(`dev.js?v=8`). **Supabase에서 `supabase/sql_26_site_leads.sql`을 실행해야 저장된다.**
  - 인트로: 라이트(물질과 에너지 파랑) · 다크 테마와 전환 버튼, 스크롤 거리 1.5배 · 스크럽 부드럽게, 맨 아래 S 심볼, 요금제 아래 「무료 체험하기」, 문의는 메일 대신 자체 문의, 넓은 화면에서 기기 배치가 퍼지지 않게(LW), QR 스캔을 카메라 화면처럼, 장면별 세부 기능 줄, 휴대폰 목업 다듬기. `sw.js` VER `solvi-v158`, `intro.*?v=7`.
  - 목업: 사용자가 Apple 공식 목업을 원했으나 Apple Design Resources 라이선스가 「Apple OS 전용 소프트웨어의 목업」으로 한정하고 웹사이트 콘텐츠 사용을 금지해서 쓰지 않음(받은 파일 삭제). 공개 저장소 목업은 옛 기종 · CC BY-SA라 부적합 → 자체 CSS 3D 기기를 다듬음.
- 바뀐 파일: `index.html`, `books.js`(`?v=66`), `dev.js`, `styles/screens.css`, `styles/legacy.css`, `intro.*`, `trial.html`, `contact.html`, `lead.*`, `policy.html`, `sw.js`, `supabase/sql_26_site_leads.sql`, `tests/intro-regression.cjs`
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
