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

# rsync 배제 — 재생성 가능/외부 소유 (coverage 정신)
EXCLUDES=(
  --exclude=.git/ --exclude=.venv/ --exclude=venv/ --exclude=node_modules/
  --exclude=__pycache__/ --exclude=dist/ --exclude=build/
  --exclude=.pytest_cache/ --exclude=.ruff_cache/ --exclude=.uv-cache/
  --exclude=.mypy_cache/ --exclude=.next/ --exclude=target/
  --exclude=.DS_Store --exclude='*.pyc'
)

# 검증 manifest용 동일 배제 (find prune) — 로컬 배열 / 리모트 문자열
PRUNE_DIRS=(.git .venv venv node_modules __pycache__ dist build .pytest_cache .ruff_cache .uv-cache .mypy_cache .next target)
LFIND_PRUNE=(-type d \()
for i in "${!PRUNE_DIRS[@]}"; do
  [ "$i" -gt 0 ] && LFIND_PRUNE+=(-o)
  LFIND_PRUNE+=(-name "${PRUNE_DIRS[$i]}")
done
LFIND_PRUNE+=(\) -prune)

RPRUNE=$(printf -- '-name %s -o ' "${PRUNE_DIRS[@]}"); RPRUNE=${RPRUNE%-o }
RFIND="find . \\( -type d \\( $RPRUNE \\) -prune \\) -o -type f ! -name .DS_Store ! -name '*.pyc' -exec sha256sum {} + | LC_ALL=C sort -k2"

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
  "$CDROOT/HSWM:COMPAT_SOURCES/CDROOT/HSWM"
  "$CDROOT/spacegirl_tool:COMPAT_SOURCES/CDROOT/spacegirl_tool"
)

say() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

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
(cd "$SYM" && find . -maxdepth 1 -type f -print0 | tar --null -cf - --files-from -) | ssh $DEST "tar xf - -C $NEW/ROOT_FILES/"
say "root files ok"

# --- 2. 매핑별 양쪽 SHA-256 manifest 검증 (1차 실패 시 settle 후 1회 재동기화·재검) ---
# hot append-only 로그(세션 receipts 등)가 rsync↔검증 사이에 바뀌는 경합 흡수 (2026-07-25,
# GIT/ 매핑 연속 MISMATCH 사례). 재검 불일치는 진짜 불일치 — 차이 5건을 표시하고 FAIL.
FAIL=0
for m in "${SYNCED[@]}"; do
  src=${m%%:*}; rel=${m#*:}
  L=$( (cd "$src" && LC_ALL=C find . "${LFIND_PRUNE[@]}" -o -type f ! -name .DS_Store ! -name '*.pyc' -exec shasum -a 256 {} + | LC_ALL=C sort -k2) )
  R=$(ssh $DEST "cd '$NEW/$rel' && $RFIND")
  if [ "$L" != "$R" ]; then
    say "verify FAIL(1차): $rel — 45s settle 후 재동기화·재검"
    sleep 45
    LINKDEST=""
    if ssh $DEST "test -d $CUR/$rel" 2>/dev/null; then LINKDEST="--link-dest=$CUR/$rel"; fi
    # shellcheck disable=SC2086
    rsync -az $LINKDEST "${EXCLUDES[@]}" "$src/" "$DEST:$NEW/$rel/"
    L=$( (cd "$src" && LC_ALL=C find . "${LFIND_PRUNE[@]}" -o -type f ! -name .DS_Store ! -name '*.pyc' -exec shasum -a 256 {} + | LC_ALL=C sort -k2) )
    R=$(ssh $DEST "cd '$NEW/$rel' && $RFIND")
  fi
  if [ "$L" = "$R" ]; then
    n=$(printf '%s\n' "$L" | grep -c . || true)
    say "verify ok: $rel ($n files)"
  else
    say "verify FAIL: $rel (재검 후에도 불일치)"
    printf '%s\n' "$L" | LC_ALL=C sort > /tmp/lakatotree-sync-L.txt
    printf '%s\n' "$R" | LC_ALL=C sort > /tmp/lakatotree-sync-R.txt
    say "차이 상위 5건: $(comm -3 /tmp/lakatotree-sync-L.txt /tmp/lakatotree-sync-R.txt | awk '{print $2}' | head -5 | tr '\n' ' ')"
    FAIL=1
  fi
done

if [ "$FAIL" -ne 0 ]; then
  say "MANIFEST MISMATCH — 포인터 전진 안 함. 스냅샷 보존: $NEW"
  exit 1
fi

# --- 2.5. Proxmox-only 콘텐츠 carry-forward (no-clobber union) ---
# 이전 current의 top-level 중 새 스냅샷에 없는 것(Proxmox 생성 연구 등)은 하드링크로 이어받고,
# RUNTIME_EVIDENCE 는 내용 병합. 매핑된 루트(PI/THEORY 등) 남남은 미러링 유지 — Mac 삭제분 부활 방지.
if OLD=$(ssh $DEST "readlink -f $CUR" 2>/dev/null) && [ -n "$OLD" ]; then
  ssh $DEST "for e in \$(ls '$OLD'); do [ -e '$NEW/'\$e ] || cp -al '$OLD/'\$e '$NEW/'\$e; done; cp -aln '$OLD/RUNTIME_EVIDENCE/.' '$NEW/RUNTIME_EVIDENCE/' 2>/dev/null || true"
  say "carry-forward from: $OLD"
fi

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
# 루트 파일 심링크
ssh $DEST "cd $NEW/ROOT_FILES && for f in *; do [ -f \"\$f\" ] && ln -sfn $CUR/ROOT_FILES/\"\$f\" $CFARM/\"\$f\"; done" 2>/dev/null || true
say "symlink farm updated"

# --- 5. 영수증 + 스크립트산 스냅샷 keep-last 정리 ---
read -r -d '' RECEIPT <<EOF || true
{"stamp":"$STAMP","snapshot":"$NEW","mappings":${#SYNCED[@]},"verified":true,"keep":$KEEP,"actor":"lakatotree-sync-now.sh"}
EOF
ssh $DEST "cat > $NEW/RUNTIME_EVIDENCE/SYNC_RECEIPT.json" <<< "$RECEIPT"
TARGET=$(ssh $DEST "readlink -f $CUR")
ssh $DEST "cd $RUNTIME && ls -1d research-2*[0-9]-[0-9]* 2>/dev/null | sort | head -n -$KEEP" | while read -r old; do
  full=$(ssh $DEST "readlink -f $RUNTIME/$old")
  [ "$full" = "$TARGET" ] && continue
  say "prune: $old"
  ssh $DEST "rm -rf $RUNTIME/$old"
done
say "DONE"
