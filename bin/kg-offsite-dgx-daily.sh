#!/bin/bash
# kg-offsite-dgx-daily.sh — TIER 3-B 진짜 오프사이트: 별개 물리 호스트(DGX)로 일일 사본
# Cron(제안, 미설치): 30 2 * * * /Users/lagyeongjun/CD/SYMPOSIUM/bin/kg-offsite-dgx-daily.sh
#
# 왜 필요한가 (2026-07-27 실측):
#   기존 TIER 3 = kg-mirror-monthly.sh → mc localminio(kg-offsite).
#   그런데 localminio 는 macmini localhost:9000 이고, 그 socat 은
#     TCP-LISTEN:9000 → TCP:192.168.0.25:9000  (= data-01)
#   KG 원본 Neo4j 도 같은 VM:
#     TCP-LISTEN:7687 → TCP:192.168.0.25:7687  (= data-01)
#   즉 "오프사이트 미러"가 원본과 같은 VM 에 있다. data-01 사망 = 원본+미러 동시 소멸.
#   호스트 밖 사본은 macmini 로컬 7일치가 전부였다.
#
#   DGX(192.168.0.23, edgexpert-e229)는 systemd-detect-virt=none 인 별개 물리 머신이고
#   data-01 은 MAC bc:24:11:* (Proxmox VM OUI) 인 가상머신이다 → 장애 도메인 분리 확인.
#   ⚠️ 정직한 한계: 같은 LAN(192.168.0.0/24) 같은 건물이다. 호스트 단위 장애는 커버하지만
#      화재/침수/건물 정전은 커버하지 못한다. 진짜 지리적 오프사이트는 별도 과제로 남는다.
#
# Retention: daily 14 + monthly 12
#
# 가드 — kg-mirror-monthly.sh 의 2026-07-15 조용한-실패 방지 가드를 계승/강화:
#   (a) 최신 백업이 낡았으면 stale 재업로드 대신 실패.
#       원본은 월간 케이던스라 40일이었으나, 본 레인은 일간이므로 2일로 강화.
#   (b) 최종 원격 파일 수가 0 이면 exit 1 (성공 가장 금지)
#   (c) 직전 푸시와 sha256 이 같은데 파일명이 다르면 실패.
#       2026-05~07 사고의 정확한 서명 = "같은 파일이 매달 재업로드되며 백업 부재를 은폐"
#   (d) 전송 후 원격에서 gunzip|sha256sum 으로 end-to-end 무결성 검증. 불일치 시 .part 폐기 후 실패
#   (e) 원격 여유 공간 부족 시 사전 실패
#   (f) meta.json sha256 대조 — 반쯤 쓰인/손상된 덤프를 밀어올리지 않는다
#
# 설계 메모: macmini 데이터 볼륨이 93% (여유 13Gi) 이므로 로컬 임시 압축파일을 만들지 않는다.
#   gzip -c → ssh cat 스트리밍으로 로컬 디스크를 전혀 쓰지 않는다.

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"   # cron PATH 에 brew 없음 (2026-07-15 fix)
set -u

SRC="${KG_BACKUP_DIR:-/Users/lagyeongjun/CD/SYMPOSIUM/_archive/kg-backups}"
LOG="${SRC}/offsite-dgx.log"
DGX_HOST="${KG_OFFSITE_HOST:-dgx}"
RDIR="${KG_OFFSITE_REMOTE_DIR:-\$HOME/kg-offsite}"   # 원격 쉘이 전개한다
MAX_AGE_DAYS="${KG_OFFSITE_MAX_AGE_DAYS:-2}"
DAILY_KEEP="${KG_OFFSITE_DAILY_KEEP:-14}"
MONTHLY_KEEP="${KG_OFFSITE_MONTHLY_KEEP:-12}"
MIN_FREE_GB="${KG_OFFSITE_MIN_FREE_GB:-20}"
SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=15 -o ControlMaster=no -o ControlPath=none"
# stdin 을 쓰지 않는 호출은 반드시 -n. ssh 는 기본적으로 stdin 을 삼키므로
# 본 스크립트를 파이프/heredoc 안에서 돌리면 호출자의 입력을 먹어치운다 (2026-07-27 실측).
SSH_N="$SSH_OPTS -n"

ts=$(date -u +%FT%TZ)
MONTH=$(date -u +%Y%m)

mkdir -p "$SRC"
echo "[$ts] starting offsite push → ${DGX_HOST}:${RDIR}/daily/" >> "$LOG"

# ── 0. 소스 존재 ────────────────────────────────────────────────────────────
if [ ! -d "$SRC" ] || ! ls "$SRC"/kg-*.cypher 2>/dev/null > /dev/null; then
  echo "[$ts] FAIL: no kg-*.cypher backups in $SRC" >> "$LOG"
  exit 1
fi

NEWEST=$(ls -t "$SRC"/kg-*.cypher 2>/dev/null | head -1)
BN=$(basename "$NEWEST")

# ── (a) 신선도 가드 ─────────────────────────────────────────────────────────
# 일일 백업(02:00)이 죽었는데 어제/그제 파일을 매일 다시 밀어올리며
# "오프사이트 있음"을 가장하는 것을 막는다. kg-mirror-monthly.sh 40d → 여기선 2d.
if [ -z "$(find "$NEWEST" -mtime -${MAX_AGE_DAYS} 2>/dev/null)" ]; then
  echo "[$ts] FAIL: newest backup $BN is STALE (>${MAX_AGE_DAYS}d) — 일일 백업 점검 필요. 전송 중단." >> "$LOG"
  exit 1
fi

SIZE=$(stat -f %z "$NEWEST" 2>/dev/null || stat -c %s "$NEWEST" 2>/dev/null)
if [ "${SIZE:-0}" -lt 100000000 ]; then
  echo "[$ts] FAIL: $BN suspiciously small (${SIZE}B < 100MB) — 덤프 손상 의심. 전송 중단." >> "$LOG"
  exit 1
fi

SHA=$(shasum -a 256 "$NEWEST" | cut -d' ' -f1)

# ── (f) meta.json sha 대조 = 반쯤 쓰인 덤프 차단 ────────────────────────────
# kg-backup-daily.sh 는 .cypher 를 다 쓴 뒤에야 meta.json 을 만든다.
# 따라서 meta 가 없거나 sha 가 어긋나면 = 아직 쓰는 중이거나 손상. 밀어올리면 안 된다.
META="${NEWEST}.meta.json"
if [ ! -f "$META" ]; then
  echo "[$ts] FAIL: $BN 의 meta.json 없음 — 백업 미완료/손상 의심. 전송 중단." >> "$LOG"
  exit 1
fi
META_SHA=$(python3 -c "import json;print(json.load(open('$META'))['sha256'])" 2>/dev/null)
if [ -z "${META_SHA:-}" ] || [ "$META_SHA" != "$SHA" ]; then
  echo "[$ts] FAIL: sha 불일치 meta=${META_SHA:0:12} file=${SHA:0:12} — 쓰는 중이거나 손상. 전송 중단." >> "$LOG"
  exit 1
fi

# ── 1. 원격 도달성 ──────────────────────────────────────────────────────────
if ! ssh $SSH_N "$DGX_HOST" true 2>>"$LOG"; then
  echo "[$ts] FAIL: ${DGX_HOST} 도달 불가 — 오프사이트 사본 갱신 안 됨 (조용히 넘어가지 않는다)" >> "$LOG"
  exit 1
fi

ssh $SSH_N "$DGX_HOST" "mkdir -p ${RDIR}/daily ${RDIR}/monthly" 2>>"$LOG" || {
  echo "[$ts] FAIL: 원격 디렉토리 생성 실패" >> "$LOG"; exit 1; }

# ── (e) 원격 여유 공간 ──────────────────────────────────────────────────────
FREE_KB=$(ssh $SSH_N "$DGX_HOST" "df -Pk \$HOME | awk 'NR==2{print \$4}'" 2>>"$LOG")
FREE_GB=$(( ${FREE_KB:-0} / 1024 / 1024 ))
if [ "$FREE_GB" -lt "$MIN_FREE_GB" ]; then
  echo "[$ts] FAIL: ${DGX_HOST} 여유 공간 ${FREE_GB}GB < ${MIN_FREE_GB}GB — 전송 중단" >> "$LOG"
  exit 1
fi

# ── (c) 동일 내용 재푸시 가드 ───────────────────────────────────────────────
LAST=$(ssh $SSH_N "$DGX_HOST" "cat ${RDIR}/LAST_PUSH 2>/dev/null" 2>/dev/null)
LAST_SHA=$(echo "$LAST" | awk '{print $1}')
LAST_BN=$(echo "$LAST" | awk '{print $2}')
if [ -n "${LAST_SHA:-}" ] && [ "$LAST_SHA" = "$SHA" ]; then
  if [ "$LAST_BN" = "$BN" ]; then
    echo "[$ts] SKIP: $BN 이미 전송됨 (sha=${SHA:0:12}) — 멱등 no-op" >> "$LOG"
    exit 0
  fi
  echo "[$ts] FAIL: 새 파일 $BN 이 직전 푸시 $LAST_BN 과 내용 동일 (sha=${SHA:0:12}) — KG 정체 또는 백업 파이프라인 고장 의심. 전송 중단." >> "$LOG"
  exit 1
fi

# ── 2. 스트리밍 압축 전송 (로컬 임시파일 없음) ──────────────────────────────
RPART="${RDIR}/daily/${BN}.gz.part"
RFINAL="${RDIR}/daily/${BN}.gz"
if ! gzip -6 -c "$NEWEST" | ssh $SSH_OPTS "$DGX_HOST" "cat > ${RPART}" 2>>"$LOG"; then
  echo "[$ts] FAIL: 스트리밍 전송 실패 — .part 정리" >> "$LOG"
  ssh $SSH_N "$DGX_HOST" "rm -f ${RPART}" 2>/dev/null
  exit 1
fi

# ── (d) 원격 end-to-end 무결성 검증 ─────────────────────────────────────────
RSHA=$(ssh $SSH_N "$DGX_HOST" "gunzip -c ${RPART} 2>/dev/null | sha256sum | cut -d' ' -f1" 2>>"$LOG")
if [ "$RSHA" != "$SHA" ]; then
  echo "[$ts] FAIL: 무결성 불일치 local=${SHA:0:12} remote=${RSHA:0:12} — .part 폐기" >> "$LOG"
  ssh $SSH_N "$DGX_HOST" "rm -f ${RPART}" 2>/dev/null
  exit 1
fi

ssh $SSH_N "$DGX_HOST" "mv ${RPART} ${RFINAL} && printf '%s  %s\n' '$SHA' '$BN' > ${RFINAL}.sha256" 2>>"$LOG" || {
  echo "[$ts] FAIL: 원격 커밋(mv) 실패" >> "$LOG"; exit 1; }

# meta.json 동반 (작아서 그냥 스트림)
# ※ scp 를 쓰면 안 된다: scp 원격 경로는 쉘 전개가 되지 않아 $HOME 이 리터럴로 남는다
#   (2026-07-27 실측: scp: dest open "$HOME/kg-offsite/...": No such file or directory)
if [ -f "${NEWEST}.meta.json" ]; then
  ssh $SSH_OPTS "$DGX_HOST" "cat > ${RDIR}/daily/${BN}.gz.meta.json" < "${NEWEST}.meta.json" 2>>"$LOG"
fi

GZSIZE=$(ssh $SSH_N "$DGX_HOST" "stat -c %s ${RFINAL}" 2>/dev/null)

# LAST_PUSH 갱신 — (c) 가드의 근거
ssh $SSH_N "$DGX_HOST" "printf '%s  %s\n' '$SHA' '$BN' > ${RDIR}/LAST_PUSH" 2>>"$LOG"

# ── 3. 월간 승격 (재전송 없이 원격 cp) ──────────────────────────────────────
ssh $SSH_OPTS "$DGX_HOST" "bash -s" <<REMOTE_MONTHLY 2>>"$LOG"
set -u
cd "${RDIR}" 2>/dev/null || exit 1
if ! ls monthly/${MONTH}-kg-*.cypher.gz >/dev/null 2>&1; then
  cp "daily/${BN}.gz" "monthly/${MONTH}-${BN}.gz"
  cp "daily/${BN}.gz.sha256" "monthly/${MONTH}-${BN}.gz.sha256" 2>/dev/null
  cp "daily/${BN}.gz.meta.json" "monthly/${MONTH}-${BN}.gz.meta.json" 2>/dev/null
fi
REMOTE_MONTHLY

# ── 4. 보존 정리 (daily N, monthly M) ───────────────────────────────────────
# 파일명이 kg-YYYYMMDD-HHMMSS 라 사전순 == 시간순이다.
ssh $SSH_OPTS "$DGX_HOST" "bash -s" <<REMOTE_RETENTION 2>>"$LOG"
set -u
cd "${RDIR}/daily" 2>/dev/null || exit 1
ls -1 kg-*.cypher.gz 2>/dev/null | sort | head -n -${DAILY_KEEP} | while read -r old; do
  rm -f "\$old" "\$old.sha256" "\$old.meta.json"
done
cd "${RDIR}/monthly" 2>/dev/null || exit 1
ls -1 *-kg-*.cypher.gz 2>/dev/null | sort | head -n -${MONTHLY_KEEP} | while read -r old; do
  rm -f "\$old" "\$old.sha256" "\$old.meta.json"
done
REMOTE_RETENTION

# ── (b) 0건이면 실패 ────────────────────────────────────────────────────────
DCOUNT=$(ssh $SSH_N "$DGX_HOST" "ls -1 ${RDIR}/daily/kg-*.cypher.gz 2>/dev/null | wc -l" 2>/dev/null | tr -d ' ')
MCOUNT=$(ssh $SSH_N "$DGX_HOST" "ls -1 ${RDIR}/monthly/*-kg-*.cypher.gz 2>/dev/null | wc -l" 2>/dev/null | tr -d ' ')
if [ "${DCOUNT:-0}" -eq 0 ]; then
  echo "[$ts] FAIL: 전송 후 원격 daily 파일 0건 — 성공 가장 금지" >> "$LOG"
  exit 1
fi

echo "[$ts] OK: $BN → ${DGX_HOST}:${RDIR}/daily/${BN}.gz (${SIZE}B → ${GZSIZE:-?}B, sha=${SHA:0:12}, verified) daily=${DCOUNT} monthly=${MCOUNT} free=${FREE_GB}GB" >> "$LOG"
exit 0
