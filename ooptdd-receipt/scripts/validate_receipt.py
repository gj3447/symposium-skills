#!/usr/bin/env python3
"""Validate an OOPTDD evidence envelope; never execute its commands."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{7,64}$")
TIERS = {"local_pass", "emitted", "arrived", "queryable_causal", "external_verdict"}
COMPLETION_TIERS = {"arrived", "queryable_causal", "external_verdict"}
NEGATIVE_TECHNIQUES = {"mutation", "patch", "revert", "drop_backend", "fault_injection"}


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def req_text(value: dict[str, Any], key: str, errors: list[str], prefix: str) -> None:
    if not text(value.get(key)):
        errors.append(f"{prefix}.{key} must be a non-empty string")


def req_sha(value: dict[str, Any], key: str, errors: list[str], prefix: str) -> None:
    candidate = value.get(key)
    if not isinstance(candidate, str) or SHA256.fullmatch(candidate) is None:
        errors.append(f"{prefix}.{key} must be a lowercase 64-hex SHA-256")


def forbidden_keys(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in {"verdict", "manual_verdict", "verdict_source"}:
                errors.append(f"{path}.{key} is forbidden")
            errors.extend(forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(forbidden_keys(child, f"{path}[{index}]"))
    return errors


def verify_file(path_value: Any, sha_value: Any, root: Path, label: str) -> list[str]:
    if not text(path_value) or not isinstance(sha_value, str) or SHA256.fullmatch(sha_value) is None:
        return []
    path = Path(path_value)
    root = root.resolve()
    resolved = (path if path.is_absolute() else root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return [f"{label} escapes artifact root: {resolved}"]
    try:
        actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    except OSError as error:
        return [f"{label} cannot be hash-verified at {resolved}: {error}"]
    return [] if actual == sha_value else [f"{label} SHA-256 mismatch at {resolved}"]


def verify_linked_files(document: Any, root: Path) -> list[str]:
    if not isinstance(document, dict):
        return []
    errors: list[str] = []
    spec = obj(document.get("spec"))
    positive = obj(document.get("positive"))
    negative = obj(document.get("negative_oracle"))
    binding = obj(document.get("source_binding"))
    errors.extend(verify_file(spec.get("path"), spec.get("sha256"), root, "spec.path"))
    errors.extend(verify_file(positive.get("receipt_path"), positive.get("receipt_sha256"), root, "positive.receipt_path"))
    errors.extend(verify_file(negative.get("receipt_path"), negative.get("receipt_sha256"), root, "negative_oracle.receipt_path"))
    errors.extend(verify_file(binding.get("path"), binding.get("sha256"), root, "source_binding.path"))
    return errors


def validate(document: Any, allow_template: bool = False) -> list[str]:
    if not isinstance(document, dict):
        return ["document must be a JSON object"]
    errors = forbidden_keys(document)
    if allow_template:
        if document.get("template_only") is not True:
            errors.append("--template requires template_only=true")
    elif document.get("template_only") is not False:
        errors.append("completion receipt must explicitly set template_only=false")
    if document.get("schema_version") != "symposium-ooptdd-receipt/v1":
        errors.append("schema_version must be 'symposium-ooptdd-receipt/v1'")
    for key in ("receipt_id", "cycle_id", "requirement_group"):
        req_text(document, key, errors, "root")

    spec = obj(document.get("spec"))
    req_text(spec, "path", errors, "spec")
    req_sha(spec, "sha256", errors, "spec")
    if spec.get("locked_before_positive_run") is not True:
        errors.append("spec.locked_before_positive_run must be true")

    producer = obj(document.get("producer"))
    for key in ("command", "cwd", "entrypoint", "source_path", "source_symbol"):
        req_text(producer, key, errors, "producer")
    git_head = producer.get("git_head")
    if not isinstance(git_head, str) or GIT_SHA.fullmatch(git_head) is None:
        errors.append("producer.git_head must be a lowercase 7-64 hex commit id")
    if producer.get("real_code_path") is not True:
        errors.append("producer.real_code_path must be true")
    if producer.get("exit_code") != 0:
        errors.append("producer.exit_code must be 0 for the restored positive run")
    req_text(obj(document.get("correlation")), "cid", errors, "correlation")

    requirements = items(document.get("requirements"))
    roles: set[str] = set()
    ids: list[str] = []
    for index, raw in enumerate(requirements):
        requirement = obj(raw)
        req_text(requirement, "id", errors, f"requirements[{index}]")
        req_text(requirement, "event", errors, f"requirements[{index}]")
        role = requirement.get("role")
        if role not in {"guard_defect", "guard_mechanism"}:
            errors.append(f"requirements[{index}].role must be guard_defect or guard_mechanism")
        else:
            roles.add(role)
        if text(requirement.get("id")):
            ids.append(requirement["id"])
    if len(ids) != len(set(ids)):
        errors.append("requirements IDs must be unique")
    if roles != {"guard_defect", "guard_mechanism"}:
        errors.append("requirements must include both guard_defect and guard_mechanism")

    positive = obj(document.get("positive"))
    if positive.get("observed_verdict") not in {"green", "present"}:
        errors.append("positive.observed_verdict must be green or present")
    req_text(positive, "receipt_path", errors, "positive")
    req_sha(positive, "receipt_sha256", errors, "positive")
    tier = positive.get("evidence_tier")
    if tier not in TIERS:
        errors.append("positive.evidence_tier is not recognized")
    elif tier not in COMPLETION_TIERS:
        errors.append("positive evidence must prove readback; local_pass/emitted are insufficient")
    ratio = positive.get("charge_ratio")
    if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not 0 < ratio <= 1:
        errors.append("positive.charge_ratio must be in (0, 1]")
    if positive.get("forbidden_events_passed") is not True:
        errors.append("positive.forbidden_events_passed must be true")
    loop = obj(positive.get("loop"))
    if loop:
        if loop.get("complete") is not True or loop.get("methodology_ok") is not True:
            errors.append("positive.loop requires complete and methodology_ok")
        done, total = loop.get("done"), loop.get("total")
        if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
            errors.append("positive.loop.total must be a positive integer")
        if not isinstance(done, int) or isinstance(done, bool) or done != total:
            errors.append("positive.loop.done must equal total")

    negative = obj(document.get("negative_oracle"))
    req_sha(negative, "spec_sha256", errors, "negative_oracle")
    if negative.get("spec_sha256") != spec.get("sha256"):
        errors.append("negative_oracle.spec_sha256 must match spec.sha256")
    if negative.get("technique") not in NEGATIVE_TECHNIQUES:
        errors.append("negative_oracle.technique is not an active supported injection")
    req_text(negative, "injection", errors, "negative_oracle")
    if negative.get("observed_verdict") not in {"absent", "red", "failed", "rejected"}:
        errors.append("negative_oracle.observed_verdict must be absent, red, failed, or rejected; inconclusive is unverified")
    req_text(negative, "receipt_path", errors, "negative_oracle")
    req_sha(negative, "receipt_sha256", errors, "negative_oracle")
    if negative.get("restored") is not True:
        errors.append("negative_oracle.restored must be true")

    oracle = obj(document.get("oracle"))
    for key in ("emit_identity", "read_identity"):
        req_text(oracle, key, errors, "oracle")
    identities_differ = oracle.get("emit_identity") != oracle.get("read_identity")
    if oracle.get("separate_source") is True and not identities_differ:
        errors.append("separate_source requires distinct emit and read identities")
    independently_corroborated = (
        oracle.get("corroborated") is True
        and oracle.get("separate_source") is True
        and identities_differ
    )
    if (tier == "external_verdict") != independently_corroborated:
        errors.append("external_verdict must exactly correspond to independent corroboration")

    binding = obj(document.get("source_binding"))
    for key in ("path", "symbol"):
        req_text(binding, key, errors, "source_binding")
    req_sha(binding, "sha256", errors, "source_binding")
    if binding.get("path") != producer.get("source_path") or binding.get("symbol") != producer.get("source_symbol"):
        errors.append("source_binding must identify the producer source path and symbol")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--template", action="store_true", help="validate the bundled placeholder template only")
    parser.add_argument("--verify-linked", action="store_true", help="hash-verify linked artifacts under --root")
    parser.add_argument("--root", type=Path, help="repository root used for relative linked artifact paths")
    args = parser.parse_args()
    if args.verify_linked and args.root is None:
        parser.error("--verify-linked requires --root")
    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 2
    errors = validate(document, allow_template=args.template)
    if args.verify_linked:
        errors.extend(verify_linked_files(document, args.root.resolve()))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.template:
        print("valid symposium-ooptdd-receipt/v1 template; not completion evidence")
    elif args.verify_linked:
        print("valid symposium-ooptdd-receipt/v1; linked artifact hashes verified")
    else:
        print("structurally valid symposium-ooptdd-receipt/v1; claimed artifacts were not executed or hash-verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
