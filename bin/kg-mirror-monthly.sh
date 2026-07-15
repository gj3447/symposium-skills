#!/bin/bash
# kg-mirror-monthly.sh — TIER 3 offsite mirror (PROM 16 A10)
# Cron: 0 3 1 * * /Users/lagyeongjun/CD/SYMPOSIUM/bin/kg-mirror-monthly.sh
# Mirror /Users/lagyeongjun/CD/SYMPOSIUM/_archive/kg-backups/ → minio dgx:30900/kg-offsite/<YYYYMM>/
# Retention: 12 months

set -u
MC="${MC:-/opt/homebrew/bin/mc}"
ALIAS="${MC_ALIAS:-localminio}"
BUCKET="${MC_BUCKET:-kg-offsite}"
SRC="${KG_BACKUP_DIR:-/Users/lagyeongjun/CD/SYMPOSIUM/_archive/kg-backups}"
LOG="${SRC}/mirror.log"
RETENTION_MONTHS="${KG_MIRROR_RETENTION_MONTHS:-12}"

ts=$(date -u +%FT%TZ)
MONTH=$(date -u +%Y%m)

echo "[$ts] starting mirror → ${ALIAS}/${BUCKET}/${MONTH}/" >> "$LOG"

if [ ! -d "$SRC" ] || ! ls "$SRC"/kg-*.cypher 2>/dev/null > /dev/null; then
  echo "[$ts] FAIL: no kg-*.cypher backups in $SRC" >> "$LOG"
  exit 1
fi

# 신선도 가드 (2026-07-15 fix): 최신 백업이 40일 초과로 낡았으면
# stale 파일을 조용히 재업로드하지 말고 실패시킨다.
# 2026-05-11 스냅샷이 매달 재업로드되며 2개월간 백업 부재를 은폐했음.
NEWEST=$(ls -t "$SRC"/kg-*.cypher 2>/dev/null | head -1)
if [ -n "$NEWEST" ] && [ -z "$(find "$NEWEST" -mtime -40 2>/dev/null)" ]; then
  echo "[$ts] FAIL: newest backup $(basename "$NEWEST") is STALE (>40d) — 일일 백업 점검 필요. 업로드 중단." >> "$LOG"
  exit 1
fi

# Upload all kg-*.cypher and .meta.json from current month (or all if monthly)
for f in "$SRC"/kg-*.cypher "$SRC"/kg-*.cypher.meta.json; do
  [ -f "$f" ] || continue
  bn=$(basename "$f")
  "$MC" cp -q "$f" "${ALIAS}/${BUCKET}/${MONTH}/${bn}" 2>>"$LOG"
done

# Verify
count=$("$MC" ls "${ALIAS}/${BUCKET}/${MONTH}/" 2>/dev/null | wc -l | tr -d ' ')
echo "[$ts] uploaded $count files to ${ALIAS}/${BUCKET}/${MONTH}/" >> "$LOG"

# 업로드 0건이면 실패 (2026-07-15 fix): 과거 localminio alias 가 죽은
# 100.64.0.3:30900 을 가리켜 0건 업로드였는데도 exit 0 으로 성공을 가장했음.
if [ "${count:-0}" -eq 0 ]; then
  echo "[$ts] FAIL: 0 files uploaded — MinIO alias/연결 점검 필요 (mc alias list)" >> "$LOG"
  exit 1
fi

# Retention: remove months older than N
CUTOFF=$(date -u -v -${RETENTION_MONTHS}m +%Y%m 2>/dev/null || date -u --date="${RETENTION_MONTHS} months ago" +%Y%m 2>/dev/null)
if [ -n "$CUTOFF" ]; then
  "$MC" ls "${ALIAS}/${BUCKET}/" 2>/dev/null | awk '{print $NF}' | sed 's|/$||' | while read month_dir; do
    if [[ "$month_dir" =~ ^[0-9]{6}$ ]] && [ "$month_dir" \< "$CUTOFF" ]; then
      "$MC" rb --force "${ALIAS}/${BUCKET}/${month_dir}" >> "$LOG" 2>&1
      echo "[$ts] retention cleanup: removed ${month_dir} (< $CUTOFF)" >> "$LOG"
    fi
  done
fi

exit 0
