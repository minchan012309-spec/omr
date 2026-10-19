#!/usr/bin/env bash
# 하루 한 번 DB 를 통째로 저장하고 14개만 남깁니다.  사용: ./backup.sh [저장폴더]
#   crontab -e 에  30 3 * * * /home/pi/omr/pi/backup.sh /mnt/ssd/solvi-backup  를 추가하세요.
# (같은 SSD 에만 두면 SSD 고장 때 같이 사라지니, 다른 곳으로도 복사해 두세요.)
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-./backup}"; mkdir -p "$OUT"
F="$OUT/solvi-$(date +%Y%m%d-%H%M).sql.gz"
docker compose exec -T db pg_dump -U supabase_admin -d postgres --no-owner --schema=public --schema=auth --exclude-table='auth.schema_migrations' | gzip > "$F"
[ -s "$F" ] || { echo "백업 실패"; rm -f "$F"; exit 1; }
ls -1t "$OUT"/solvi-*.sql.gz | tail -n +15 | xargs -r rm -f
echo "백업 완료: $F"
