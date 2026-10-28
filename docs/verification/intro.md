# Solvi 인트로 검증 — 2026-10-29

## 구현

- `intro.html`, `intro.css`, `intro.js`만으로 정적 배포 구조 유지. Solvi 로고, 남색·노랑, Pretendard 유지.
- 연속 스크롤: 문제 선택 → 교재 → QR/OMR → 취약 유형 분석. 스크롤 가로채기, 슬라이드 스냅, 타이머 자동 전환 없음.
- 데스크톱: 태블릿 기울기와 크기, 노트북 키보드 등장, 교재 표지 3D 열림과 실제 내부 쪽 넘김, OMR 휴대폰과 채점 결과, 실제 분석 화면 교체를 스크롤 위치에 연결.
- 모바일(900px 이하), reduced motion, no-JS는 순서대로 읽는 실제 화면과 교재 이미지 제공. 본문 숨김에 JavaScript 성공을 요구하지 않음.
- 실제 `index.html?app=1`, `#login`, `#student` 목적지와 `omr_app` localStorage 규약 보존.
- 기존 가격 조회 계약 `/rest/v1/site_config?key=eq.pricing&select=value` 유지. 기존 코드에는 가격 RPC 호출이 없었으며 이 공개 조회와 실패 시 HTML 기본 가격을 보존했다. 가격 기능 선택과 동적 가격·문의 링크 동작 유지. 외부 설정의 문의 주소는 HTTP(S)/이메일만 허용.
- 기존 정적 기능 비교표는 서버에서 요금제가 바뀔 때 실제 가격 카드와 달라질 수 있어 제거.

## 디자인 근거

적용 skill: `design-taste-frontend`, `design-motion-principles` Create workflow. 방향 draw: `colour-chapters` (palette/type 유지, redraw 없음). 실제 Solvi의 인쇄 학습지와 QR이 화면→교재→채점→다음 학습을 연결하는 소재가 된다. Jakub의 절제된 전환을 중심으로 Jhey의 CSS 3D를 제품 설명에 한정. 별도 라이브러리와 새 원격 자산 없음.

실제 자산: `intro/`의 display, app-build, app-weak, app-stu, book-sheet/cover/toc/concept/problem/ox, phone-omr/result/home/parent WebP. `tools/capture_intro.js`의 실제 제품 캡처 자산이며 예시 학생·학습 데이터임을 본문에 표시했다. 외부 사진·영상·유료 디자인 없음. 새 고객 수, 성과 수치, 후기는 만들지 않음.

## 실행한 검증

- `node --check intro.js`, `node --check tests/intro-regression.cjs`: 통과.
- `node tests/intro-regression.cjs`: Chrome headless, `http://127.0.0.1:8765`에서 통과.
- 검증 내용: 기존 가격 요청/서버 응답 렌더링/문의 링크/기능별 추천, 가격 조회 실패 기본 카드, 모든 이미지 URL 응답, 태블릿→노트북, 표지 열림과 내부 쪽 회전, OMR 등장, 분석 UI 교체, 앱 저장 규약, 1440/768/390 가로 넘침 없음, 모바일 메뉴 Escape 및 포커스, reduced motion에서 모든 핵심 이미지, no-JS의 본문·기본 요금·네이티브 FAQ.
- 디자인 lint: **0 FAIL / 0 WARN**.
- 디자인 browser inspector 최종: **0 FAIL / 2 WARN**. 1440/768/390에서 제목 최대 2줄, Pretendard 확인, 실제 이미지 18개. 남은 경고: 크기 종류 16개(실제 제품 UI·가격 숫자·대형 워드마크 포함), 영상 없음(실제 제품 스크롤 스토리로 대체; 관련 없는 영상 추가하지 않음).
- 스크린샷 육안 확인: 데스크톱 hero/book/OMR, 모바일 hero/OMR와 전체 흐름. 첫 검토의 키보드/흐름 링크 중첩을 줄이도록 기기 크기와 위치 수정. 최종 OMR에서는 제품 화면 아래 흐름 링크가 분리됨.
- 자체 시각 평가: 구성 8/10, 브랜드 8/10, 가독성 8/10, 움직임 8/10. 제품 내 작은 글씨는 확대된 실서비스가 아닌 실제 화면을 설명하는 증거 이미지라는 한계가 있다.

## 결과물

- `/tmp/solvi-intro-verification/`: desktop-hero/book/omr/analysis, viewport-1440/768/390 전체 이미지, mobile-hero/omr, no-js, reduced-motion PNG.
- `/tmp/solvi-intro-taste-final/report.json`: 디자인 inspector 상세 수치.
- `/tmp/solvi-intro-taste-final/`: desktop/tablet/mobile 화면별 JPG.

## 검증 범위 밖

실서비스 가격 값·인증·DB 쓰기, 실제 교재 인쇄, 실제 학생 기록, iOS Safari/Android 기기, 저사양 GPU 성능은 검증하지 않았다. 가격 테스트는 고정 응답과 실패 응답으로 계약만 검증했으며 운영 DB를 수정하지 않았다. 로컬 캡처는 저장소에 포함하지 않음.
