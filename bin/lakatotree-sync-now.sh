#!/bin/bash
# lakatotree-sync-now.sh — Mac 지식 루트 → Proxmox lakatotree-01 canonical snapshot 동기화
#
# 패턴 (2026-07-24 research 마이그레이션과 동일):
#   1. 날짜 스냅샷 research-YYYYMMDD-HHMMSS 생성 (--link-dest로 불변 파일은 하드링크)
#   2. 매핑별 양쪽 SHA-256 manifest 일치 검증
#   3. 전부 일치할 때만 research-current 포인터 전진 (불일치 시 포인터 불변, 스냅샷 보존)
#   4. /Users/lagyeongjun/CD/... 호환 심링크 농장 갱신 (서버가 Mac 절대경로를 realpath로 해소)
#   5. 스크립트산 스냅샷 keep-last 정리 (수제 스냅샷은 건드리지 않음)
#
# 수동 실행: bin/lakatotree-sync-now.sh
# nightly: ~/Library/LaunchAgents/com.symposium.lakatotree-sync.plist
set -euo pipefail

CDROOT=/Users/lagyeongjun/CD
SYM=$CDROOT/SYMPOSIUM
DEST=root@192.168.0.26
RUNTIME=/opt/lakatotree/.runtime
STAMP=$(date +%Y%m%d-%H%M%S)
NEW=$RUNTIME/research-$STAMP
CUR=$RUNTIME/research-current
KEEP=6
CFARM=/Users/lagyeongjun/CD/SYMPOSIUM   # 컨테이너 측 심링크 농장
LEGACY_HSWM=$CDROOT/HSWM
LEGACY_HSWM_ARCHIVE_REL=ARCHIVED_SUPERSEDED/CDROOT/HSWM
LEGACY_HSWM_B21_REL=prom_search_hswm/prom_b21_learned_router.py
LEGACY_HSWM_B21_SHA=76af6dd849416e9410bc01f635047da0a1418902a1541c7ea0e516fcf7d31f88
HSWM_SSOT_REL=COMPAT_SOURCES/CDROOT/SYMPOSIUM/GIT/HSWM

# rsync 배제 — 재생성 가능/외부 소유 (coverage 정신)
# + 시크릿 패턴 (2026-07-25 .env/settings.json 유출 사고 교훈): .env 계열·키 파일·.qwen·dt-guard-env 민감 2종
EXCLUDES=(
  --exclude=.git/ --exclude=.venv/ --exclude=venv/ --exclude=node_modules/
  --exclude=__pycache__/ --exclude=dist/ --exclude=build/
  --exclude=.pytest_cache/ --exclude=.ruff_cache/ --exclude=.uv-cache/
  --exclude=.mypy_cache/ --exclude=.next/ --exclude=target/ --exclude=.f2_cache/
  --exclude=.DS_Store --exclude='*.pyc'
  --exclude=.env --exclude='.env.*' --exclude='*.pem' --exclude='*.key'
  --exclude='id_rsa*' --exclude='id_ed25519*' --exclude=.qwen/
  --exclude=/symposium-dt-guard-env-20260716/settings.json
  --exclude=/symposium-dt-guard-env-20260716/.qwen/
)

# 검증 manifest용 동일 배제 (find prune) — 로컬 배열 / 리모트 문자열
PRUNE_DIRS=(.git .venv venv node_modules __pycache__ dist build .pytest_cache .ruff_cache .uv-cache .mypy_cache .next target .qwen .f2_cache)
LFIND_PRUNE=(-type d \()
for i in "${!PRUNE_DIRS[@]}"; do
  [ "$i" -gt 0 ] && LFIND_PRUNE+=(-o)
  LFIND_PRUNE+=(-name "${PRUNE_DIRS[$i]}")
done
LFIND_PRUNE+=(\) -prune)

# 시크릿/잡 파일 배제 — 양쪽 find 동일 적용 (rsync EXCLUDES 와 1:1 대응)
LFILE_EXCL=(! -name .DS_Store ! -name '*.pyc' ! -name .env ! -name '.env.*' ! -name '*.pem' ! -name '*.key' ! -name 'id_rsa*' ! -name 'id_ed25519*' ! -path './symposium-dt-guard-env-20260716/settings.json' ! -path './symposium-dt-guard-env-20260716/.qwen/*')
RFILE_EXCL="! -name .DS_Store ! -name '*.pyc' ! -name .env ! -name '.env.*' ! -name '*.pem' ! -name '*.key' ! -name 'id_rsa*' ! -name 'id_ed25519*' ! -path './symposium-dt-guard-env-20260716/settings.json' ! -path './symposium-dt-guard-env-20260716/.qwen/*'"

RPRUNE=$(printf -- '-name %s -o ' "${PRUNE_DIRS[@]}"); RPRUNE=${RPRUNE%-o }
RFIND="find . \\( -type d \\( $RPRUNE \\) -prune \\) -o -type f $RFILE_EXCL -exec sha256sum {} + | LC_ALL=C sort -k2"

# src:dest 매핑 (dest = 스냅샷 루트 상대). src 없으면 skip.
MAPPINGS=(
  "$SYM/PI:PI"
  "$SYM/HSWM:HSWM"
  "$SYM/THEORY:THEORY"
  "$SYM/FINDINGS:FINDINGS"
  "$SYM/METAHUMOTONIC:METAHUMOTONIC"
  "$SYM/MATH:MATH"
  "$SYM/PAPERS:PAPERS"
  "$SYM/BIZ_IDEA:BIZ_IDEA"
  "$SYM/GAMES:GAMES"
  "$SYM/GAME_IDEA:GAME_IDEA"
  "$SYM/GROK:GROK"
  "$SYM/FEEDBACK:FEEDBACK"
  "$SYM/docs:docs"
  "$SYM/bin:bin"
  "$SYM/kg:kg"
  "$SYM/methodology-resolver:methodology-resolver"
  "$SYM/REPRODUCTION:REPRODUCTION"
  "$SYM/ONTOLOGY:ONTOLOGY"
  "$SYM/mcp-server-symposium:mcp-server-symposium"
  "$SYM/GIT:COMPAT_SOURCES/CDROOT/SYMPOSIUM/GIT"
  "$SYM/_archive:_archive"
  "$SYM/SKILLS:SKILLS"
  "$CDROOT/spacegirl_tool:COMPAT_SOURCES/CDROOT/spacegirl_tool"
)

say() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

# dogfood 자기보고 — 실행 영수증을 SyncHarness 연구 트리 노드로 (2026-07-25)
START_TS=$(date +%s)
TOTAL_FILES=0
report_run() {  # report_run OK|FAIL <note>
  ssh $DEST "/opt/lakatotree/.venv/bin/python /opt/lakatotree/report_sync_run.py '$1' $TOTAL_FILES $(( $(date +%s) - START_TS )) '$STAMP' '$2'" >/dev/null 2>&1 || true
}

ssh $DEST "mkdir -p $NEW/ROOT_FILES $NEW/RUNTIME_EVIDENCE"
say "snapshot: $NEW"

# --- 1. 매핑별 rsync ---
SYNCED=()
for m in "${MAPPINGS[@]}"; do
  src=${m%%:*}; rel=${m#*:}
  if [ ! -d "$src" ]; then say "SKIP (no src): $src"; continue; fi
  LINKDEST=""
  if ssh $DEST "test -d $CUR/$rel" 2>/dev/null; then LINKDEST="--link-dest=$CUR/$rel"; fi
  ssh $DEST "mkdir -p $(dirname "$NEW/$rel")"
  # shellcheck disable=SC2086
  rsync -az $LINKDEST "${EXCLUDES[@]}" "$src/" "$DEST:$NEW/$rel/"
  SYNCED+=("$m")
  say "rsync ok: $rel"
done

# --- 1b. SYMPOSIUM 루트 파일들 (AGENTS.md 등) ---
# 시크릿/라이브DB/캐시/AppleDouble 제외 — .env·settings.json 유출 사고(2026-07-25) 교훈: denylist 필수.
export COPYFILE_DISABLE=1
(cd "$SYM" && find . -maxdepth 1 -type f \
  ! -name '.env' ! -name '.env.*' ! -name 'settings.json' \
  ! -name '*.db' ! -name '*.db-shm' ! -name '*.db-wal' \
  ! -name '.lycheecache' ! -name '.DS_Store' ! -name '._*' \
  ! -name '*.pem' ! -name '*.key' ! -name 'id_*' \
  -print0 | tar --null -cf - --files-from -) | ssh $DEST "tar xf - -C $NEW/ROOT_FILES/"
say "root files ok"

# --- 2. 매핑별 양쪽 SHA-256 manifest 검증 (불일치 시 settle 에스컬레이션 45s→5m→15m ×3 재동기화·재검) ---
# hot append-only 로그(HSWM 실험 receipts 등)가 rsync↔검증 사이에 바뀌는 경합 흡수.
# 2026-07-25 개선(q-partial-pointer-advance): 3차 재검 실패 매핑은 *마지막 검증 세대*를 carry-forward하고
# SYNC_RECEIPT.stale_mappings에 명시 — 경합 매핑 하나가 24개 전체 포인터 전진을 막지 않는다 (매핑별 원자성).
# 이전 세대가 없는 신규 매핑만 FAIL(전체 중단, 포인터 불변) — fail-closed는 integrity에만 발동.
FAIL=0
verify_mapping() {
  local src=$1 rel=$2 wait_s LINKDEST L R n
  for wait_s in 0 45 300 900; do
    if [ "$wait_s" -gt 0 ]; then
      say "verify FAIL: $rel — ${wait_s}s settle 후 재동기화·재검"
      sleep "$wait_s"
      LINKDEST=""
      if ssh $DEST "test -d $CUR/$rel" 2>/dev/null; then LINKDEST="--link-dest=$CUR/$rel"; fi
      # shellcheck disable=SC2086
      rsync -az $LINKDEST "${EXCLUDES[@]}" "$src/" "$DEST:$NEW/$rel/"
    fi
    L=$( (cd "$src" && LC_ALL=C find . "${LFIND_PRUNE[@]}" -o -type f "${LFILE_EXCL[@]}" -exec shasum -a 256 {} + | LC_ALL=C sort -k2) )
    R=$(ssh $DEST "cd '$NEW/$rel' && $RFIND")
    if [ "$L" = "$R" ]; then
      n=$(printf '%s\n' "$L" | grep -c . || true)
      TOTAL_FILES=$(( TOTAL_FILES + n ))
      say "verify ok: $rel ($n files)"
      return 0
    fi
  done
  say "verify FAIL: $rel (3차 재검 후에도 불일치) — 마지막 검증 세대로 carry-forward (stale 표기)"
  if ssh $DEST "test -d '$CUR/$rel'"; then
    ssh $DEST "rm -rf '$NEW/$rel' && mkdir -p $(dirname "$NEW/$rel") && cp -al '$CUR/$rel' '$NEW/$rel'"
    STALE_MAPPINGS+=("$rel")
    say "carried stale: $rel (from $(ssh $DEST "readlink -f $CUR" | xargs basename))"
    return 0
  fi
  say "verify FAIL: $rel — 이전 세대 없음, carry-forward 불가"
  printf '%s\n' "$L" | LC_ALL=C sort > /tmp/lakatotree-sync-L.txt
  printf '%s\n' "$R" | LC_ALL=C sort > /tmp/lakatotree-sync-R.txt
  say "차이 상위 5건: $(comm -3 /tmp/lakatotree-sync-L.txt /tmp/lakatotree-sync-R.txt | awk '{print $2}' | head -5 | tr '\n' ' ')"
  return 1
}
STALE_MAPPINGS=()
for m in "${SYNCED[@]}"; do
  verify_mapping "${m%%:*}" "${m#*:}" || FAIL=1
done

if [ "$FAIL" -ne 0 ]; then
  say "MANIFEST MISMATCH — 포인터 전진 안 함. 스냅샷 보존: $NEW"
  report_run FAIL "manifest mismatch after escalation retries; pointer unchanged; snapshot kept at $NEW"
  exit 1
fi

# --- 2.5. superseded HSWM replay archive + Proxmox-only carry-forward ---
# /CD/HSWM 을 최신 코드로 재지정하면 과거 LakatoTree receipt의 절대경로+SHA 재현이 깨진다.
# 첫 세대에는 이전 current의 legacy copy를 독립 inode로 동결하고, 다음 세대부터는 그
# read-only archive를 hardlink carry-forward한다. 실행 정본은 오직 GIT/HSWM이다.
OLD=$(ssh $DEST "readlink -f '$CUR'" 2>/dev/null || true)
if [ -z "$OLD" ]; then
  say "ARCHIVE FAIL: 이전 research-current가 없어 legacy HSWM 계보를 보존할 수 없음"
  report_run FAIL "missing previous research-current; legacy HSWM archive not created"
  exit 1
fi

OLD_BASE=${OLD##*/}
if ! ssh $DEST "set -eu
  archive='$NEW/$LEGACY_HSWM_ARCHIVE_REL'
  old_archive='$OLD/$LEGACY_HSWM_ARCHIVE_REL'
  old_compat='$OLD/COMPAT_SOURCES/CDROOT/HSWM'
  mkdir -p '$NEW/ARCHIVED_SUPERSEDED/CDROOT'
  seeded=0
  if [ -d '$OLD/ARCHIVED_SUPERSEDED' ]; then
    cp -al '$OLD/ARCHIVED_SUPERSEDED/.' '$NEW/ARCHIVED_SUPERSEDED/'
  fi
  if [ ! -d \"\$archive\" ] && [ -d \"\$old_compat\" ]; then
    cp -a \"\$old_compat\" \"\$archive\"
    chmod -R a-w \"\$archive\"
    seeded=1
  fi
  if [ ! -d \"\$archive\" ]; then
    exit 44
  fi
  test -d \"\$archive\"
  test -f \"\$archive/$LEGACY_HSWM_B21_REL\"
  actual=\$(sha256sum \"\$archive/$LEGACY_HSWM_B21_REL\" | awk '{print \$1}')
  test \"\$actual\" = '$LEGACY_HSWM_B21_SHA'
  test -z \"\$(find \"\$archive\" \\( -type f -o -type d \\) -perm /222 -print -quit)\"
  if [ \"\$seeded\" -eq 1 ]; then
    printf '%s\n' '{\"schema\":\"hswm-superseded-replay-archive/v1\",\"source_snapshot\":\"$OLD_BASE\",\"legacy_git_head\":\"c01fe5d2989e053a60e278b039bd59fbe3b4d1ad\",\"superseded_by\":\"$HSWM_SSOT_REL\",\"role\":\"FROZEN_REPLAY_ONLY\",\"claim_boundary\":\"HISTORICAL_REFERENCE_INTEGRITY_NOT_ACTIVE_CODE\"}' > '$NEW/ARCHIVED_SUPERSEDED/CDROOT/HSWM_ARCHIVE_PROVENANCE.json'
    chmod a-w '$NEW/ARCHIVED_SUPERSEDED/CDROOT/HSWM_ARCHIVE_PROVENANCE.json'
  fi
  test -f '$NEW/ARCHIVED_SUPERSEDED/CDROOT/HSWM_ARCHIVE_PROVENANCE.json'"; then
  say "ARCHIVE FAIL: legacy HSWM seed/carry-forward/hash/read-only 검증 실패"
  report_run FAIL "legacy HSWM archive preservation failed; pointer unchanged"
  exit 1
fi
say "archive ok: $LEGACY_HSWM_ARCHIVE_REL (B21 SHA exact, read-only)"

# compatibility target가 실제 디렉터리면 절대 지우지 않는다. 포인터 전진 전 fail-closed.
if ! ssh $DEST "[ ! -e '$LEGACY_HSWM' ] || [ -L '$LEGACY_HSWM' ]"; then
  say "ARCHIVE FAIL: $LEGACY_HSWM 이 symlink가 아닌 실제 경로 — 자동 교체 거부"
  report_run FAIL "legacy compatibility target is not a symlink; pointer unchanged"
  exit 1
fi

# 이전 current의 top-level 중 새 스냅샷에 없는 것(Proxmox 생성 연구 등)은 하드링크로 이어받고,
# RUNTIME_EVIDENCE 는 내용 병합. 매핑된 루트(PI/THEORY 등) 남남은 미러링 유지 — Mac 삭제분 부활 방지.
ssh $DEST "for e in \$(ls '$OLD'); do [ -e '$NEW/'\$e ] || cp -al '$OLD/'\$e '$NEW/'\$e; done; cp -aln '$OLD/RUNTIME_EVIDENCE/.' '$NEW/RUNTIME_EVIDENCE/' 2>/dev/null || true"
say "carry-forward from: $OLD"

# --- 3. 결합 매니페스트 + 포인터 전진 ---
ssh $DEST "cd $NEW && find . -path ./RUNTIME_EVIDENCE -prune -o -type f -print0 | xargs -0 -r sha256sum | LC_ALL=C sort -k2 > RUNTIME_EVIDENCE/SHA256SUMS && ln -sfn $NEW $CUR.tmp.$$ && mv -T $CUR.tmp.$$ $CUR"
say "pointer advanced: research-current -> $NEW"

# --- 4. 심링크 농장 갱신 (한 세그먼트 매핑만; GIT은 별도 처리) ---
for m in "${SYNCED[@]}"; do
  rel=${m#*:}
  case "$rel" in */*) continue;; esac
  ssh $DEST "ln -sfn $CUR/$rel $CFARM/$rel"
done
# GIT: 구형은 실재 dir+HSWM 심링크 — full 동기화 이후 심링크로 교체 (HSWM 은 그 안에 포함)
ssh $DEST "if [ -d $CFARM/GIT ] && [ ! -L $CFARM/GIT ]; then rm -rf $CFARM/GIT; fi; ln -sfn $CUR/COMPAT_SOURCES/CDROOT/SYMPOSIUM/GIT $CFARM/GIT"
# 과거 절대경로는 frozen replay archive로만 유지. 위에서 non-symlink를 이미 거부했다.
ssh $DEST "ln -sfn '$CUR/$LEGACY_HSWM_ARCHIVE_REL' '$LEGACY_HSWM'"
# 루트 파일 심링크
ssh $DEST "cd $NEW/ROOT_FILES && for f in *; do [ -f \"\$f\" ] && ln -sfn $CUR/ROOT_FILES/\"\$f\" $CFARM/\"\$f\"; done" 2>/dev/null || true
# dead 링크 청소 (동기화 대상에서 빠진 파일의 잔여 링크 — 배제 정책 변경분 포함)
ssh $DEST "find $CFARM -maxdepth 1 -type l ! -exec test -e {} \; -delete" 2>/dev/null || true
say "symlink farm updated"

# --- 5. 영수증 + 스크립트산 스냅샷 keep-last 정리 ---
if [ "${#STALE_MAPPINGS[@]}" -eq 0 ]; then
  STALE_JSON='[]'
else
  STALE_JSON=$(printf ', "%s"' "${STALE_MAPPINGS[@]}")
  STALE_JSON="[${STALE_JSON#*, }]"
fi
read -r -d '' RECEIPT <<EOF || true
{"stamp":"$STAMP","snapshot":"$NEW","mappings":${#SYNCED[@]},"verified":true,"stale_mappings":$STALE_JSON,"keep":$KEEP,"actor":"lakatotree-sync-now.sh"}
EOF
ssh $DEST "cat > $NEW/RUNTIME_EVIDENCE/SYNC_RECEIPT.json" <<< "$RECEIPT"
TARGET=$(ssh $DEST "readlink -f $CUR")
ssh $DEST "cd $RUNTIME && ls -1d research-2*[0-9]-[0-9]* 2>/dev/null | sort | head -n -$KEEP" | while read -r old; do
  full=$(ssh $DEST "readlink -f $RUNTIME/$old")
  [ "$full" = "$TARGET" ] && continue
  say "prune: $old"
  ssh $DEST "rm -rf $RUNTIME/$old"
done
report_run OK "verified_files=$TOTAL_FILES mappings=${#SYNCED[@]} stale=${#STALE_MAPPINGS[@]}(${STALE_MAPPINGS[*]:-none}) pointer advanced to research-$STAMP"
say "DONE"
