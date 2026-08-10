#!/bin/bash
# kg-offsite-dgx.sh — TIER 3-B 오프사이트 백업 레인: 별개 물리 호스트(DGX)로 월간 사본
# Cron: 45 2 1 * * /Users/lagyeongjun/CD/SYMPOSIUM/bin/kg-offsite-dgx.sh
#   (02:00 kg-backup-daily.sh 완료 후, 03:00 kg-mirror-monthly.sh 전. 실측 소요 ~25s)
# Dest: dgx:~/kg-offsite/<YYYYMM>/   (kg-YYYYMMDD-HHMMSS.cypher.gz + .sha256 + .meta.json)
# Retention: 12 months
#
# 왜 필요한가 (2026-07-27 실측):
#   기존 TIER 3 = kg-mirror-monthly.sh → mc localminio(kg-offsite).
#   그런데 localminio 는 macmini localhost:9000 이고 그 socat 은
#     TCP-LISTEN:9000 → TCP:192.168.0.25:9000  (= data-01)
#   KG 원본 Neo4j 도 같은 VM:
#     TCP-LISTEN:7687 → TCP:192.168.0.25:7687  (= data-01)
#   즉 "오프사이트 미러"가 원본과 같은 VM 안에 있다. data-01 사망 = 원본+미러 동시 소멸.
#   호스트 밖 사본은 macmini 로컬 7일치가 전부였다.
#
#   DGX(192.168.0.23, edgexpert-e229)는 systemd-detect-virt=none 인 별개 물리 머신이고
#   data-01 은 MAC bc:24:11:* (Proxmox VM OUI) 인 가상머신이다 → 장애 도메인 분리 확인.
#
#   ⚠️ 정직한 한계: 같은 LAN(192.168.0.0/24), 같은 건물이다. 호스트 단위 장애는 커버하지만
#      화재/침수/건물 정전은 커버하지 못한다. 진짜 지리적 오프사이트는 별도 과제로 남는다.
#
# 가드 — kg-mirror-monthly.sh 의 2026-07-15 "조용한 실패" 방지 가드를 계승:
#   (a) 최신 로컬 덤프가 40일 초과로 낡았으면 stale 재업로드 대신 exit 1
#       (2026-05-11 스냅샷이 매달 재업로드되며 2개월간 백업 부재를 은폐했던 사고의 방지책)
#   (b) 전송 후 원격 <YYYYMM>/ 파일이 0건이면 exit 1 (성공 가장 금지)
#   (c) 전송 후 원격에서 sha256 을 재계산해 로컬과 대조. 불일치 시 .part 폐기 후 exit 1
#   (d) meta.json sha 대조 — 반쯤 쓰인/손상된 덤프를 밀어올리지 않는다
#   (e) 원격 여유 공간 < MIN_FREE_GB 이면 전송 전에 exit 1
#
# 설계 메모: macmini 데이터 볼륨 여유가 13Gi 뿐이라 로컬 임시 압축파일을 만들지 않는다.
#   gzip -c → ssh cat 스트리밍이라 로컬 디스크를 전혀 쓰지 않고, 원격에서 gunzip|sha256sum
#   으로 end-to-end 검증한다(압축 해제 가능성까지 함께 검증된다).
#   ※ ssh 는 기본적으로 stdin 을 삼킨다. stdin 이 필요 없는 호출은 전부 -n 을 준다.

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"   # cron PATH 에 brew 없음 (2026-07-15 fix)
set -euo pipefail

SRC="${KG_BACKUP_DIR:-/Users/lagyeongjun/CD/SYMPOSIUM/_archive/kg-backups}"
LOG="${KG_OFFSITE_LOG:-${SRC}/offsite-dgx-monthly.log}"
DGX_HOST="${KG_OFFSITE_HOST:-dgx}"
RDIR="${KG_OFFSITE_REMOTE_DIR:-\$HOME/kg-offsite}"      # 원격 쉘이 전개한다
MAX_AGE_DAYS="${KG_OFFSITE_MAX_AGE_DAYS:-40}"
RETENTION_MONTHS="${KG_OFFSITE_RETENTION_MONTHS:-12}"
MIN_FREE_GB="${KG_OFFSITE_MIN_FREE_GB:-20}"
MIN_DUMP_BYTES="${KG_OFFSITE_MIN_DUMP_BYTES:-100000000}"
GZIP_BIN="${KG_OFFSITE_GZIP_BIN:-gzip}"
SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=15 -o ControlMaster=no -o ControlPath=none"
SSH_N="$SSH_OPTS -n"

ts=$(date -u +%FT%TZ)
MONTH=$(date -u +%Y%m)

mkdir -p "$SRC" 2>/dev/null || true
log() { printf '[%s] %s\n' "$ts" "$1" >> "$LOG"; }

log "starting monthly offsite push → ${DGX_HOST}:${RDIR}/${MONTH}/"

# ── 0. 로컬 덤프 존재 ───────────────────────────────────────────────────────
if [ ! -d "$SRC" ] || ! ls "$SRC"/kg-*.cypher >/dev/null 2>&1; then
  log "FAIL: no kg-*.cypher backups in $SRC"
  exit 1
fi

NEWEST=$(ls -t "$SRC"/kg-*.cypher 2>/dev/null | head -1) || true
if [ -z "${NEWEST:-}" ] || [ ! -f "$NEWEST" ]; then
  log "FAIL: 최신 덤프 탐색 실패 in $SRC"
  exit 1
fi
BN=$(basename "$NEWEST")

# ── (a) 신선도 가드: 40일 초과 stale 이면 재업로드 금지 ─────────────────────
if [ -z "$(find "$NEWEST" -mtime -"${MAX_AGE_DAYS}" 2>/dev/null)" ]; then
  log "FAIL: newest backup $BN is STALE (>${MAX_AGE_DAYS}d) — 일일 백업 점검 필요. 전송 중단."
  exit 1
fi

SIZE=$(stat -f %z "$NEWEST" 2>/dev/null || stat -c %s "$NEWEST" 2>/dev/null) || true
if [ "${SIZE:-0}" -lt "$MIN_DUMP_BYTES" ]; then
  log "FAIL: $BN 이 비정상적으로 작음 (${SIZE:-0}B < ${MIN_DUMP_BYTES}B) — 덤프 손상 의심. 전송 중단."
  exit 1
fi

SHA=$(shasum -a 256 "$NEWEST" | cut -d' ' -f1)

# ── (d) meta.json sha 대조 = 반쯤 쓰인 덤프 차단 ────────────────────────────
# kg-backup-daily.sh 는 .cypher 를 다 쓴 뒤에야 meta.json 을 만든다.
# meta 가 없거나 sha 가 어긋나면 = 아직 쓰는 중이거나 손상 → 밀어올리면 안 된다.
META="${NEWEST}.meta.json"
if [ ! -f "$META" ]; then
  log "FAIL: $BN 의 meta.json 없음 — 백업 미완료/손상 의심. 전송 중단."
  exit 1
fi
META_SHA=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['sha256'])" "$META" 2>/dev/null) || true
if [ -z "${META_SHA:-}" ] || [ "$META_SHA" != "$SHA" ]; then
  log "FAIL: sha 불일치 meta=${META_SHA:-none} file=${SHA:0:12} — 쓰는 중이거나 손상. 전송 중단."
  exit 1
fi

# ── 1. 원격 도달성 / 목적지 준비 ────────────────────────────────────────────
if ! ssh $SSH_N "$DGX_HOST" true 2>>"$LOG"; then
  log "FAIL: ${DGX_HOST} 도달 불가 — 오프사이트 사본 갱신 안 됨 (조용히 넘어가지 않는다)"
  exit 1
fi

RDEST="${RDIR}/${MONTH}"
if ! ssh $SSH_N "$DGX_HOST" "mkdir -p ${RDEST}" 2>>"$LOG"; then
  log "FAIL: 원격 디렉토리 생성 실패 (${DGX_HOST}:${RDEST})"
  exit 1
fi

# ── (e) 원격 여유 공간 ──────────────────────────────────────────────────────
FREE_KB=$(ssh $SSH_N "$DGX_HOST" "df -Pk ${RDEST} | awk 'NR==2{print \$4}'" 2>>"$LOG") || true
FREE_GB=$(( ${FREE_KB:-0} / 1024 / 1024 ))
if [ "$FREE_GB" -lt "$MIN_FREE_GB" ]; then
  log "FAIL: ${DGX_HOST} 여유 공간 ${FREE_GB}GB < ${MIN_FREE_GB}GB — 전송 중단"
  exit 1
fi

RPART="${RDEST}/${BN}.gz.part"
RFINAL="${RDEST}/${BN}.gz"

# ── 2. 이미 같은 내용이 올라가 있으면 재전송 생략 (멱등) ────────────────────
# 생략하더라도 아래 (b) 0건 가드와 보존정리는 그대로 통과시킨다.
EXIST_SHA=$(ssh $SSH_N "$DGX_HOST" "test -f ${RFINAL} && gunzip -c ${RFINAL} 2>/dev/null | sha256sum | cut -d' ' -f1" 2>/dev/null) || true
if [ "${EXIST_SHA:-}" = "$SHA" ]; then
  log "SKIP: ${BN}.gz 이미 ${MONTH}/ 에 존재하고 sha 일치 (${SHA:0:12}) — 재전송 생략"
else
  # ── 3. 스트리밍 압축 전송 (로컬 임시파일 없음) ────────────────────────────
  if ! "$GZIP_BIN" -6 -c "$NEWEST" | ssh $SSH_OPTS "$DGX_HOST" "cat > ${RPART}" 2>>"$LOG"; then
    log "FAIL: 스트리밍 전송 실패 — .part 정리"
    ssh $SSH_N "$DGX_HOST" "rm -f ${RPART}" 2>/dev/null || true
    exit 1
  fi

  # ── (c) 전송 후 원격 sha256 재계산 → 로컬과 대조 ──────────────────────────
  RSHA=$(ssh $SSH_N "$DGX_HOST" "gunzip -c ${RPART} 2>/dev/null | sha256sum | cut -d' ' -f1" 2>>"$LOG") || true
  if [ "${RSHA:-}" != "$SHA" ]; then
    log "FAIL: 무결성 불일치 local=${SHA:0:12} remote=${RSHA:-none} — .part 폐기, 전송 실패로 처리"
    ssh $SSH_N "$DGX_HOST" "rm -f ${RPART}" 2>/dev/null || true
    exit 1
  fi

  # 검증 통과분만 원자적으로 최종 이름으로 승격
  if ! ssh $SSH_N "$DGX_HOST" "mv ${RPART} ${RFINAL} && printf '%s  %s\n' '$SHA' '${BN}' > ${RFINAL}.sha256" 2>>"$LOG"; then
    log "FAIL: 원격 커밋(mv) 실패"
    exit 1
  fi
fi

# meta.json 동반 전송
# ※ scp 를 쓰면 안 된다: scp 의 원격 목적지는 쉘 전개가 되지 않아 $HOME 이 리터럴로 남는다.
ssh $SSH_OPTS "$DGX_HOST" "cat > ${RDEST}/${BN}.gz.meta.json" < "$META" 2>>"$LOG" || true

GZSIZE=$(ssh $SSH_N "$DGX_HOST" "stat -c %s ${RFINAL} 2>/dev/null" 2>/dev/null) || true

# ── (b) 전송 후 0건이면 실패 ────────────────────────────────────────────────
COUNT=$(ssh $SSH_N "$DGX_HOST" "ls -1 ${RDEST}/ 2>/dev/null | wc -l" 2>/dev/null | tr -d ' ') || true
if [ "${COUNT:-0}" -eq 0 ]; then
  log "FAIL: 전송 후 ${DGX_HOST}:${RDEST}/ 파일 0건 — 성공 가장 금지"
  exit 1
fi

# ── 4. 보존 정리: RETENTION_MONTHS 개월 이전 <YYYYMM> 디렉토리 제거 ─────────
# ⚠️ 6자리 숫자 디렉토리만 건드린다. 같은 부모의 daily/ monthly/ LAST_PUSH 는 다른
#    레인(kg-offsite-dgx-daily.sh)의 자산이므로 절대 지우지 않는다.
CUTOFF=$(date -u -v -"${RETENTION_MONTHS}"m +%Y%m 2>/dev/null || date -u --date="${RETENTION_MONTHS} months ago" +%Y%m 2>/dev/null) || true
if [ -n "${CUTOFF:-}" ]; then
  ssh $SSH_OPTS "$DGX_HOST" "bash -s" >>"$LOG" 2>&1 <<REMOTE_RETENTION || log "WARN: 보존정리 원격 실행 실패 (전송은 성공)"
set -u
cd "${RDIR}" || exit 1
for d in */ ; do
  n="\${d%/}"
  case "\$n" in
    [0-9][0-9][0-9][0-9][0-9][0-9]) ;;
    *) continue ;;
  esac
  if [ "\$n" -lt "${CUTOFF}" ]; then
    rm -rf -- "\$n" && echo "retention: removed \$n (< ${CUTOFF})"
  fi
done
REMOTE_RETENTION
  MONTHS_KEPT=$(ssh $SSH_N "$DGX_HOST" "ls -1d ${RDIR}/[0-9][0-9][0-9][0-9][0-9][0-9] 2>/dev/null | wc -l" 2>/dev/null | tr -d ' ') || true
  log "retention: kept ${MONTHS_KEPT:-?} month dirs (>= ${CUTOFF})"
fi

log "OK: $BN → ${DGX_HOST}:${RDEST}/${BN}.gz (${SIZE}B → ${GZSIZE:-?}B, sha=${SHA:0:12}, verified) files=${COUNT} free=${FREE_GB}GB"
exit 0
