#!/usr/bin/env bash
# 기존 Supabase 의 데이터(학생·기록·학습지·교사 계정 등)를 Pi 로 옮깁니다.
# 준비: ① Pi 에서 ./init-db.sh 까지 끝낸 상태(표는 비어 있어야 함)
#       ② Supabase 대시보드 > Project Settings > Database > Connection string(URI) 을 SUPABASE_DB_URL 로
# 사용:  SUPABASE_DB_URL='postgresql://postgres:비밀번호@db.xxxx.supabase.co:5432/postgres' ./migrate-from-supabase.sh
# 옮기기 시작하면 Supabase 쪽에 새 데이터가 쌓이지 않도록, 전환 직전에 실행하세요.
set -euo pipefail
cd "$(dirname "$0")"
: "${SUPABASE_DB_URL:?SUPABASE_DB_URL 을 지정하세요}"
D="$(mktemp -d)"; trap 'rm -rf "$D"' EXIT
echo "1/3 Supabase 에서 내려받는 중 (public 데이터 + 교사 계정 auth.users/identities)..."
pg_dump "$SUPABASE_DB_URL" --data-only --no-owner --disable-triggers --column-inserts \
  --table='public.*' --table=auth.users --table=auth.identities > "$D/data.sql"
echo "2/3 Pi 에 넣는 중..."
docker compose exec -T db psql -U supabase_admin -d postgres -v ON_ERROR_STOP=1 -q < "$D/data.sql"
echo "3/3 확인:"
docker compose exec -T db psql -U supabase_admin -d postgres -tAc "select 'auth.users', count(*) from auth.users union all select 'students', count(*) from students union all select 'attempts', count(*) from attempts union all select 'worksheets', count(*) from worksheets"
echo "완료. 교사 비밀번호 해시도 같이 옮겨져서 기존 비밀번호로 로그인됩니다(단, JWT_SECRET 이 달라 기존 로그인 세션은 풀립니다)."
