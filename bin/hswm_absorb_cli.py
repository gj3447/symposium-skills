#!/usr/bin/env python3
"""
HSWM absorb CLI — multi-agent handoff + contract validator (stdlib only).

Subcommands:
  handoff           flat | flat_L4 | structure (structure = diagnostic only)
  validate-contract check claim JSON / prose against ABSORB_CONTRACT anti-patterns
  contract-print    emit locked contract summary JSON

Exit codes:
  0 OK
  2 contract violation / bad input
  0 UNAVAILABLE never (stdlib pure)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VERSION = "hswm-absorb-cli/1.0.0"
CONTRACT_ID = "ABSORB_CONTRACT_v1"
DEPLOY_SLOGAN = "Admit flat. Expand gated (optional). Govern late. TRAVERSAL_OFF. Fuse weight may be 0."

# Banned patterns for validate-contract (case-insensitive substring)
ANTI_ABSORB_PATTERNS = [
    ("structure_primary_deploy", r"structure[-_ ]primary", "structure-primary ranking as deploy"),
    ("structure_primary_handoff", r"layered[-_ ]primary.*handoff|primary ranker.*structure", "structure as handoff primary"),
    ("traversal_on_default", r"traversal[_\s]*mu\s*[=>:]?\s*[1-9]|traversal\s*on\s*default|query[-_ ]time\s+traversal\s+on", "query-time traversal ON default"),
    ("blind_rrf_only", r"blind\s*rrf\s*only|fusion\s*=\s*blind\s*rrf", "blind RRF as sole fusion"),
    ("cognitive_uplift_claim", r"cognitive\s+uplift\s+over\s+direct|beats?\s+direct[-_ ]?llm\s+rerank", "cognitive uplift product claim"),
    ("deep_stack_perf", r"deep\s+gnn\s+stack.*recall|propagation\s+depth.*performance\s+default", "deep GNN stack as performance default"),
    ("progressive_from_docs", r"progressive\s+from\s+markdown|progressive\s+without\s+receipt", "progressive without receipt"),
    ("default_on_weave", r"default[-_ ]on\s+semantic\s+weave|hswm\s+mode\s*=\s*on\s+default", "default-on semantic weave"),
]

import re

_COMPILED = [(k, re.compile(p, re.I), msg) for k, p, msg in ANTI_ABSORB_PATTERNS]


def _load_json(path: str | None) -> Any:
    if path:
        return json.loads(Path(path).read_text())
    return json.load(sys.stdin)


def cmd_handoff(args: argparse.Namespace) -> int:
    """
    Input JSON:
    {
      "candidates": [{"doc_id": str, "score": float, "supersede": 0..1, "version": str?}],
      "B1": 10, "B2": 20, "B3": 10,   # optional budgets
      "mode": "flat" | "flat_L4" | "structure"  # or --mode
    }
    structure mode is allowed for diagnostic A/B only; emit warning flag.
    """
    data = _load_json(args.input)
    mode = args.mode or data.get("mode") or "flat_L4"
    if mode not in {"flat", "flat_L4", "structure"}:
        print(json.dumps({"status": "ERROR", "reason": f"bad mode {mode}"}))
        return 2
    cands = list(data.get("candidates") or [])
    if not cands:
        print(json.dumps({"status": "ERROR", "reason": "empty candidates"}))
        return 2
    B1 = int(data.get("B1", args.B1))
    B2 = int(data.get("B2", args.B2))
    B3 = int(data.get("B3", args.B3))

    # normalize
    rows = []
    for c in cands:
        rows.append({
            "doc_id": str(c["doc_id"]),
            "score": float(c.get("score", 0.0)),
            "supersede": float(c.get("supersede", 0.0)),
            "version": str(c.get("version") or "v0"),
        })
    # sort by score desc
    ranked = sorted(rows, key=lambda r: -r["score"])
    a1 = ranked[:B1]
    # expand: next B2 by score (flat path); structure mode pretends structure re-rank = same scores for stdlib
    a2_pool = ranked[:B2]
    cand: list[dict] = []
    for r in a1 + a2_pool:
        if mode == "structure" and r["supersede"] >= 0.95:
            continue  # early filter (M0 loser path — diagnostic)
        if all(x["doc_id"] != r["doc_id"] for x in cand):
            cand.append(r)
    cand = cand[: B1 + B2]

    if mode == "flat":
        final = sorted(cand, key=lambda r: -r["score"])[:B3]
    elif mode == "flat_L4":
        live = [r for r in cand if r["supersede"] < 0.95]
        pool = live if live else cand
        final = sorted(pool, key=lambda r: -r["score"])[:B3]
    else:  # structure diagnostic
        final = sorted(cand, key=lambda r: -r["score"])[:B3]

    handoff = []
    for rank, r in enumerate(final, start=1):
        handoff.append({
            "doc_id": r["doc_id"],
            "rank": rank,
            "score": r["score"],
            "version": r["version"],
            "supersede_flag": r["supersede"] >= 0.95,
            "supersede_dose": r["supersede"],
            "path": mode,
        })

    out = {
        "status": "OK",
        "contract_id": CONTRACT_ID,
        "mode": mode,
        "deploy_default": mode == "flat_L4",
        "diagnostic_only": mode == "structure",
        "warning": (
            "structure mode is REFUTED as deploy default (MuSiQue/2Wiki); use only as control arm"
            if mode == "structure"
            else None
        ),
        "budget": {"B1": B1, "B2": B2, "B3": B3},
        "handoff": handoff,
        "slogan": DEPLOY_SLOGAN,
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0


def cmd_validate_contract(args: argparse.Namespace) -> int:
    """
    Input: {"text": "..."} or {"claims": ["...", ...]} or raw string file
    """
    raw = Path(args.input).read_text() if args.input else sys.stdin.read()
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            texts = []
            if "text" in data:
                texts.append(str(data["text"]))
            if "claims" in data:
                texts.extend(str(c) for c in data["claims"])
            blob = "\n".join(texts) if texts else raw
        else:
            blob = raw
    except json.JSONDecodeError:
        blob = raw

    violations = []
    for key, cre, msg in _COMPILED:
        if cre.search(blob):
            violations.append({"id": key, "message": msg})

    # mode force checks
    if args.require_mode:
        if args.require_mode == "flat_L4" and re.search(r"mode\s*[:=]\s*structure", blob, re.I):
            violations.append({"id": "mode_structure_as_required", "message": "required flat_L4 but text sets structure"})

    ok = len(violations) == 0
    print(json.dumps({
        "status": "OK" if ok else "VIOLATION",
        "contract_id": CONTRACT_ID,
        "ok": ok,
        "violations": violations,
        "slogan": DEPLOY_SLOGAN,
    }, ensure_ascii=False))
    return 0 if ok else 2


def cmd_contract_print(_args: argparse.Namespace) -> int:
    print(json.dumps({
        "status": "OK",
        "contract_id": CONTRACT_ID,
        "version": VERSION,
        "slogan": DEPLOY_SLOGAN,
        "ship_now": [
            "flat_primary_admit",
            "L4_late_supersede_gate",
            "L1_static_residual_optin",
            "TRAVERSAL_OFF",
            "direct_preregister_measure_record",
            "S3_dual_channel_write_identity",
        ],
        "never": [
            "structure_primary_ranking",
            "query_time_traversal_ON_default",
            "cognitive_uplift_product",
            "deep_gnn_stack_performance_default",
            "default_on_semantic_weave",
            "progressive_from_markdown_alone",
        ],
        "evidence": {
            "2wiki_L4_minus_flat_joint": 0.1,
            "2wiki_stale_cut": 0.35,
            "musique_multiseed_min_joint": 0.03,
            "S3_collapse": 0.4458,
        },
        "data_paths_gm": {
            "2wiki": "/Volumes/GM/bench/2wiki_dev.jsonl",
            "musique": "/Volumes/GM/bench/musique_dev.jsonl",
            "hf_cache": "/Volumes/GM/hswm_lab/hf_cache",
        },
    }, ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="hswm_absorb_cli.py", description=VERSION)
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("handoff", help="multi-agent handoff emit (flat|flat_L4|structure)")
    p.add_argument("--input", help="JSON file (stdin if omitted)")
    p.add_argument("--mode", choices=["flat", "flat_L4", "structure"], default=None)
    p.add_argument("--B1", type=int, default=10)
    p.add_argument("--B2", type=int, default=20)
    p.add_argument("--B3", type=int, default=10)
    p.set_defaults(fn=cmd_handoff)

    p = sub.add_parser("validate-contract", help="fail closed on anti-absorb prose")
    p.add_argument("--input", help="claims JSON or text file")
    p.add_argument("--require-mode", default=None)
    p.set_defaults(fn=cmd_validate_contract)

    p = sub.add_parser("contract-print", help="print locked absorb contract JSON")
    p.set_defaults(fn=cmd_contract_print)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
