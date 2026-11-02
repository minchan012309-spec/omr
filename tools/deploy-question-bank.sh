#!/usr/bin/env bash
set -euo pipefail

usage() { echo "사용법: $0 --destination user@pi:/SSD/solvi-question-bank [--dry-run]" >&2; exit 2; }
destination=""; dry=""
while (($#)); do
  case "$1" in
    --destination) destination="${2:-}"; shift 2 ;;
    --dry-run) dry="--dry-run"; shift ;;
    *) usage ;;
  esac
done
[[ -n "$destination" ]] || usage
for dir in bank cm ph hl; do [[ -d "$dir" ]] || { echo "문제 폴더가 없습니다: $dir" >&2; exit 1; }; done
echo "전송 대상: $destination"
echo "전송 폴더: bank cm ph hl"
rsync -av $dry bank cm ph hl "$destination"
