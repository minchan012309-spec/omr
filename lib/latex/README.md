# 브라우저 LaTeX 조판

조판은 자료 생성자의 브라우저 Web Worker 안에서 실행한다. Python 서버·Edge 조판·유료 조판 API는 사용하지 않는다. Supabase에는 문항 코드와 최종 쪽 구분만 저장한다.

- `engine/`: SwiftLaTeX v20022022의 XeTeX/xdvipdfmx WebAssembly 배포 파일. 원본: https://github.com/SwiftLaTeX/SwiftLaTeX/releases/tag/v20022022
- 변경: Worker 파일의 경로를 현재 스크립트 기준으로 고정, `setTexliveEndpoint`가 Worker 참조를 지우던 오류 수정, 정적 호스팅의 `fileid` 헤더 부재 처리, 엔진의 CommonJS 전역 변수 격리, 기본 패키지 주소를 같은 사이트의 정적 파일로 고정.
- `texlive/`: 원본 재현에 필요한 TeX Live 2020 정적 패키지. 다운로드 출처: https://texlive.texlyre.org/ 및 SwiftLaTeX/Texlive-Ondemand의 초기화 파일. 파일별 SHA-256은 `texlive/manifest.json`.
- `template.tex`: 사용자 제공 6–10회 XeLaTeX 원본의 preamble. 수식과 본문 글꼴 지정 유지.
- `STIXTwoMath-Regular.otf`: 원본이 지정한 TeX `stix2-otf` 패키지의 수식 글꼴.
- 개인 제공 신명조·KoPubWorld·HancomEQN 폰트는 저장소에 넣지 않는다. 사용자가 처음 한 번 등록하면 해당 브라우저 IndexedDB에 저장하며 서버로 보내지 않는다. `font-manifest.json`의 원본 해시로 확인한다.

## Supabase

`supabase/sql_27_latex_manifests.sql`을 기존 프로젝트에 적용한다. 기존 자료 테이블은 수정하지 않는다. 새 RPC는 익명/로그인 사용자의 쪽 QR 명세 저장·개별 조회만 허용하고 테이블 전체 조회·수정·삭제는 허용하지 않는다. 인쇄물이 배포된 뒤에도 QR을 유지하도록 명세에는 만료 시간을 두지 않는다.

## 초기 다운로드

엔진·포맷·패키지는 지연 로드한다. 기본 앱의 서비스 워커 초기 설치 목록에 대용량 파일을 넣지 않는다. 사용자가 조판할 때 정적 파일을 받아 일반 서비스 워커 캐시에 보관한다. 외부 패키지 서버에 컴파일 문서나 폰트를 전송하지 않는다.

## 검증

첨부 원본 문제지 7쪽을 네 지정 폰트와 STIX Two Math로 Chrome 안에서 생성했다. 원본에서 생성한 네이티브 XeLaTeX PDF와 첫 쪽을 육안 비교하고 전 7쪽을 래스터 비교했다. 엔진 버전·패키지 버전의 차이에 따른 작은 차이가 있으므로 모든 종류의 신규 교재가 완전히 동일한 조판이라고 주장하지 않는다. 앱 연결과 과목별 검증 결과는 WORKLOG와 검증 기록을 확인한다.

## 양식과 버전 보존

`printEngine`가 없는 자료는 HTML입니다. 새 자료에만 `xelatex-v1`과 `haewon-2026-v1`을 저장합니다. 이후 양식을 바꿀 때에는 이 버전의 패키지·템플릿을 덮어써 기존 출력이 바뀌게 하지 말고 새 버전과 경로를 추가해야 합니다. 기존 HTML 높이표를 새 PDF용으로 재측정하지 않습니다.

HWP 표지의 원본 용지는 771.02pt × 1116pt입니다. A4에 종횡비를 유지해 맞추는 배율은 841.89/1116입니다. 실제 글자 모양 레코드의 제목 Bold 25pt/장평 85%, 과목명 Bold 46pt, 본문 Medium 17pt를 이 배율로 변환했습니다. 본문·문제지 양식은 첨부 XeLaTeX preamble을 사용합니다. 추가 QR과 본문이 겹치지 않게 PDF 본문 하단에는 24mm를 확보합니다.

원본 폰트 4개는 사용자 제공 파일의 SHA-256으로 확인합니다. 새/대체 폰트를 자동 선택하지 않습니다. STIX의 저작권·OFL 전문은 `STIX-LICENSE.txt`, `STIX-OFL.txt`를 참고하세요. 엔진 라이선스와 수정 후 해시는 `engine/LICENSE`, `engine/manifest.json`에 있습니다.
