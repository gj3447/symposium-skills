#!/bin/bash
# cypher_validate.sh — Extract cypher blocks + EXPLAIN syntax check
# A3 finding: bash regex extract + cypher-shell EXPLAIN (no-execute)

set -u
NEO4J_URI="${NEO4J_URI:-bolt://100.64.0.3:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASS="${NEO4J_PASS:-neo4jpassword}"

if [ $# -eq 0 ]; then
  paths=(
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/_common
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/apt-sa
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/apt-sp
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/apt-st
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/apt-scw
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/apt-meta-review
  )
else
  paths=("$@")
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Extract all cypher blocks into single file separated by ===EOB===
find "${paths[@]}" -name "*.md" -not -path "*/_legacy/*" 2>/dev/null | while read -r f; do
  awk '
    /^```cypher$/ { in_block=1; next }
    /^```$/ && in_block { in_block=0; print "===EOB==="; next }
    in_block { print }
  ' "$f"
done > "$TMP/all.txt"

# Split into individual query files using awk
awk -v outdir="$TMP" '
  BEGIN { n=0; out=sprintf("%s/q_%04d.cyp", outdir, n) }
  /^===EOB===$/ { close(out); n++; out=sprintf("%s/q_%04d.cyp", outdir, n); next }
  { print > out }
' "$TMP/all.txt"

total=0; passed=0; failed=0
declare -a FAILS=()

for q in "$TMP"/q_*.cyp; do
  [ -s "$q" ] || continue
  # Skip if only comments/whitespace
  if ! grep -qE "^[^/[:space:]]" "$q"; then continue; fi
  total=$((total+1))

  # Determine if query uses Cypher params ($name) — wrap with WITH for EXPLAIN validation
  if grep -qE '\$[a-zA-Z_]+' "$q"; then
    # Use WITH NULL prefix to declare params via passing
    prefix=""
    params_decl=""
    for p in $(grep -oE '\$[a-zA-Z_]+' "$q" | sort -u | sed 's/^\$//'); do
      params_decl+="$p:null, "
    done
    params_decl=${params_decl%, }
    prefix="WITH {$params_decl} AS params "
    # Replace $X with params.X — too complex. Simpler: pass -P
    full=$(cat "$q")
    out=$(printf "EXPLAIN %s" "$full" | cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASS" --format plain 2>&1 | head -3)
  else
    out=$(printf "EXPLAIN %s" "$(cat "$q")" | cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASS" --format plain 2>&1 | head -3)
  fi

  # SyntaxError or other Cypher Statement errors = FAIL
  # ParameterNotFoundException is OK (we didn't pass params for EXPLAIN)
  if echo "$out" | grep -qE "SyntaxError|ProcedureNotFoundException|UndefinedAlias|TypeError"; then
    failed=$((failed+1))
    snip=$(head -1 "$q" | tr -d '\n' | cut -c1-80)
    err=$(echo "$out" | head -2 | tr '\n' ' ' | cut -c1-200)
    FAILS+=("[#$total] $snip ... → $err")
  else
    passed=$((passed+1))
  fi
done

echo ""
echo "=== Cypher Template Validation Result ==="
echo "Total cypher blocks: $total"
echo "PASS: $passed"
echo "FAIL: $failed"
if [ "$failed" -gt 0 ]; then
  echo ""
  echo "FAILURES:"
  printf '%s\n' "${FAILS[@]}"
  exit 1
fi
echo "ALL PASS"
