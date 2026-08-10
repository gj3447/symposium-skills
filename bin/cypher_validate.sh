#!/bin/bash
# cypher_validate.sh v3 — validate ```cypher blocks in skill docs via EXPLAIN
# v2: single cypher-shell JVM batch (~5s; v1 was JVM-per-query ~6min).
# v3 (2026-08-10, dev-01 이관):
#   - 경로를 스크립트 위치 기준으로 해석 (v2는 /Users 하드코딩 → dev-01에서
#     0블록 매치 + "ALL PASS" false-green이었다)
#   - total=0 을 실패로 처리 (경로 해석이 깨지면 통과가 아니라 죽어야 한다)
#   - cypher-shell 부재 시 Neo4j HTTP tx API(curl)로 fallback.
#     HTTP 경로는 첫 오류에서 트랜잭션이 멈추므로 오류 개수는 1로만 보고되지만
#     게이트 의미(전부 통과해야 PASS)는 동일하다.

set -u
SKILLS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NEO4J_URI="${NEO4J_URI:-bolt://192.168.0.25:7687}"
NEO4J_HTTP="${NEO4J_HTTP:-http://192.168.0.25:7474}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASS="${NEO4J_PASS:-neo4jpassword}"

if [ $# -eq 0 ]; then
  paths=(
    "$SKILLS_ROOT/_common"
    "$SKILLS_ROOT/apt-sa"
    "$SKILLS_ROOT/apt-sp"
    "$SKILLS_ROOT/apt-st"
    "$SKILLS_ROOT/apt-scw"
    "$SKILLS_ROOT/apt-meta-review"
  )
else
  paths=("$@")
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Build single .cypher file with all queries as EXPLAIN, separated by ;
{
  echo "// cypher_validate.sh v3 batch — $(date -u +%FT%TZ)"
  echo ""
  find "${paths[@]}" -name "*.md" -not -path "*/_legacy/*" 2>/dev/null | while read -r f; do
    awk -v src="$f" '
      /^```cypher$/ { in_block=1; n++; print "// === " src " block " n " ==="; print "EXPLAIN"; next }
      /^```$/ && in_block { in_block=0; print ";"; print ""; next }
      in_block { print }
    ' "$f"
  done
} > "$TMP/all.cypher"

total=$(grep -c "^EXPLAIN$" "$TMP/all.cypher")

if [ "$total" -eq 0 ]; then
  echo "=== Cypher Template Validation Result (v3) ==="
  echo "FAIL: 0 cypher blocks found under: ${paths[*]}"
  echo "(경로 해석 실패 또는 문서 소실 — v2의 false-green 재발 방지로 실패 처리)"
  exit 1
fi

if command -v cypher-shell >/dev/null 2>&1; then
  out=$(cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASS" --format plain \
         --fail-at-end -f "$TMP/all.cypher" 2>&1)
  fails=$(echo "$out" | grep -cE "SyntaxError|ProcedureNotFoundException|UndefinedAlias|TypeError" || true)
else
  # HTTP fallback: EXPLAIN 문장들을 하나의 tx로 POST. 첫 오류에서 중단되므로
  # 오류가 있으면 fails=1 로만 보고된다 (게이트 판정에는 충분).
  python3 - "$TMP/all.cypher" > "$TMP/payload.json" <<'PY'
import json, sys
raw = open(sys.argv[1]).read()
stmts, cur = [], []
for line in raw.splitlines():
    if line.startswith("//") or not line.strip():
        continue
    if line.strip() == ";":
        if cur:
            stmts.append("\n".join(cur))
            cur = []
        continue
    cur.append(line)
if cur:
    stmts.append("\n".join(cur))
print(json.dumps({"statements": [{"statement": s} for s in stmts]}))
PY
  out=$(curl -s -m 60 -u "$NEO4J_USER:$NEO4J_PASS" -H 'Content-Type: application/json' \
         -X POST "$NEO4J_HTTP/db/neo4j/tx/commit" --data-binary "@$TMP/payload.json")
  fails=$(printf '%s' "$out" | python3 -c 'import json,sys
try:
    d = json.load(sys.stdin)
    print(len(d.get("errors", [])))
except Exception:
    print(1)')
fi

passed=$((total - fails))

echo ""
echo "=== Cypher Template Validation Result (v3) ==="
echo "Total cypher blocks: $total"
echo "PASS: $passed"
echo "FAIL: $fails"
if [ "$fails" -gt 0 ]; then
  echo ""
  echo "FAILURE samples:"
  echo "$out" | grep -B1 -A1 -E "SyntaxError|ProcedureNotFoundException|\"code\"" | head -20
  exit 1
fi
echo "ALL PASS"
exit 0
