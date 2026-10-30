# AGENTS.md — 이 저장소에서 일하는 모든 AI가 작업 전에 반드시 읽을 것

사용자는 여러 AI(Claude Code, Codex 등)를 번갈아 씁니다. **다른 AI가 직전에 무엇을 고쳤는지 모르는 상태로 시작하지 마세요.** 아래 「작업 시작 전 확인」을 먼저 하고, 끝나면 「작업 끝난 뒤 기록」을 남기세요.

## 1. 작업 시작 전 확인 (필수)

1. **`WORKLOG.md`의 맨 위 기록 3~5개를 읽는다.** 직전 작업, 미완료 항목, 주의 사항이 있다.
2. `git fetch origin && git log --oneline -15 origin/main` 으로 최근 병합을 본다.
3. `gh pr list --state open` 으로 열려 있는 PR을 본다. 같은 파일을 고치는 PR이 있으면 그 브랜치 위에서 이어 가거나 사용자에게 묻는다.
4. 작업 브랜치는 **최신 `origin/main`에서 새로** 만든다(`git switch -c <도구>/<주제> origin/main`). 이미 병합된 브랜치에 커밋을 쌓지 않는다.
5. 제품 맥락은 `PRODUCT.md`, 기능 설명은 `README.md`, 검증 기록은 `docs/verification/`에 있다.

## 2. 프로젝트 한눈에

- **Solvi(솔비)**: 고등 과학 · 국어 문제은행으로 학습지 · 교재 · 모의고사를 만들고, QR · 번호로 채점하고, 취약 유형을 분석하고, 학원 운영(원생 · 반 · 출결 · 상담 · 보강 · 수납 · 알림장)까지 하는 웹앱.
- **빌드 없음.** 정적 파일을 GitHub Pages(`solvi.p-e.kr`)로 배포. 서버 데이터는 Supabase(`supabase/`, `setup.sql`).
- 주요 파일
  | 파일 | 내용 |
  |---|---|
  | `index.html` | 앱 본체(약 4,700줄, 화면 · 상태 · 채점 · 인쇄 창 · 개념학습). 탭마다 `xxxView()` 함수, `render()`가 분기 |
  | `books.js` | 교재 엔진(쪽 계획 `bkPlan`, 쪽 HTML `bkPageHtml`, 인쇄 · PDF, eBook `bkEbook`/`ebk*`). `index.html`의 `bkLoad()`가 `books.js?v=N`으로 늦게 불러온다 |
  | `lazy/*.js` | 늦게 불러오는 화면(`admin` 학원 운영, `acad` 출결 · 수납 · 알림장, `tset` 학원 설정, `omr-report`) |
  | `styles/*.css` | `tokens → legacy → base → shell → components → screens` 순(새 디자인 층이 legacy를 덮음). 링크와 `sw.js` SHELL에 같은 `?v=N`. 새 화면 스타일은 `screens.css`, `--ui-*` 토큰 사용 |
  | `bank/`, `cm/`, `ph/`, `hl/` | 과목 데이터(물질과 에너지 · 세포와 물질대사 · 역학과 에너지 · 화법과 언어). `index.json`(유형 목록), `data.json`/`data.js`(교재 문항), `<태그>.json`(문제은행) |
  | `intro.html` · `intro.css` · `intro.js` | 로그인 전 소개 페이지. 장면마다 문구 + 실제 앱 캡처(`intro/*.webp`)만 둔 보통 문서. 기기 목업 · 3D 무대 · GSAP · 스크롤 연출 없음(사용자 요청, 2026-10-30). 캡처는 `tools/capture_cine.js` · `tools/capture_intro.js` → `tools/intro_webp.py` |
  | `policy.html` | 이용약관 · 개인정보처리방침(초안, 법률 검토 전) |
  | `sw.js` | 서비스 워커. **배포되는 파일을 바꾸면 `VER`을 올린다** |
  | `tools/` | 캡처(`capture_intro.js`, `capture_cine.js`) · 교재 높이 측정(`measure_books.js`) · 화법과 언어 생성기(`tools/hl/`) |

## 3. 실행 · 검증 명령

```bash
python3 server.py                 # http://localhost:8765 (로컬 확인용)
npm test                          # 정적 파싱 + UI 계약 + DB + 인쇄 + 국어 + 행정 + 인트로(스크롤 포함) + 앱 행동 회귀 (Playwright, Chrome 필요)
npm run verify:local-backup       # 로컬 전용: git 제외 backups/ 백업 검증(CI · 깨끗한 clone에서는 돌리지 않음)
node scripts/verify-static.cjs    # 모든 인라인 스크립트 문법 확인(커밋 전 최소한 이것)
node tools/measure_books.js [hl]  # 교재 글꼴·여백·문항을 바꾸면 반드시 쪽 높이 재측정
python3 tools/hl/make_hl.py       # 화법과 언어 문항을 바꾸면 재생성 → python3 tools/hl/audit.py --all
```

- Playwright로 **인쇄 창(about:blank 팝업)을 시험할 때 `context.route()`를 걸면 팝업의 네트워크가 멈춘다.** 인쇄 창을 시험하는 스크립트에서는 route를 쓰지 말 것(앱 버그가 아님).
- 화면을 바꿨으면 데스크톱(1440) · 태블릿(820) · 휴대폰(390)에서 스크린샷으로 직접 확인한다.

## 4. 지켜야 할 규칙

- UI 문구는 한국어, 글꼴은 Pretendard. 화면은 "깔끔하고 직관적이게, AI 티 나지 않게". 기본 HTML 버튼 · 입력 모양이 그대로 보이면 안 된다.
- 무거운 효과(`backdrop-filter`, 큰 blur, 글래스) 금지 — 사용자가 렉 때문에 싫어함.
- 교재의 ①·㉠ 같은 원문자는 CSS로 그리지 말고 글꼴 특수문자. 교재 디자인에 **왼쪽 굵은 실선(`border-left` 액센트) 금지.**
- 과목색: 물질과 에너지 파랑(`#2f7fd0`), 세포와 물질대사 초록, 역학과 에너지 보라, 화법과 언어 주황. `body[data-subj]`의 `--b`로 쓴다.
- 인쇄는 A4. 인쇄 창은 새 창(`popOpen` → `popInject` → `popWire`). **태블릿 · 휴대폰(`isMob()`)은 브라우저 인쇄가 여백을 멋대로 넣어 쪽이 밀리므로 인쇄 버튼이 A4 PDF 저장(`popPdf`)으로 바뀐다.** 교재는 `bkPdf`.
- 개념 인쇄 문서는 `cpDoc()`으로 만들고 인쇄 창에서 `cpPaginate()`가 A4 쪽(`.cpg`)으로 나눈다.
- `books.js`를 바꾸면 `index.html`의 `books.js?v=N` 숫자도 올린다. 배포 파일을 바꾸면 `sw.js`의 `VER`도 올린다.
- 사용자 후기 · 성과 수치 · 고객 수는 만들어 내지 않는다. 화면 캡처의 학생 이름과 기록은 예시 데이터임을 밝힌다.
- 개인정보가 담긴 실제 학생 데이터를 캡처 · 커밋하지 않는다.

## 5. Git · PR 규칙

- 커밋 · 푸시 · PR은 사용자가 시킬 때. PR 제목과 설명은 한국어. **사용자가 시키지 않으면 병합하지 않는다.**
- 커밋 메시지 끝에는 쓰는 도구가 요구하는 attribution 줄을 붙인다.
- 보고할 때는 한 것 · 확인한 방법 · 못 한 것(확인 못 한 기기 포함)을 사실대로 적는다.

## 6. 작업 끝난 뒤 기록 (필수)

`WORKLOG.md` **맨 위에** 아래 형식으로 한 덩어리를 추가하고 같은 커밋에 넣는다.

```markdown
## YYYY-MM-DD · 도구 이름 · 브랜치 / PR 번호
- 한 일: …
- 바뀐 파일: …
- 확인: …
- 남은 일 · 주의: …
```
