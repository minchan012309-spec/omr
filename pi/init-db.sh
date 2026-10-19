#!/usr/bin/env bash
# 컨테이너를 처음 올린 뒤 한 번 실행: GoTrue 가 auth 표를 만든 것을 확인하고 setup.sql 을 적용합니다. 다시 실행해도 안전합니다.
set -euo pipefail
cd "$(dirname "$0")"
DC="docker compose"
echo "GoTrue 가 DB 를 준비할 때까지 기다리는 중..."
for i in $(seq 1 60); do
  if $DC exec -T db psql -U supabase_admin -d postgres -tAc "select to_regclass('auth.users') is not null" 2>/dev/null | grep -q t; then ok=1; break; fi
  sleep 3
done
[ "${ok:-}" = 1 ] || { echo "auth.users 가 없습니다. 'docker compose logs auth' 를 확인하세요."; exit 1; }
echo "setup.sql 적용 중..."
$DC exec -T db psql -U supabase_admin -d postgres -v ON_ERROR_STOP=1 -q < ../setup.sql
# PostgREST 가 새 함수·표를 바로 알도록
$DC kill -s SIGUSR1 rest >/dev/null 2>&1 || true
echo "완료. 다음: README 의 '개발자 계정 등록' 단계."
