#!/usr/bin/env python3
"""
Taliban --lens mathematical sampler PoC.

Reads MIC_v1.MathematicalSamplingPolicy slot from KG, returns N lens names
from 13-domain × 113-lens taxonomy (stratified random per domain).

Modes:
  --full          : all 113 lens
  --sample 0.30   : sample rate (default per policy slot)
  --sample N      : explicit N lens count
  --minimum       : 12 lens floor (CI smoke gate, 1 per domain ceil-floor)
  --policy        : print active MathematicalSamplingPolicy

Stratification: 13 mathematical-validation domains
  LL/CT/TT/AL (9 each), OL/TG/AN (8), CD (9), NT (8), CC/FV/GD/IC (9)

KG: lensset-mathematical (113 lens registry),
    MIC_v1.MathematicalSamplingPolicy slot,
    mathematical-sampling-default-2026-05-06,
    fw-mathematical-113-coverage-2026-05-06

Limitations:
  - PoC: outputs lens names only (does not dispatch)
  - Lens definitions live in 113_LENS_TAXONOMY.md, KG node count not equal to taxonomy yet
  - Cost guard auto-degrade not implemented (manual mode flags)
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys

NEO4J_URL = os.environ.get("NEO4J_URL", "http://neo4j.metahumotonic.com/db/neo4j/tx/commit")
NEO4J_AUTH = os.environ.get("NEO4J_AUTH", "neo4j:neo4jpassword")

# 113-lens taxonomy stratification (from THEORY/TALIBAN/113_LENS_TAXONOMY.md §2).
DOMAINS = {
    "LL": 9, "CT": 9, "TT": 9, "AL": 9,
    "OL": 8, "TG": 8, "AN": 8,
    "CD": 9, "NT": 8,
    "CC": 9, "FV": 9, "GD": 9, "IC": 9,
}
TOTAL = sum(DOMAINS.values())  # = 113


def cypher(stmt, params=None):
    body = {"statement": stmt}
    if params:
        body["parameters"] = params
    payload = json.dumps({"statements": [body]})
    out = subprocess.check_output(
        [
            "curl", "-s", "-m", "5",
            "-u", NEO4J_AUTH,
            "-H", "Content-Type: application/json",
            "-d", payload,
            NEO4J_URL,
        ],
        timeout=10,
    )
    return json.loads(out.decode())


def fetch_policy():
    res = cypher(
        "MATCH (s:MethodologySlot {name:'MathematicalSamplingPolicy'}) "
        "MATCH (p:MathematicalSamplingPolicy {name:s.currentConcrete}) "
        "RETURN p.default_sample_rate AS rate, p.default_sample_count AS count, "
        "p.minimum_sample_count AS minimum, p.lens_total AS total"
    )
    rows = res.get("results", [{}])[0].get("data", [])
    if not rows:
        return {"rate": 0.30, "count": 34, "minimum": 12, "total": 113}
    r = rows[0]["row"]
    return {"rate": r[0], "count": r[1], "minimum": r[2], "total": r[3]}


def stratified_sample(target_count):
    """Distribute target_count proportionally across 13 domains."""
    rng = random.Random(42)  # deterministic for PoC
    rate = target_count / TOTAL
    samples = {}
    for domain, domain_total in DOMAINS.items():
        domain_target = max(1, round(domain_total * rate))
        # lens names are domain-prefixed: LL_001, LL_002, ...
        domain_lens = [f"{domain}_{i:03d}" for i in range(1, domain_total + 1)]
        rng.shuffle(domain_lens)
        samples[domain] = domain_lens[:min(domain_target, domain_total)]
    return samples


def cmd_policy():
    p = fetch_policy()
    print(f"MathematicalSamplingPolicy:")
    print(f"  default_sample_rate:  {p['rate']}")
    print(f"  default_sample_count: {p['count']}")
    print(f"  minimum_sample_count: {p['minimum']}")
    print(f"  lens_total:           {p['total']}")
    return 0


def cmd_full():
    samples = stratified_sample(TOTAL)
    total = sum(len(v) for v in samples.values())
    for domain, lenses in samples.items():
        print(f"  {domain}: {len(lenses)}/{DOMAINS[domain]} — {','.join(lenses)}")
    print(f"total: {total}")
    return 0


def cmd_sample(n):
    samples = stratified_sample(n)
    total = sum(len(v) for v in samples.values())
    for domain, lenses in samples.items():
        print(f"  {domain}: {len(lenses)}/{DOMAINS[domain]} — {','.join(lenses)}")
    print(f"total: {total} (target {n})")
    return 0


def cmd_minimum():
    p = fetch_policy()
    return cmd_sample(p["minimum"])


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    if args[0] == "--policy":
        return cmd_policy()
    if args[0] == "--full":
        return cmd_full()
    if args[0] == "--minimum":
        return cmd_minimum()
    if args[0] == "--sample" and len(args) >= 2:
        v = args[1]
        if "." in v:
            rate = float(v)
            return cmd_sample(round(rate * TOTAL))
        return cmd_sample(int(v))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
