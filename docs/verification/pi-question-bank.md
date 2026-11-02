# Pi 문제은행·자동 백업 배포 확인

## CasaOS에 올리기

1. SSD에 `solvi-question-bank`, `solvi-backups` 폴더를 만든다.
2. `pi/question-bank/.env.example`를 CasaOS의 Compose 환경 변수에 맞게 채운다. `QUESTION_BANK_ROOT`와 `BACKUP_ROOT`는 SSD의 절대 경로다.
3. CasaOS에서 **사용자 정의 Compose 앱**으로 `pi/question-bank/docker-compose.yml`을 올린다. 기존 8000번 Nginx 앱은 건드리지 않고 기본 포트 8010을 쓴다.
4. Cloudflare Tunnel에 `bank.solvi.win` Published application을 하나 추가하고 서비스 URL을 `http://localhost:8010`으로 설정한다.
5. `https://bank.solvi.win/bank/index.json`을 열어 JSON이 보이는지 확인한다.

## 앱 전환 순서

1. Mac 저장소에서 `tools/deploy-question-bank.sh --destination 'server@라즈베리IP:/SSD/solvi-question-bank/'`를 실행해 네 과목 폴더를 전송한다. 처음에는 `--dry-run`으로 목록만 확인한다.
2. `bank.solvi.win`에서 index.json이 열리는 것을 먼저 확인한다.
3. GitHub Pages Custom domain을 `solvi.win`으로 설정하고 Cloudflare DNS를 GitHub Pages 안내에 맞춘다. 기존 루트 Tunnel route는 마지막에 지운다.
4. 새 `https://solvi.win`으로 로그인해 문제 제작과 자동 백업을 확인한다. 선생님 계정으로 15분을 기다리거나 새로 로그인한 뒤 SSD의 `solvi-backups/teachers/<UUID>/`에 `.json.gz`가 생기는지 확인한다.

## 되돌리기

Pi 장애 때는 `bank-origin.js`의 운영 원점을 빈 값으로 바꾸고 GitHub Pages에 기존 문제 파일이 남아 있는 상태에서 배포한다. 수동 **백업 내려받기**는 자동 백업과 별개로 계속 쓸 수 있다.

> 자동 백업 SSD는 학생 기록을 포함한다. CasaOS 관리자 계정·Pi 비밀번호를 보호하고, SSD 고장에 대비한 별도 복제는 이후에 추가한다.
