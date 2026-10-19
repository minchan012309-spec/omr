# Solvi 라즈베리파이 서버

Supabase 에서 이 앱이 쓰던 것(DB, REST, 로그인, 패스키)만 라즈베리파이 5(2GB)로 옮기는 설치 파일입니다.
Realtime·Storage·Studio 는 앱이 쓰지 않아 뺐고, 컨테이너 합계 메모리 한도는 약 1.2GB 입니다.

> **상태: 라즈베리파이에서 직접 돌려 보지 않았습니다.** `setup.sql` 이 일반 PostgreSQL 16 에서 오류 없이 두 번 실행되는 것,
> 데이터 덤프→복원, 키 생성 스크립트의 서명은 이 저장소 쪽 환경에서 확인했습니다.
> Docker 이미지 실행, Caddy 설정, 패스키 함수, 외부 접속은 Pi 에서 처음 올릴 때 확인해야 합니다. 오류가 나면 `docker compose logs <서비스>` 내용을 알려주세요.

```
브라우저(https://solvi.p-e.kr) ──HTTPS──> Tailscale Funnel/Cloudflare Tunnel ──> Caddy(127.0.0.1:8080)
                                                ├ /rest/v1/*            -> PostgREST ─┐
                                                ├ /auth/v1/*            -> GoTrue ────┼─> PostgreSQL (USB SSD)
                                                └ /functions/v1/passkey -> Deno(패스키)┘
```

## 0. 준비물
- 라즈베리파이 5 + **64비트** Raspberry Pi OS Lite, 가능하면 **USB SSD 로 부팅**(또는 DB 폴더만 SSD)
- 학교 인터넷(바깥 포트 개방 없이 쓸 수 있는 방법을 아래에서 고릅니다)
- 정전 대비: 가능하면 UPS 또는 안전 종료 방법

## 1. Pi 기본 설정
```bash
sudo apt update && sudo apt full-upgrade -y
curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker $USER   # 다시 로그인
# 메모리 2GB 이므로 zram 스왑을 켭니다
sudo apt install -y zram-tools && echo -e "ALGO=zstd\nPERCENT=50" | sudo tee /etc/default/zramswap && sudo systemctl restart zramswap
# SSD 를 /mnt/ssd 에 마운트해 두었다면 DB 폴더를 만듭니다
sudo mkdir -p /mnt/ssd/solvi && sudo chown $USER /mnt/ssd/solvi
```

## 2. 올리기
```bash
git clone https://github.com/minchan012309-spec/omr.git && cd omr/pi
./gen-keys.sh          # .env 를 만들고 비밀번호·JWT 키를 채웁니다 (ANON_KEY 가 출력됩니다)
nano .env              # SITE_URL, API_URL, DATA_DIR 확인 (API_URL 은 3단계 후 알게 됩니다)
docker compose up -d
./init-db.sh           # 표·함수·접근 정책 만들기 (setup.sql). 다시 실행해도 안전
curl -s localhost:8080/health   # ok 가 나오면 게이트웨이 동작
```

## 3. 바깥에서 HTTPS 로 접속되게 (둘 중 하나)
브라우저가 `https://solvi.p-e.kr` 에서 Pi 로 요청하므로 **Pi 도 HTTPS 주소**가 필요합니다.

**A. Tailscale Funnel (도메인 없이 가능, 권장)**
```bash
curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up
# Tailscale 관리 콘솔(DNS 탭)에서 HTTPS 인증서를 켜고, ACL 에서 Funnel 을 허용한 뒤:
sudo tailscale funnel --bg 8080      # https://<기기이름>.<tailnet>.ts.net 주소가 나옵니다
```
그 주소를 `.env` 의 `API_URL` 에 넣고 `docker compose up -d` 로 다시 올립니다.

**B. Cloudflare Tunnel** — 도메인의 DNS 를 Cloudflare 에서 관리할 수 있을 때만 가능합니다. `p-e.kr` 같은 무료 도메인은 보통 불가하니, 자기 도메인(예: `api.내도메인.com`)이 있을 때만 고르세요.

> 학교 네트워크 정책(외부 터널 허용 여부)은 담당 선생님께 확인하세요.

## 4. 개발자·교사 계정
- 기존 데이터를 옮기면 교사 계정과 개발자 등록도 같이 옮겨집니다(5단계).
- 새로 시작한다면: 앱에서 회원가입한 뒤, 아래를 실행해 개발자로 등록합니다.
```bash
docker compose exec -T db psql -U supabase_admin -d postgres -c "insert into developers(user_id,email) select id,email from auth.users where email='내이메일@example.com' on conflict do nothing"
```
- 이메일 인증: SMTP 서버가 없으면 `.env` 의 `MAILER_AUTOCONFIRM=true`(가입 즉시 사용)로 둡니다. 가입 승인 절차(앱의 가입 요청 승인)는 그대로 동작합니다.

## 5. 기존 Supabase 데이터 옮기기 (전환 직전에)
```bash
sudo apt install -y postgresql-client
SUPABASE_DB_URL='postgresql://postgres:비밀번호@db.xxxx.supabase.co:5432/postgres' ./migrate-from-supabase.sh
```
교사 비밀번호 해시가 같이 옮겨져 기존 비밀번호로 로그인됩니다. JWT 키가 달라서 **로그인 세션은 전부 풀립니다**(다시 로그인). 패스키는 같은 사이트 주소(`solvi.p-e.kr`)이므로 그대로 쓸 수 있을 가능성이 높지만, 안 되면 다시 등록하세요.

## 6. 앱을 Pi 로 전환
`index.html` 의 `loadCfg()` 에서 **두 값만** 바꿉니다.
```js
CF={url:'<API_URL>', key:'<ANON_KEY>', pub:'https://solvi.p-e.kr/'}
```
그리고 `books.js`/`dev.js` 는 건드리지 않으므로 `?v=` 번호는 그대로 둡니다. 배포 후 `sw.js` 의 `VER` 를 하나 올리면 학생 기기에서도 빠르게 갱신됩니다.
**되돌리기**: 위 두 값을 예전 Supabase 값으로 되돌리면 됩니다(전환 후 Pi 에 쌓인 데이터는 Supabase 에 없습니다).

## 7. 백업과 운영
```bash
crontab -e   # 매일 새벽 3시 30분 백업 (14개 보관)
30 3 * * * /home/pi/omr/pi/backup.sh /mnt/ssd/solvi-backup
```
- **다른 장소로도 복사**해 두세요(SSD 고장 대비). 복원: `gunzip -c 백업.sql.gz | docker compose exec -T db psql -U supabase_admin -d postgres`
- 상태: `docker compose ps`, `docker stats --no-stream`(메모리), `docker compose logs -f auth rest passkey`
- 업데이트: `git pull && docker compose pull && docker compose up -d` (그 전에 백업)
- 개인정보: 학생 이름·풀이 기록이 학교 기기에 저장됩니다. 학교의 개인정보 보호 지침에 맞춰 접근 권한과 보관 기간을 정하세요.

## 문제 확인 순서
1. `curl -s localhost:8080/health` → ok 아니면 `docker compose logs gateway`
2. `curl -s -H "apikey: $ANON_KEY" localhost:8080/rest/v1/site_config?select=key&limit=1` → `[]` 또는 목록이면 REST 정상
3. `curl -s localhost:8080/auth/v1/health` → GoTrue 정상
4. 앱의 개발자 탭 → 진단에서 "Supabase REST", "패스키 함수" 점검 항목 확인
