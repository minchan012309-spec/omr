# Solvi Frontend System Rebuild Design

## Intent

Solvi의 기능과 정적 배포 구조를 유지하면서, 로그인과 교사용 핵심 작업 화면을 하나의 일관된 앱 디자인 시스템으로 전면 재구축한다. 사용자가 화면을 열었을 때 가장 중요한 질문과 다음 행동을 즉시 찾을 수 있어야 하며, 카드·칩·그라디언트·글래스·이모지가 기능의 중요도를 대신하지 않게 한다.

## Goals

- 색, 활자, 간격, 표면, 모서리, 상태를 공통 토큰으로 고정한다.
- 로그인 화면을 데스크톱과 모바일 각각에 맞는 명확한 진입 화면으로 재구성한다.
- 학습지 만들기, 취약 유형, 학생 목록 화면을 각 화면의 한 가지 핵심 질문 중심으로 다시 구성한다.
- 앱 UI의 장식성 이모지, 바탕/버튼 그라디언트, 정지 카드 그림자, 글래스를 제거한다.
- `index.html` 안의 스타일을 역할별 CSS 파일로 분리하고 정적 배포와 오프라인 캐시를 유지한다.
- 기존 저장, 로그인, 학생/학부모, 채점, 인쇄, 교재, 분석 동작을 보존한다.

## Non-goals

- 데이터 모델, Supabase RPC, 로컬 저장 키, 문제 은행, 인쇄 문서 디자인을 재작성하지 않는다.
- 프레임워크나 빌드 시스템을 도입하지 않는다.
- 소개 페이지의 정보 구조를 다시 설계하지 않는다. 앱과 공유해야 하는 브랜드 토큰만 맞춘다.
- 모든 화면의 마크업을 한 번에 다시 쓰지 않는다. 공통 셸과 지정된 네 화면을 먼저 재구축하고 나머지 화면은 새 시스템 위에서 기존 기능을 유지한다.

## Anti-goals

- 기능을 숨겨서 단순해 보이게 만들지 않는다.
- 모든 것을 동일한 카드나 동일한 버튼으로 표현하지 않는다.
- 모바일을 데스크톱의 축소판으로 만들지 않는다.
- 디자인 정리를 이유로 인쇄용 CSS와 데이터 시각화의 의미 있는 색을 제거하지 않는다.

## Constraints

- 빌드 없는 정적 HTML/CSS/JS 배포를 유지한다.
- 기존 전역 함수 이름과 인라인 이벤트 계약을 보존한다.
- Pretendard와 Solvi 브랜드의 남색·노랑을 유지하되, 앱에서는 남색을 데이터와 한 개의 주요 행동에만 사용한다.
- 터치 대상은 44px 이상, 본문은 14px 이상, 보조 텍스트는 12px 이상으로 한다.
- 앱 제목은 20–28px, 패널 제목은 16–18px로 제한한다.
- 정지 패널은 테두리 또는 명도 차이로 분리하고 그림자를 쓰지 않는다.
- 원본 백업과 복원 검증을 구현보다 먼저 완료한다.

## Approaches Considered

### Incremental system cleanup

기존 DOM을 최대한 유지하고 스타일만 점진적으로 교체한다. 회귀 위험은 낮지만 카드 중심 정보 구조가 남는다.

### Full UI rebuild — selected

공통 셸과 지정 화면의 마크업을 다시 구성하고, 스타일을 역할별 파일로 분리한다. 디자인 일관성과 정보 계층 개선 폭이 가장 크다. 전역 함수와 데이터 로직을 보존하고 브라우저 회귀 테스트로 위험을 통제한다.

### Styling-only cleanup

색과 그림자만 정리한다. 빠르지만 사용자의 핵심 작업이 묻히는 구조적 문제를 해결하지 못한다.

## Backup and Recovery

구현 전 `backups/ui-rebuild-2026-10-29/`를 만들고 다음을 보존한다.

- `index.html`, `intro.html`, `intro.css`, `intro.js`, `sw.js`
- 현재 UI 관련 테스트 파일
- `git rev-parse HEAD`, `git status --short`, 각 파일 SHA-256을 기록한 `MANIFEST.txt`

백업 폴더는 제품 배포 대상이 아니므로 `.gitignore`에 추가한다. 복구 검증은 백업 파일의 체크섬과 원본 체크섬이 같은지 확인하는 테스트로 한다.

## Design System

### Tokens

- Ground `#f4f6f8`, surface `#ffffff`, raised `#eef1f4`, border `#dde2e8`
- Text `#121820`, muted `#586474`, faint `#737e8c`
- Accent `#1769aa`, accent-soft `#e8f2fb`, brand yellow `#fdc62d`
- Positive `#147a52`, warning `#9b6500`, negative `#bf2f38`
- Card radius 8px, control radius 6px, pills only for compact status data
- Spacing on a 4px base; canvas gutter 24–40px desktop, 16px phone
- One font family, five visible sizes: 12, 14, 16, 24, 32px

### Surface rules

- Resting panels: flat surface with 1px border or one tone step, never both shadow and border.
- Floating surfaces: menu, dialog, tooltip and bottom sheet may use one restrained shadow.
- Primary action: one filled accent button per task region.
- Data and status may use semantic colour; navigation and generic chrome remain neutral.
- Gradients remain only where they encode progress or chart data. Print highlights are outside the app rule.

### Shared components

- `app-shell`: sidebar/top bar, canvas, scope switcher, mobile sheet.
- `screen-header`: noun title, one-line finding, primary action, optional quiet secondary actions.
- `panel`: bordered or tone-separated content region.
- `metric-strip`: one divided container instead of separate KPI cards.
- `segmented-control`, `status-pill`, `empty-state`, `action-menu`, `field-group`.

## Screen Designs

### Login

Desktop uses a two-column entry: left side states what Solvi does and offers number grading; right side contains one unified role switch for teacher, student and parent login. The current teacher authentication contract and student/parent credential contracts remain separate behind that shared entry UI. Mobile keeps a single-column form with the grading shortcut below the primary login action. The page has one `h1`, no decorative update toast overlapping the form, and no large unclosed void.

### Worksheet builder start

The screen question is “오늘 어떤 학습지를 만들 것인가?”. The first region contains two recommended starts: weak-type worksheet and manual type selection. Remaining methods are a compact secondary list grouped as question bank, purpose and exam. Scope and student selection stay visible above the title; only one creation action is filled. When no individual student is selected, weak-type recommendations use the currently selected class or all-student scope rather than blocking the flow.

### Weak-type map

For an individual, the screen question is “이 학생에게 지금 무엇을 보강할 것인가?”. For a class or all-student scope it becomes “이 범위에서 무엇을 먼저 보강할 것인가?”. A finding strip states the weakest type or shared weakness and evidence computed from the active scope. View/filter controls occupy one row. The map/list is the dominant region, and the selected-types summary becomes a sticky side panel on desktop and a bottom action bar on mobile. Status uses shape, labels and limited semantic colour instead of emoji.

### Student list

The screen question is “누가 지금 도움이 필요한가?”. Registration forms move into a secondary drawer/dialog rather than occupying the first column permanently. The first screen shows the divided summary strip, search/scope, and student rows. Each row exposes `상세 보기` as its single main action and an overflow menu; account issuance, reports, attendance, fees, weak types and destructive actions live in the detail panel/menu.

## CSS File Boundaries

- `styles/tokens.css`: fonts, colour, spacing, type, radius and motion tokens.
- `styles/base.css`: reset, document defaults, accessibility and generic form controls.
- `styles/shell.css`: desktop sidebar, top bar, canvas, mobile navigation and responsive shell.
- `styles/components.css`: buttons, panels, metrics, tabs, tables, forms, dialogs and states.
- `styles/screens.css`: login, worksheet builder, weak map and student list layouts.
- `styles/legacy.css`: extracted untouched rules required by screens outside this rebuild; reduced over time, not redesigned in this change.
- `styles/print.css`: existing print and generated-document rules that can safely live outside inline script strings.

Inline styles generated inside printable HTML strings remain inline because they belong to exported documents, not the app shell.

## Emoji and Decorative Effects

Visible app chrome and workflow labels use the existing outline SVG system or text. Educational content, user-authored text and literal answer feedback may retain symbols when they carry meaning. Progress rings may keep `conic-gradient`; page/card/button gradients are replaced with flat fills. Shadows remain only on floating overlays. Glass settings and backdrop filters are removed from normal app rendering.

## Testing and Rollout

- Add a static UI contract test that verifies CSS files, tokens, no glass layer, required screen structures and service-worker caching.
- Extend Playwright regressions for login, worksheet start, weak map, student list and 390px mobile behavior.
- Run existing static, runtime, print, Korean editor and database-independent tests.
- Run Taste Skill lint and inspector against login and authenticated fixture screens at 1440, 768 and 390px.
- Inspect every final screenshot and record remaining exceptions for print or chart semantics.

## Builder Decisions Left Open

- Exact helper names for the new render fragments may follow nearby project conventions as long as current public functions (`enterView`, `startView`, `weakView`, `stuView`) remain callable.
- Existing legacy CSS may initially be extracted mechanically before selective deletion; no visual changes outside the named screens are required beyond global tokens and removal of banned chrome effects.
- The authenticated browser fixture may stub remote data, but must render the real production functions and DOM.
