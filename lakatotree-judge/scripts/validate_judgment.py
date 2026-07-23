#!/usr/bin/env python3
"""Validate a LakatoTree judgment handoff without accepting an authored verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{7,64}$")
FORBIDDEN = {"verdict", "verdict_source", "metric_verdict", "manual_verdict", "human_verdict"}
ACTOR_ID = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")


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


def req_actor(value: dict[str, Any], key: str, errors: list[str], prefix: str) -> None:
    candidate = value.get(key)
    if not isinstance(candidate, str) or ACTOR_ID.fullmatch(candidate) is None:
        errors.append(f"{prefix}.{key} must be a canonical lowercase actor id")


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def scan_forbidden(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN:
                errors.append(f"{path}.{key} is forbidden; read the machine result from its raw artifact")
            errors.extend(scan_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(scan_forbidden(child, f"{path}[{index}]"))
    return errors


def parse_time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not text(value):
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


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
    prereg = obj(document.get("preregistration"))
    for path_key, sha_key in (
        ("request_path", "request_sha256"),
        ("response_path", "response_sha256"),
        ("judge_script_path", "judge_script_sha256"),
    ):
        errors.extend(verify_file(prereg.get(path_key), prereg.get(sha_key), root, f"preregistration.{path_key}"))
    measurement = obj(document.get("measurement"))
    for index, raw in enumerate(items(measurement.get("evidence_records"))):
        record = obj(raw)
        errors.extend(verify_file(record.get("path"), record.get("sha256"), root, f"measurement.evidence_records[{index}].path"))
    errors.extend(verify_file(measurement.get("novel_result_path"), measurement.get("novel_result_sha256"), root, "measurement.novel_result_path"))
    judge = obj(document.get("judge"))
    errors.extend(verify_file(judge.get("response_path"), judge.get("response_sha256"), root, "judge.response_path"))
    verification = obj(document.get("verification"))
    errors.extend(verify_file(verification.get("receipt_chain_path"), verification.get("receipt_chain_sha256"), root, "verification.receipt_chain_path"))
    errors.extend(verify_file(verification.get("verify_output_path"), verification.get("verify_output_sha256"), root, "verification.verify_output_path"))
    return errors


def validate(document: Any, stage: str, allow_template: bool = False) -> list[str]:
    if not isinstance(document, dict):
        return ["document must be a JSON object"]
    errors = scan_forbidden(document)
    if allow_template:
        if document.get("template_only") is not True:
            errors.append("--template requires template_only=true")
    elif document.get("template_only") is not False:
        errors.append("completion judgment must explicitly set template_only=false")
    if document.get("schema_version") != "symposium-lakatotree-judgment/v1":
        errors.append("schema_version must be 'symposium-lakatotree-judgment/v1'")
    for key in ("programme", "branch", "conjecture"):
        req_text(document, key, errors, "root")

    roles = obj(document.get("roles"))
    req_actor(roles, "implementer", errors, "roles")
    req_actor(roles, "judge", errors, "roles")
    if roles.get("implementer") == roles.get("judge"):
        errors.append("roles.implementer and roles.judge must differ")

    prereg = obj(document.get("preregistration"))
    for key in ("request_path", "response_path", "kill_condition", "judge_script_path"):
        req_text(prereg, key, errors, "preregistration")
    for key in ("request_sha256", "response_sha256", "prediction_receipt_sha256", "judge_script_sha256"):
        req_sha(prereg, key, errors, "preregistration")
    if prereg.get("registered_before_measurement") is not True:
        errors.append("preregistration.registered_before_measurement must be true")
    prediction = obj(prereg.get("prediction"))
    req_text(prediction, "metric", errors, "preregistration.prediction")
    if prediction.get("direction") not in {"lower", "higher"}:
        errors.append("preregistration.prediction.direction must be lower or higher")
    for key in ("baseline", "noise_band"):
        value = prediction.get(key)
        if not finite_number(value):
            errors.append(f"preregistration.prediction.{key} must be finite")
    if finite_number(prediction.get("noise_band")) and prediction["noise_band"] < 0:
        errors.append("preregistration.prediction.noise_band must be nonnegative")
    if prediction.get("scale_type") not in {"ratio", "interval", "ordinal"}:
        errors.append("preregistration.prediction.scale_type must be ratio, interval, or ordinal")
    if prediction.get("scale_type") == "ordinal" and prediction.get("noise_band") != 0:
        errors.append("ordinal prediction requires noise_band == 0")
    novel_target = obj(prereg.get("novel_target"))
    if novel_target:
        req_text(novel_target, "metric", errors, "preregistration.novel_target")
        if novel_target.get("direction") not in {"lower", "higher"}:
            errors.append("preregistration.novel_target.direction must be lower or higher")
        if not finite_number(novel_target.get("threshold")):
            errors.append("preregistration.novel_target.threshold must be finite")
    registered_at = parse_time(prereg.get("registered_at"), "preregistration.registered_at", errors)

    if stage == "complete":
        measurement = obj(document.get("measurement"))
        started_at = parse_time(measurement.get("started_at"), "measurement.started_at", errors)
        if registered_at and started_at and not registered_at < started_at:
            errors.append("preregistration must precede measurement")
        evidence = items(measurement.get("evidence_records"))
        if not evidence:
            errors.append("measurement.evidence_records must not be empty")
        for index, raw in enumerate(evidence):
            record = obj(raw)
            req_text(record, "path", errors, f"measurement.evidence_records[{index}]")
            req_sha(record, "sha256", errors, f"measurement.evidence_records[{index}]")
            if record.get("schema") != "lakato-evidence-record/v1":
                errors.append(f"measurement.evidence_records[{index}].schema must be lakato-evidence-record/v1")
            if record.get("grounded") is not True:
                errors.append(f"measurement.evidence_records[{index}].grounded must be true")
            if record.get("contains_verdict") is not False:
                errors.append(f"measurement.evidence_records[{index}].contains_verdict must be false")
        if novel_target or "novel_result_path" in measurement or "novel_result_sha256" in measurement:
            req_text(measurement, "novel_result_path", errors, "measurement")
            req_sha(measurement, "novel_result_sha256", errors, "measurement")

        judge = obj(document.get("judge"))
        for key in ("command", "cwd", "entrypoint", "response_path"):
            req_text(judge, key, errors, "judge")
        git_head = judge.get("git_head")
        if not isinstance(git_head, str) or GIT_SHA.fullmatch(git_head) is None:
            errors.append("judge.git_head must be a lowercase 7-64 hex commit id")
        if judge.get("exit_code") != 0:
            errors.append("judge.exit_code must be 0")
        for key in ("response_sha256", "verdict_receipt_sha256", "prev_receipt_sha256"):
            req_sha(judge, key, errors, "judge")
        if judge.get("prev_receipt_sha256") != prereg.get("prediction_receipt_sha256"):
            errors.append("judge.prev_receipt_sha256 must bind the preregistration prediction receipt")

        verification = obj(document.get("verification"))
        for key in ("receipt_chain_path", "verify_output_path"):
            req_text(verification, key, errors, "verification")
        for key in ("receipt_chain_sha256", "verify_output_sha256", "head_receipt_sha256"):
            req_sha(verification, key, errors, "verification")
        if verification.get("head_receipt_sha256") != judge.get("verdict_receipt_sha256"):
            errors.append("verification.head_receipt_sha256 must bind the judge verdict receipt")
        if verification.get("ok") is not True:
            errors.append("verification.ok must be true")
        if verification.get("from_receipt") is not True:
            errors.append("verification.from_receipt must be true")
        if verification.get("scripted_source_confirmed") is not True:
            errors.append("verification.scripted_source_confirmed must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--stage", choices=("plan", "complete"), default="complete")
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
    errors = validate(document, args.stage, allow_template=args.template)
    if args.verify_linked:
        errors.extend(verify_linked_files(document, args.root.resolve()))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.template:
        print(f"valid symposium-lakatotree-judgment/v1 template ({args.stage}); not a judge result")
    elif args.verify_linked:
        print(f"valid symposium-lakatotree-judgment/v1 ({args.stage}); linked artifact hashes verified")
    else:
        print(f"structurally valid symposium-lakatotree-judgment/v1 ({args.stage}); raw receipts were not executed or hash-verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
