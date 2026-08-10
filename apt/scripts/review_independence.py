#!/usr/bin/env python3
"""Build an auditable proposer-reviewer independence receipt.

Different agent names are not independent evidence.  A clean PASS requires
different resolved weight families, prompts, temperature bands, and sessions.
Same-family review is explicitly correlated and can reach only CONDITIONAL when
both a deterministic oracle and a human decision are bound to the artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


POLICY_VERSION = "apt-review-independence-v1"
ORACLE_KINDS = frozenset({"exact_query", "source_snapshot", "test_result"})


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return value == value.lower()


def temperature_band(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "unspecified"
    if value < 0 or value > 2:
        return "invalid"
    if value < 0.30:
        return "low"
    if value <= 0.70:
        return "medium"
    return "high"


def _normalize_identity(role: str, raw: Any) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not isinstance(raw, dict):
        return {}, [f"{role} identity must be an object"]
    required_text = ("provider", "model_revision", "weight_family", "session_id")
    normalized: dict[str, Any] = {}
    for field in required_text:
        value = raw.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{role}.{field} is required")
            normalized[field] = ""
        else:
            normalized[field] = value.strip().lower()
    if not _is_sha256(raw.get("prompt_sha256")):
        errors.append(f"{role}.prompt_sha256 must be a SHA-256 digest")
        normalized["prompt_sha256"] = ""
    else:
        normalized["prompt_sha256"] = raw["prompt_sha256"]
    normalized["temperature"] = raw.get("temperature")
    normalized["temperature_band"] = temperature_band(raw.get("temperature"))
    if normalized["temperature_band"] in {"unspecified", "invalid"}:
        errors.append(f"{role}.temperature must be a number in [0, 2]")
    normalized["family_key"] = (
        f"{normalized.get('provider', '')}:{normalized.get('weight_family', '')}"
    )
    normalized["identity_sha256"] = canonical_sha256(normalized)
    return normalized, errors


def _valid_oracles(raw: Any, artifact_sha256: str) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    accepted: list[dict[str, Any]] = []
    for oracle in raw:
        if not isinstance(oracle, dict):
            continue
        if (
            oracle.get("kind") in ORACLE_KINDS
            and oracle.get("verdict") == "PASS"
            and oracle.get("artifact_sha256") == artifact_sha256
            and _is_sha256(oracle.get("receipt_sha256"))
        ):
            accepted.append(dict(oracle))
    return accepted


def _human_bound(raw: Any, artifact_sha256: str) -> bool:
    return (
        isinstance(raw, dict)
        and raw.get("decision") == "APPROVE"
        and raw.get("artifact_sha256") == artifact_sha256
        and isinstance(raw.get("actor"), str)
        and bool(raw["actor"].strip())
        and _is_sha256(raw.get("decision_sha256"))
    )


def evaluate(request: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    artifact_sha256 = request.get("artifact_sha256")
    if not _is_sha256(artifact_sha256):
        errors.append("artifact_sha256 must be a SHA-256 digest")
        artifact_sha256 = ""
    producer, producer_errors = _normalize_identity("producer", request.get("producer"))
    reviewer, reviewer_errors = _normalize_identity("reviewer", request.get("reviewer"))
    errors.extend(producer_errors)
    errors.extend(reviewer_errors)

    dimensions = {
        "different_weight_family": bool(producer)
        and producer.get("family_key") != reviewer.get("family_key"),
        "different_model_revision": bool(producer)
        and producer.get("model_revision") != reviewer.get("model_revision"),
        "different_prompt": bool(producer)
        and producer.get("prompt_sha256") != reviewer.get("prompt_sha256"),
        "different_temperature_band": bool(producer)
        and producer.get("temperature_band") != reviewer.get("temperature_band"),
        "different_session": bool(producer)
        and producer.get("session_id") != reviewer.get("session_id"),
    }
    valid_oracles = _valid_oracles(request.get("deterministic_oracles"), artifact_sha256)
    human_bound = _human_bound(request.get("human_approval"), artifact_sha256)

    clean_dimensions = (
        "different_weight_family",
        "different_prompt",
        "different_temperature_band",
        "different_session",
    )
    clean_pass = not errors and all(dimensions[name] for name in clean_dimensions)
    if clean_pass:
        verdict = "PASS"
        confidence_ceiling = "INDEPENDENT_REVIEW"
    elif (
        not errors
        and not dimensions["different_weight_family"]
        and dimensions["different_prompt"]
        and dimensions["different_temperature_band"]
        and dimensions["different_session"]
        and bool(valid_oracles)
        and human_bound
    ):
        verdict = "CONDITIONAL"
        confidence_ceiling = "CORRELATED_SAME_MODEL_WITH_EXTERNAL_CHECK"
    else:
        verdict = "BLOCK"
        confidence_ceiling = "NO_REVIEW_CONFIDENCE"

    remediation: list[str] = []
    if errors:
        remediation.extend(errors)
    for dimension, instruction in (
        ("different_weight_family", "Use a reviewer with a different resolved weight family."),
        ("different_prompt", "Use a separately authored adversarial prompt and record its digest."),
        ("different_temperature_band", "Place proposer and reviewer in different temperature bands."),
        ("different_session", "Run the reviewer in a separate context/session."),
    ):
        if not dimensions[dimension]:
            remediation.append(instruction)
    if not dimensions["different_weight_family"]:
        if not valid_oracles:
            remediation.append(
                "Bind at least one passing exact-query/source-snapshot/test-result oracle to the artifact."
            )
        if not human_bound:
            remediation.append(
                "Bind a human APPROVE decision to the same artifact digest; same-family review cannot self-elevate."
            )

    receipt = {
        "policy_version": POLICY_VERSION,
        "artifact_sha256": artifact_sha256,
        "producer": producer,
        "reviewer": reviewer,
        "dimensions": dimensions,
        "deterministic_oracle_count": len(valid_oracles),
        "human_approval_bound": human_bound,
        "correlation_status": (
            "CROSS_FAMILY"
            if dimensions["different_weight_family"]
            else "CORRELATED_SAME_MODEL"
        ),
        "verdict": verdict,
        "confidence_ceiling": confidence_ceiling,
        "remediation": list(dict.fromkeys(remediation)),
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    args = parser.parse_args(argv)
    request = json.loads(args.request.read_text())
    if not isinstance(request, dict):
        parser.error("request JSON must be an object")
    receipt = evaluate(request)
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["verdict"] in {"PASS", "CONDITIONAL"} else 2


if __name__ == "__main__":
    sys.exit(main())
