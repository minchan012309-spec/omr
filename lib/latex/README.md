> 현재 앱의 LaTeX 생성 경로는 폐기되었습니다. 이 폴더의 원본 글꼴 파일만 HTML/HWPX의 글꼴 제공에 계속 사용합니다. 아래는 이전 실험의 출처 기록입니다.

# 브라우저 LaTeX 조판

조판은 자료 생성자의 브라우저 Web Worker 안에서 실행한다. Python 서버·Edge 조판·유료 조판 API는 사용하지 않는다. Supabase에는 문항 코드와 최종 쪽 구분만 저장한다.

- `engine/`: SwiftLaTeX v20022022의 XeTeX/xdvipdfmx WebAssembly 배포 파일. 원본: https://github.com/SwiftLaTeX/SwiftLaTeX/releases/tag/v20022022
- 변경: Worker 파일의 경로를 현재 스크립트 기준으로 고정, `setTexliveEndpoint`가 Worker 참조를 지우던 오류 수정, 정적 호스팅의 `fileid` 헤더 부재 처리, 엔진의 CommonJS 전역 변수 격리, 기본 패키지 주소를 같은 사이트의 정적 파일로 고정. 고정 배포본의 `dvipdfmx_main` 압축 인수를 켜는 재현 스크립트는 `tools/enable_latex_pdf_compression.cjs`이며 WASM 해시를 먼저 확인한다.
- `texlive/`: 원본 재현에 필요한 TeX Live 2020 정적 패키지. 다운로드 출처: https://texlive.texlyre.org/ 및 SwiftLaTeX/Texlive-Ondemand의 초기화 파일. 파일별 SHA-256은 `texlive/manifest.json`.
- `template.tex`: 사용자 제공 6–10회 XeLaTeX 원본의 preamble. 수식과 본문 글꼴 지정 유지.
- `STIXTwoMath-Regular.otf`: 원본이 지정한 TeX `stix2-otf` 패키지의 수식 글꼴.
- `fonts/`: 사용자가 정적 사이트 배포를 지시한 신명조·KoPubWorld·HancomEQN 원본 4개. 사이트에서 자동으로 내려받으며 `font-manifest.json`의 SHA-256과 일치하는지 확인한다. 이용자가 별도로 폰트를 등록할 필요가 없다.

## Supabase

`supabase/sql_27_latex_manifests.sql`을 기존 프로젝트에 적용한다. 기존 자료 테이블은 수정하지 않는다. 새 RPC는 익명/로그인 사용자의 쪽 QR 명세 저장·개별 조회만 허용하고 테이블 전체 조회·수정·삭제는 허용하지 않는다. 인쇄물이 배포된 뒤에도 QR을 유지하도록 명세에는 만료 시간을 두지 않는다.

## 미리보기와 최종 저장

출력 창이 열리면 자동으로 조판하고, 제목·표지·유형명·문항코드 등 설정을 바꾸면 입력을 잠시 멈춘 뒤 최신 설정을 반영한다. 갱신 중에는 마지막 정상 PDF를 유지하고, 이미 시작된 이전 설정의 결과는 화면에 적용하지 않는다. 정상 조판 후 Worker와 내려받은 TeX 패키지는 재사용하며 문서 작업 파일은 매번 비운다. 취소·오류·창 닫기에는 Worker를 정리한다.

미리보기는 Supabase에 명세를 쓰지 않는다. **PDF 저장 또는 인쇄를 누를 때** 해당 PDF의 QR 명세를 저장한 다음 자료의 최종 출력 기록을 갱신한다. 같은 결과를 다시 저장할 때에는 명세를 중복 생성하지 않는다.

## 초기 다운로드

엔진·포맷·패키지는 지연 로드한다. 기본 앱의 서비스 워커 초기 설치 목록에 대용량 파일을 넣지 않는다. 사용자가 조판할 때 정적 파일을 받아 일반 서비스 워커 캐시에 보관한다. 외부 패키지 서버에 컴파일 문서나 폰트를 전송하지 않는다.

## 교재 디자인과 학습지 양식의 분리

학습지·모의고사는 첨부 XeLaTeX 본문과 HWP 표지를 사용한다. 새 교재는 `book-original-v1` 별도 경로로 기존 `bkPlan`/`bkDocHtml`의 페이지·색상·표지·글꼴·목차·개념·문제·해설을 유지한다. 기존 교재 미리보기와 디자인 설정도 유지한다. 교재는 원래 브라우저 레이아웃의 본문 위치와 글꼴을 측정해 native XeTeX 텍스트로 배치하며, 비텍스트 장식·그림·일부 수식은 원래 렌더링을 배경 자산으로 보존한다. 문서 전체를 이미지로 만드는 방식은 아니다. 지원되는 원본 TTF가 없는 글꼴을 선택하면 필요한 파일명을 알리고 자동 대체하지 않는다.

기존 교재의 WOFF2 글꼴 14개는 문자표·폭·윤곽을 유지한 SFNT로 변환한다. 파일별 원본·변환 후 해시는 `book-font-sources.json`, 로딩 해시는 `optional-font-manifest.json`에 있다. 기본 교재는 기존 Pretendard이며 신명조로 강제 변경하지 않는다.

미리보기 작업은 직렬 대기열로 처리하고, 창별 취소는 다른 창의 작업을 취소하지 않는다. PDF의 QR은 JavaScript로 생성해 실제 쪽에 삽입한다. 원본 픽셀을 유지한 zlib 압축으로 큰 교재 배경도 손실 없이 저장한다.

## 검증

첨부 원본 문제지 7쪽을 네 지정 폰트와 STIX Two Math로 Chrome 안에서 생성했다. 원본에서 생성한 네이티브 XeLaTeX PDF와 첫 쪽을 육안 비교하고 전 7쪽을 래스터 비교했다. 엔진 버전·패키지 버전의 차이에 따른 작은 차이가 있으므로 모든 종류의 신규 교재가 완전히 동일한 조판이라고 주장하지 않는다. 앱 연결과 과목별 검증 결과는 WORKLOG와 검증 기록을 확인한다.

## 양식과 버전 보존

`printEngine`가 없는 자료는 HTML입니다. 새 자료에만 `xelatex-v1`과 `haewon-2026-v1`을 저장합니다. 이후 양식을 바꿀 때에는 이 버전의 패키지·템플릿을 덮어써 기존 출력이 바뀌게 하지 말고 새 버전과 경로를 추가해야 합니다. 기존 HTML 높이표를 새 PDF용으로 재측정하지 않습니다.

HWP 표지의 원본 용지는 771.02pt × 1116pt입니다. A4에 종횡비를 유지해 맞추는 배율은 841.89/1116입니다. 실제 글자 모양 레코드의 제목 Bold 25pt/장평 85%, 과목명 Bold 46pt, 본문 Medium 17pt를 이 배율로 변환했습니다. 본문·문제지 양식은 첨부 XeLaTeX preamble을 사용합니다. 본문은 원본의 12mm 상단·16.5mm 하단 여백과 195/235mm 첫 쪽·후속 쪽 단 높이를 사용합니다. QR은 본문 밖 하단에 배치합니다. 해설도 2단이며, 지문 첫 두 줄만 단 끝에 남기는 쪽 나눔을 막습니다.

원본 폰트 4개는 사용자 제공 파일의 SHA-256으로 확인합니다. 새/대체 폰트를 자동 선택하지 않습니다. STIX의 저작권·OFL 전문은 `STIX-LICENSE.txt`, `STIX-OFL.txt`를 참고하세요. 엔진 라이선스와 수정 후 해시는 `engine/LICENSE`, `engine/manifest.json`에 있습니다.

기존 교재 글꼴의 SIL OFL 전문은 `PRETENDARD-OFL.txt`, `PAPERLOGY-OFL.txt`와 저장소 기존 `fonts/SolviSymbols-OFL.txt`에 있습니다. KoPub 부분 글꼴의 기존 저작권 메타데이터는 변환한 SFNT 안에 그대로 보존됩니다.
