#!/bin/bash
# kg-restore-drill.sh — 월1 restore DRILL (PROM16 kg-governance T2, C6 구현)
# "백업만 있고 drill 없음 = 검증 안 된 DR" 해소. 실증: 2026-07-14까지 backup이
# cypher-shell PATH 문제로 조용히 실패 중이었음 — drill이 있었으면 즉시 잡혔음.
#
# Tier A (자동, 본 스크립트): freshness + sha256 무결성 + live 카운트 대조 + 구문 sanity
# Tier B (OPEN, 인프라 필요): scratch Neo4j 인스턴스에 실제 restore 후 카운트 재현
#   → dgx k8s에 scratch neo4j pod 확보 시 확장. KG: task-...-T2-restore-drill
#
# Cron: 57 3 1 * *  (매월 1일 03:57)
# KG: lesson-kg-management-methodology-consolidation-2026-07-15
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
set -u
BACKUP_DIR="${KG_BACKUP_DIR:-/Users/lagyeongjun/CD/SYMPOSIUM/_archive/kg-backups}"
NEO4J_URI="${NEO4J_URI:-bolt://192.168.0.23:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASS="${NEO4J_PASS:-neo4jpassword}"
DRILL_LOG="$BACKUP_DIR/drill.log"
ts=$(date -u +%FT%TZ)
PASS=true; REASONS=()

fail() { PASS=false; REASONS+=("$1"); }

LATEST=$(ls -t "$BACKUP_DIR"/kg-*.cypher 2>/dev/null | head -1)
[ -z "${LATEST:-}" ] && { echo "[$ts] DRILL FAIL: no backup file" >> "$DRILL_LOG"; exit 2; }
META="${LATEST}.meta.json"

# 1. freshness ≤ 26h
AGE_H=$(( ( $(date +%s) - $(stat -f %m "$LATEST") ) / 3600 ))
[ "$AGE_H" -gt 26 ] && fail "stale backup: ${AGE_H}h old (>26h)"

# 2. sha256 integrity vs meta
if [ -f "$META" ]; then
  WANT=$(python3 -c "import json;print(json.load(open('$META'))['sha256'])")
  GOT=$(shasum -a 256 "$LATEST" | cut -d' ' -f1)
  [ "$WANT" != "$GOT" ] && fail "sha256 mismatch: meta=$WANT file=$GOT"
else
  fail "meta.json missing"
fi

# 3. size sanity (>100MB for this KG)
SIZE=$(stat -f %z "$LATEST")
[ "$SIZE" -lt 100000000 ] && fail "suspiciously small: ${SIZE}B"

# 4. meta counts vs LIVE KG (±10% tolerance — 백업이 진짜 그래프를 담았나)
read -r LIVE_N LIVE_R <<< "$(python3 - <<'PY'
from neo4j import GraphDatabase
import os
d=GraphDatabase.driver(os.environ.get('NEO4J_URI','bolt://192.168.0.23:7687'),
    auth=(os.environ.get('NEO4J_USER','neo4j'),os.environ.get('NEO4J_PASS','neo4jpassword')),connection_timeout=15)
with d.session(database='neo4j') as s:
    r=s.run('CALL apoc.meta.stats() YIELD nodeCount, relCount RETURN nodeCount, relCount').single()
    print(r['nodeCount'], r['relCount'])
d.close()
PY
)"
META_N=$(python3 -c "import json;print(int(json.load(open('$META'))['node_count']))" 2>/dev/null || echo 0)
if [ "$META_N" -gt 0 ] && [ "$LIVE_N" -gt 0 ]; then
  DRIFT=$(python3 -c "print(abs($LIVE_N-$META_N)/$LIVE_N)")
  python3 -c "exit(0 if $DRIFT<=0.10 else 1)" || fail "backup/live node drift ${DRIFT}>10% (meta=$META_N live=$LIVE_N)"
fi

# 5. cypher 구문 sanity — 시작부에 실제 statement 존재
head -c 100000 "$LATEST" | grep -qE 'CREATE|UNWIND|MERGE|BEGIN' || fail "no cypher statements in head"

VERDICT=$([ "$PASS" = true ] && echo PASS || echo FAIL)
echo "[$ts] DRILL $VERDICT: $(basename "$LATEST") age=${AGE_H}h size=${SIZE}B meta_nodes=$META_N live_nodes=$LIVE_N ${REASONS[*]:-}" >> "$DRILL_LOG"

# 6. KG 결정화
python3 - "$VERDICT" "$(basename "$LATEST")" "$AGE_H" "$SIZE" "${REASONS[*]:-}" <<'PY'
import sys, os
from neo4j import GraphDatabase
verdict, fname, age, size, reasons = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv)>5 else ''
d=GraphDatabase.driver(os.environ.get('NEO4J_URI','bolt://192.168.0.23:7687'),
    auth=(os.environ.get('NEO4J_USER','neo4j'),os.environ.get('NEO4J_PASS','neo4jpassword')),connection_timeout=15)
with d.session(database='neo4j') as s:
    s.run("""MERGE (r:RestoreDrillResult {name:'restore-drill-'+toString(date())})
      SET r.verdict=$v, r.backupFile=$f, r.ageHours=toInteger($a), r.sizeBytes=toInteger($sz),
          r.failReasons=$rs, r.tier='A-integrity', r.checkedAt=datetime(),
          r.cycle_id='prom16-kg-governance-2026-07-15'""",
      v=verdict, f=fname, a=age, sz=size, rs=reasons)
d.close()
print(f"drill result crystallized: {verdict}")
PY

[ "$PASS" = true ] && exit 0 || exit 1
