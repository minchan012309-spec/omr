#!/usr/bin/env bash
# Solvi 문제 데이터 서버 설치 (Raspberry Pi OS / Debian 계열, sudo 로 실행)
#   sudo bash pi/setup.sh
# 하는 일: Caddy(파일 서버) 설치 → 저장소의 문제 데이터 폴더만 내려받기 → 5분마다 자동 갱신 → Tailscale 설치
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "sudo bash pi/setup.sh 로 실행해 주세요"; exit 1; }

REPO_URL="${REPO_URL:-https://github.com/minchan012309-spec/omr.git}"
BRANCH="${BRANCH:-main}"
DIR=/srv/solvi/repo
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "[1/5] 필요한 프로그램 설치"
apt-get update -y
apt-get install -y git curl debian-keyring debian-archive-keyring apt-transport-https gpg
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -y
  apt-get install -y caddy
fi

echo "[2/5] 문제 데이터 내려받기 (bank cm ph hl 폴더만)"
mkdir -p /srv/solvi
if [ ! -d "$DIR/.git" ]; then
  git clone --filter=blob:none --sparse --branch "$BRANCH" "$REPO_URL" "$DIR"
fi
git -C "$DIR" sparse-checkout set bank cm ph hl
git -C "$DIR" pull --ff-only
chown -R caddy:caddy /srv/solvi 2>/dev/null || true

echo "[3/5] 파일 서버 설정"
install -m 644 "$HERE/Caddyfile" /etc/caddy/Caddyfile
systemctl enable --now caddy
systemctl reload caddy || systemctl restart caddy

echo "[4/5] 5분마다 자동 갱신"
cat > /etc/systemd/system/solvi-sync.service <<S
[Unit]
Description=Solvi data sync
[Service]
Type=oneshot
ExecStart=/usr/bin/git -C $DIR pull --ff-only
S
cat > /etc/systemd/system/solvi-sync.timer <<S
[Unit]
Description=Solvi data sync every 5 minutes
[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
[Install]
WantedBy=timers.target
S
systemctl daemon-reload
systemctl enable --now solvi-sync.timer

echo "[5/5] Tailscale 설치 (밖에서 접속하게 해 주는 프로그램, 공유기 설정 필요 없음)"
if ! command -v tailscale >/dev/null; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi

echo
echo "여기까지 끝났습니다. 확인: curl http://127.0.0.1:8080/health  → ok"
echo "다음 단계는 pi/README.md 의 '4. 밖에서 접속되게 하기' 를 보세요."
