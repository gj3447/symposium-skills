#!/usr/bin/env python3
"""Validate either an engine fit decision or a full engine-spec/v1 contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ENGINE_REQUIRED = {
    "schema_version",
    "name",
    "purpose",
    "decision",
    "boundary",
    "model",
    "state_model",
    "protocol",
    "invariants",
    "ports",
    "runtime",
    "durability",
    "failure_model",
    "observability",
    "security",
    "verification",
    "implementation_slices",
    "falsifiers",
}
DECISION_REQUIRED = {
    "schema_version",
    "name",
    "verdict",
    "purpose",
    "current_consumers",
    "planned_consumers",
    "rationale",
    "boundary",
    "contract",
    "invariants",
    "failure_model",
    "verification",
    "promotion_gates",
    "falsifiers",
}


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_text_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(is_text(item) for item in value)
    )


def require_text_list(container: dict[str, Any], key: str, prefix: str, errors: list[str], *, allow_empty: bool = False) -> None:
    if not is_text_list(container.get(key), allow_empty=allow_empty):
        suffix = "a list of non-empty strings" if allow_empty else "a non-empty list of non-empty strings"
        errors.append(f"{prefix}{key} must be {suffix}")


def validate_boundary(boundary: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(boundary, dict):
        errors.append(f"{prefix}boundary must be an object")
        return
    for key in ("owns", "mechanism", "state_authority"):
        if not is_text(boundary.get(key)):
            errors.append(f"{prefix}boundary.{key} must be a non-empty string")
    for key in ("policy_outside", "non_goals"):
        require_text_list(boundary, key, f"{prefix}boundary.", errors)


def validate_module_decision(spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for key in sorted(DECISION_REQUIRED - spec.keys()):
        errors.append(f"missing required field: {key}")
    if spec.get("schema_version") != "engine-decision/v1":
        errors.append("schema_version must be 'engine-decision/v1'")
    if spec.get("verdict") not in {"module", "defer"}:
        errors.append("verdict must be 'module' or 'defer' for engine-decision/v1")
    for key in ("name", "purpose", "contract"):
        if not is_text(spec.get(key)):
            errors.append(f"{key} must be a non-empty string")
    require_text_list(spec, "current_consumers", "", errors)
    require_text_list(spec, "planned_consumers", "", errors, allow_empty=True)
    current = {item for item in spec.get("current_consumers", []) if isinstance(item, str)} if isinstance(spec.get("current_consumers"), list) else set()
    planned = {item for item in spec.get("planned_consumers", []) if isinstance(item, str)} if isinstance(spec.get("planned_consumers"), list) else set()
    overlap = current & planned
    if overlap:
        errors.append(f"current_consumers and planned_consumers overlap: {sorted(overlap)}")
    for key in ("rationale", "invariants", "failure_model", "verification", "promotion_gates", "falsifiers"):
        require_text_list(spec, key, "", errors)
    validate_boundary(spec.get("boundary"), "", errors)
    forbidden = {"protocol", "durability", "implementation_slices"} & spec.keys()
    if forbidden:
        errors.append(f"module/defer decision must not contain premature engine artifacts: {sorted(forbidden)}")
    return errors, warnings


def validate_engine(spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for key in sorted(ENGINE_REQUIRED - spec.keys()):
        errors.append(f"missing required field: {key}")
    if spec.get("schema_version") != "engine-spec/v1":
        errors.append("schema_version must be 'engine-spec/v1'")
    for key in ("name", "purpose"):
        if not is_text(spec.get(key)):
            errors.append(f"{key} must be a non-empty string")

    decision = spec.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be an object")
    else:
        if decision.get("verdict") != "engine":
            errors.append("decision.verdict must be 'engine'")
        require_text_list(decision, "current_consumers", "decision.", errors)
        require_text_list(decision, "planned_consumers", "decision.", errors, allow_empty=True)
        current = {item for item in decision.get("current_consumers", []) if isinstance(item, str)} if isinstance(decision.get("current_consumers"), list) else set()
        planned = {item for item in decision.get("planned_consumers", []) if isinstance(item, str)} if isinstance(decision.get("planned_consumers"), list) else set()
        overlap = current & planned
        if overlap:
            errors.append(f"decision current/planned consumers overlap: {sorted(overlap)}")
        require_text_list(decision, "fit_evidence", "decision.", errors)
        require_text_list(decision, "alternatives_considered", "decision.", errors)
        if len(decision.get("current_consumers", [])) == 1:
            warnings.append("only one current consumer is named; fit_evidence must prove an operational engine boundary")

    validate_boundary(spec.get("boundary"), "", errors)

    model = spec.get("model")
    if not isinstance(model, dict):
        errors.append("model must be an object")
    else:
        require_text_list(model, "resources", "model.", errors)
        require_text_list(model, "work_units", "model.", errors)
    if not isinstance(spec.get("state_model"), (str, dict)) or not spec.get("state_model"):
        errors.append("state_model must be a non-empty string or object")

    protocol = spec.get("protocol")
    if not isinstance(protocol, dict):
        errors.append("protocol must be an object")
    else:
        for key in ("commands", "events", "effects"):
            require_text_list(protocol, key, "protocol.", errors)
        if not is_text(protocol.get("versioning")):
            errors.append("protocol.versioning must be a non-empty string")
        effect_names = {
            re.sub(r"[^a-z0-9]", "", item.lower())
            for item in protocol.get("effects", [])
            if isinstance(item, str)
        }
        commit_prefixes = ("persistevent", "appendevent", "writeevent", "commitevent")
        if any(name.startswith(commit_prefixes) for name in effect_names):
            errors.append("event append/persistence is the commit boundary, not a post-commit effect")

    for key in ("invariants", "ports", "failure_model", "security", "verification", "implementation_slices", "falsifiers"):
        require_text_list(spec, key, "", errors)

    runtime = spec.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime must be an object")
    else:
        for key in ("ordering", "concurrency", "backpressure", "cancellation", "timeouts"):
            if not is_text(runtime.get(key)):
                errors.append(f"runtime.{key} must be a non-empty string")

    durability = spec.get("durability")
    if not isinstance(durability, dict):
        errors.append("durability must be an object; use explicit 'none' statements when out of scope")
    else:
        for key in ("persistence", "atomic_commit", "recovery", "effect_idempotency", "migration"):
            if not is_text(durability.get(key)):
                errors.append(f"durability.{key} must be a non-empty string")

    observability = spec.get("observability")
    if not isinstance(observability, dict):
        errors.append("observability must be an object")
    else:
        require_text_list(observability, "traces", "observability.", errors)
        require_text_list(observability, "metrics", "observability.", errors)
        if not is_text(observability.get("redaction")):
            errors.append("observability.redaction must be a non-empty string")
    return errors, warnings


def validate(spec: Any) -> tuple[list[str], list[str]]:
    if not isinstance(spec, dict):
        return ["root must be a JSON object"], []
    if spec.get("schema_version") == "engine-decision/v1":
        return validate_module_decision(spec)
    return validate_engine(spec)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} ENGINE_DESIGN.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR {path}: {error}", file=sys.stderr)
        return 2
    errors, warnings = validate(spec)
    for item in warnings:
        print(f"WARN  {item}")
    for item in errors:
        print(f"ERROR {item}")
    if errors:
        print(f"FAIL  {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK    {path}: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
