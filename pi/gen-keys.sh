#!/usr/bin/env bash
# JWT 비밀키와 anon/service_role 키를 만들어 .env 에 채웁니다. (이미 값이 있으면 건드리지 않습니다)
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
b64u() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
sign() { # $1=role  $2=secret
  local h p s
  h=$(printf '{"alg":"HS256","typ":"JWT"}' | b64u)
  p=$(printf '{"role":"%s","iss":"solvi","iat":%s,"exp":%s}' "$1" "$(date +%s)" "$(( $(date +%s) + 315360000 ))" | b64u)  # 10년
  s=$(printf '%s.%s' "$h" "$p" | openssl dgst -sha256 -hmac "$2" -binary | b64u)
  printf '%s.%s.%s' "$h" "$p" "$s"
}
get() { grep -E "^$1=" .env | head -1 | cut -d= -f2-; }
set_() { if grep -qE "^$1=" .env; then sed -i "s|^$1=.*|$1=$2|" .env; else echo "$1=$2" >> .env; fi; }
[ -n "$(get POSTGRES_PASSWORD)" ] || set_ POSTGRES_PASSWORD "$(openssl rand -hex 16)"
[ -n "$(get JWT_SECRET)" ] || set_ JWT_SECRET "$(openssl rand -hex 32)"
SECRET=$(get JWT_SECRET)
[ -n "$(get ANON_KEY)" ] || set_ ANON_KEY "$(sign anon "$SECRET")"
[ -n "$(get SERVICE_ROLE_KEY)" ] || set_ SERVICE_ROLE_KEY "$(sign service_role "$SECRET")"
echo ".env 준비 완료. 아래 ANON_KEY 를 index.html 의 key 로 씁니다(공개돼도 되는 키):"
get ANON_KEY
echo "SERVICE_ROLE_KEY 는 절대 공개하지 마세요."
