# Pi 문제은행 분리와 자동 백업 설계

## 의도

GitHub Pages에 있는 대용량 문제은행 JSON을 집의 Raspberry Pi 5 SSD로 옮겨, 앱 코드 저장소가 문항 데이터 증가로 커지지 않게 한다. 선생님이 브라우저에서 직접 내려받아야 했던 로컬 JSON 백업도 Pi SSD에 자동 보관한다.

## 현재 확인한 상태

- 앱은 `index.html`의 `DIRS` 상대 경로로 `bank/`, `cm/`, `ph/`, `hl/` JSON을 가져온다.
- 물질과 에너지의 초기 문항은 HTML보다 먼저 `bank/data.js`를 일반 스크립트로 불러온다.
- `backupAll()`은 `omr_` 로컬 저장소를 다운로드할 뿐, 서버에는 올리지 않는다.
- 문제 데이터 폴더는 약 113MB이며, GitHub에 복사된 현재 Pi 배포만으로는 GitHub 저장소 용량이 줄지 않는다.
- Pi에는 CasaOS, SSD, Cloudflare Tunnel이 준비되어 있으며 정적 Nginx 컨테이너가 `localhost:8000`을 제공한다.

## 선택한 구조

```text
solvi.win (GitHub Pages: 앱 코드)
  ├─ https://bank.solvi.win/bank|cm|ph|hl/... (Pi SSD: 문제 데이터)
  └─ https://bank.solvi.win/api/backups (Pi SSD: 선생님 자동 백업)
```

`solvi.win`은 앱 코드와 서비스 워커를 GitHub Pages에서 빠르게 제공한다. `bank.solvi.win`은 Cloudflare Tunnel을 거쳐 Pi의 CasaOS Nginx 및 백업 API로 연결한다. Pi가 잠시 꺼져도 로그인과 앱 껍데기는 열리며 문제은행·자동 백업에만 오류 안내가 표시된다.

### 전환 순서

현재 `solvi.win`은 Pi Tunnel을 가리키므로, 바로 DNS를 바꾸지 않는다. 먼저 Pi에 `bank.solvi.win` 공개 호스트명을 추가해 데이터·백업 API를 검증한다. 그 뒤 `solvi.win`을 GitHub Pages로 되돌리고, 앱을 배포한다. 전환 중에는 Pi CORS에 기존 `https://solvi.p-e.kr`와 새 `https://solvi.win`을 임시로 모두 허용하며, 전환 확인 뒤에는 `https://solvi.win`만 남긴다.

## 목표

- 문제은행 JSON과 `bank/data.js`를 Pi SSD에서 읽는다.
- 외부 데이터 요청은 `https://bank.solvi.win/` 한 곳으로 설정 가능하다.
- 서비스 워커의 같은 출처 캐싱을 깨지 않고, 외부 데이터는 기존 오프라인 내려받기 흐름에서 명시적으로 캐시한다.
- 선생님 로그인 뒤와 활성 세션 중 15분마다 브라우저의 `omr_` 로컬 데이터를 Pi SSD로 업로드한다.
- 자동 백업은 Supabase 로그인 토큰을 검증하고, 로그인 사용자 ID별 디렉터리에 압축 저장한다.
- 변경된 내용만 업로드하면서, 최근 24시간은 최대 15분 간격으로 보관하고 이후에는 하루별 최신 한 개를 30일간 보관한다.
- 계정 하나가 SSD를 과도하게 점유하지 않도록 256MB의 안전 상한을 둔다. 상한에 닿으면 오래된 파일부터 정리하고, 그래도 저장할 수 없으면 앱에 수동 JSON 내려받기 안내를 남긴다.
- 수동 JSON 내려받기·불러오기는 비상 복구 수단으로 유지한다.

## 비목표

- Supabase의 인증·운영 데이터·결제 데이터를 Pi로 옮기지 않는다.
- 현재 Git 기록을 이 작업에서 강제로 다시 쓰지 않는다. 데이터 경로 전환과 실제 Pi 배포를 검증한 뒤, 별도 승인으로 기록 정리 또는 새 앱 저장소 전환을 한다.
- 동일 SSD 안의 자동 백업을 재해 복구 백업으로 주장하지 않는다. 별도 외장 저장소나 클라우드 복제는 후속 작업이다.

## 데이터 경로 설계

- `BANK_ORIGIN`은 기본값이 빈 문자열인 앱 설정 상수다. 비어 있으면 개발·로컬 검증은 기존 상대 경로를 그대로 쓴다.
- 운영값은 `https://bank.solvi.win`이며, 과목별 JSON URL은 이 값과 기존 `DIRS` 경로를 결합한다.
- `bank/data.js`는 외부 일반 스크립트로 로드하되, 로드 실패 시 문제은행 연결 오류를 명확히 표시한다.
- Pi Nginx는 `solvi.win`만 허용하는 CORS 응답 헤더를 JSON·JS 응답에 보낸다.
- Pi 배포물은 현재의 CasaOS Nginx 앱을 덮어쓰지 않고, 별도 `solvi-bank` Compose 앱으로 설치한다. SSD 실제 마운트 이름은 CasaOS마다 달라질 수 있으므로 `QUESTION_BANK_ROOT`, `BACKUP_ROOT` 환경 변수로 지정한다.
- 데이터의 원본은 개발용 Mac의 네 과목 폴더이고, 명시적 배포 스크립트가 Pi SSD의 읽기 전용 데이터 폴더에 복사한다. 전환 검증 전에는 Git의 기존 데이터 파일을 지우지 않는다.

## 자동 백업 설계

- 클라이언트는 현재 `backupAll()`이 수집하는 것과 같은 `omr_` 키들(인증 세션 키 제외)을 JSON 본문으로 만든다.
- 선생님 계정만 업로드하며 학생·학부모 화면에서는 실행하지 않는다. 현재 데이터 모델에는 별도 교사 역할 테이블이 없고 `teacher_settings.user_id`가 선생님 Supabase 계정의 소유자이므로, 검증된 Supabase 사용자 ID가 해당 행의 소유자인지를 API가 확인한다.
- 요청에는 기존 Supabase access token을 `Authorization: Bearer`로 보낸다.
- Pi API는 Supabase Auth 사용자 조회로 토큰을 검증하고, 사용자 ID 외의 경로는 클라이언트가 지정할 수 없게 한다.
- API는 JSON 크기 제한을 적용하고 gzip 파일을 `<SSD>/solvi-backups/teachers/<user-id>/<UTC timestamp>.json.gz`에 원자적으로 저장한다.
- 직전 payload의 SHA-256이 같으면 새 업로드를 건너뛴다. 저장 성공 때만 `omr_lastbk`를 갱신한다. 실패하면 기존 백업 안내를 남기고, 다음 15분 주기와 다음 로그인에서 재시도한다.
- Pi 정리 작업은 위 보존 규칙·용량 상한에 해당하는 파일만 삭제한다.

## 배포와 되돌리기

- GitHub Pages 앱은 새 데이터 원본을 설정한 뒤 배포하며 서비스 워커 버전을 올린다.
- Pi에는 문제 데이터 전용 배포 폴더와 API 컨테이너를 별도로 둔다. 앱 소스 전체를 Pi의 원본으로 취급하지 않는다.
- Cloudflare Tunnel은 `bank.solvi.win → http://localhost:<solvi-bank 포트>`로 연결한다. `solvi.win`의 Tunnel route는 GitHub Pages 전환이 끝나면 제거한다.
- 장애가 나면 `BANK_ORIGIN`을 빈 값으로 되돌려 기존 GitHub Pages의 상대 경로 배포로 복귀한다. 자동 백업 업로드 실패는 앱 사용을 막지 않는다.

## 보안·개인정보 제약

- 백업 API는 인증되지 않은 요청·다른 사용자 ID 지정·디렉터리 열람·다운로드를 허용하지 않는다.
- Pi는 Cloudflare Tunnel로만 공개하고 공유기 포트포워딩은 하지 않는다.
- 백업 파일은 실제 학생 기록을 포함하므로 Git에 추가하지 않고, CasaOS 관리자 계정·Pi 계정·SSD 물리 접근을 보호한다.

## 검증 기준

- 앱이 `bank.solvi.win`에서 각 과목 index·data·유형 JSON을 읽고 문제 제작을 완료한다.
- Pi를 끈 상황에서 앱이 문제은행 연결 실패를 안내하고 다른 UI가 예외로 멈추지 않는다.
- 로그인한 선생님의 자동 백업만 SSD에 생성되며 다른 계정의 경로에는 쓸 수 없다.
- 새 자동 백업 성공 후 백업 알림이 사라지고, 실패 시 수동 다운로드가 계속 가능하다.
- 서비스 워커·오프라인 패키지·기존 전체 회귀가 유지된다.
